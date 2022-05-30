#  Copyright (C) 2022 National Land Survey of Finland
#  (https://www.maanmittauslaitos.fi/en).
#
#
#  This file is part of qgis-plugin-dev-tools.
#
#  qgis-plugin-dev-tools is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  qgis-plugin-dev-tools is distributed in the hope that it will be
#  useful, but WITHOUT ANY WARRANTY; without even the implied warranty
#  of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with qgis-plugin-dev-tools. If not, see <https://www.gnu.org/licenses/>.

import ast
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from qgis_plugin_dev_tools.config import DevToolsConfig
from qgis_plugin_dev_tools.utils.distributions import (
    get_distribution_top_level_package_names,
)

IGNORED_FILES = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyi")
LOGGER = logging.getLogger(__name__)


def copy_plugin_code(
    dev_tools_config: DevToolsConfig, build_directory_path: Path
) -> None:
    LOGGER.debug(
        "copying %s to build directory",
        dev_tools_config.plugin_package_path.resolve(),
    )
    shutil.copytree(
        src=dev_tools_config.plugin_package_path,
        dst=build_directory_path / dev_tools_config.plugin_package_name,
        ignore=IGNORED_FILES,
    )


@dataclass
class SpecialImportRewriter(ast.NodeTransformer):
    """
    Transformer class to rewrite simple "import module.x.y" style imports
    to vendored format, for example "import something._vendor.module.x.y".
    """

    from_module: str
    to_module: str

    _replaced_imported_names: Dict[str, str] = field(default_factory=dict, init=False)

    # collect the found imported names to replace the references also
    def visit_Import(self, node: ast.Import) -> Any:  # noqa N802
        for alias in node.names:
            if alias.name.startswith(f"{self.from_module}.") and alias.asname is None:
                old_module_name = alias.name
                new_identifier_name = "vendored_" + alias.name.replace(".", "_")
                self._replaced_imported_names[old_module_name] = new_identifier_name
                child_module_names = old_module_name.replace(
                    f"{self.from_module}.", "", 1
                )
                alias.name = f"{self.to_module}.{child_module_names}"
                alias.asname = new_identifier_name
        return node

    # check the attributes for an imported module name reference
    def visit_Attribute(self, node: ast.Attribute) -> Any:  # noqa N802
        if (attribute_name := ast.unparse(node)) in self._replaced_imported_names:
            replaced_name = self._replaced_imported_names[attribute_name]
            return ast.Name(id=replaced_name, ctx=ast.Load())

        return self.generic_visit(node)

    # this will only handle sys.modules['something'] replace
    def visit_Subscript(self, node: ast.Subscript) -> Any:  # noqa N802
        if (
            ast.unparse(node.value) == "sys.modules"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
            and node.slice.value.startswith(f"{self.from_module}.")
        ):
            child_module_names = node.slice.value.replace(f"{self.from_module}.", "", 1)
            node.slice.value = f"{self.to_module}.{child_module_names}"
            return node

        return self.generic_visit(node)


def copy_runtime_requirements(
    dev_tools_config: DevToolsConfig,
    build_directory_path: Path,
) -> None:
    plugin_package_name = dev_tools_config.plugin_package_name

    if len(dev_tools_config.runtime_distributions) > 0:
        vendor_path = build_directory_path / plugin_package_name / "_vendor"
        vendor_path.mkdir(parents=True)
        (vendor_path / "__init__.py").touch()

    runtime_package_names = []
    # copy dist infos (licenses etc) and all provided top level packages
    for dist in dev_tools_config.runtime_distributions:
        dist_info_path = Path(dist._path)  # type: ignore
        dist_top_level_packages = get_distribution_top_level_package_names(dist)

        LOGGER.debug(
            "bundling runtime requirement %s",
            dist.metadata["Name"],
        )

        # dont vendor self, but allow to vendor other packages provided
        # from plugin distribution. if "-e ." installs "my-plugin-name" distribution
        # containing my_plugin & my_util_package top level packages, bundling is only
        # needed for my_util_package
        dist_top_level_packages = [
            name for name in dist_top_level_packages if name != plugin_package_name
        ]

        runtime_package_names.extend(dist_top_level_packages)

        LOGGER.debug(
            "copying %s to build directory",
            dist_info_path.resolve(),
        )
        shutil.copytree(
            src=dist_info_path,
            dst=build_directory_path
            / plugin_package_name
            / "_vendor"
            / dist_info_path.name,
            ignore=IGNORED_FILES,
        )
        for package_name in dist_top_level_packages:
            LOGGER.debug(
                "bundling runtime requirement %s package %s",
                dist.metadata["Name"],
                package_name,
            )
            LOGGER.debug(
                "copying %s to build directory",
                (dist_info_path.parent / package_name).resolve(),
            )
            shutil.copytree(
                src=dist_info_path.parent / package_name,
                dst=build_directory_path
                / plugin_package_name
                / "_vendor"
                / package_name,
                ignore=IGNORED_FILES,
            )

    for package_name in runtime_package_names:
        LOGGER.debug("rewriting imports for %s", package_name)

        for source_file in (build_directory_path / plugin_package_name).rglob("*.py"):
            contents = source_file.read_text(encoding="utf-8")

            # special case where a submodule of the vendored package is imported
            # or the name is defined in a sys.modules key as a constant
            specials = [
                f"import {package_name}.",
                f"sys.modules['{package_name}.",
                f'sys.modules["{package_name}.',
            ]
            if any(special in contents for special in specials):

                # hold on to the original for license comments
                # since comments are lost with ast parse+unparse
                orig_file = source_file.with_name(source_file.name + "_original")
                orig_file.write_text(contents, encoding="utf-8")
                original_note = (
                    "# parsed with ast, see original at "
                    f'"{orig_file.relative_to(build_directory_path).as_posix()}"\n\n'
                )

                tree = ast.parse(contents)
                new_tree = ast.fix_missing_locations(
                    SpecialImportRewriter(
                        from_module=package_name,
                        to_module=f"{plugin_package_name}._vendor.{package_name}",
                    ).visit(tree)
                )
                contents = original_note + ast.unparse(new_tree)

            # trivial cases with valid identifiers
            contents = contents.replace(
                f"from {package_name} import",
                f"from {plugin_package_name}._vendor.{package_name} import",
            )
            contents = contents.replace(
                f"from {package_name}.",
                f"from {plugin_package_name}._vendor.{package_name}.",
            )
            contents = contents.replace(
                f"import {package_name}",
                (
                    f"import {plugin_package_name}._vendor.{package_name}"
                    f" as {package_name}"
                ),
            )

            source_file.write_text(contents, encoding="utf-8")
