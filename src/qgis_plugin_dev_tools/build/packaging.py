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

import logging
import shutil
import sys
from importlib_metadata import Distribution
from pathlib import Path

from qgis_plugin_dev_tools.build.rewrite_imports import (
    rewrite_imports_in_source_file,
    insert_as_first_import,
)
from qgis_plugin_dev_tools.config import DevToolsConfig
from qgis_plugin_dev_tools.utils.distributions import (
    get_distribution_top_level_package_names,
    get_distribution_top_level_script_names,
)

IGNORED_FILES = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyi")
LOGGER = logging.getLogger(__name__)

VENDOR_PATH_APPEND_SCRIPT = """
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.resolve().as_posix())
"""


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


def copy_runtime_requirements(
    dev_tools_config: DevToolsConfig,
    build_directory_path: Path,
) -> None:
    plugin_package_name = dev_tools_config.plugin_package_name

    if len(dev_tools_config.runtime_distributions) > 0:
        vendor_path = build_directory_path / plugin_package_name / "_vendor"
        vendor_path.mkdir(parents=True)
        vendor_init_file = vendor_path / "__init__.py"
        vendor_init_file.touch()
        if dev_tools_config.append_distributions_to_path:
            vendor_init_file.write_text(VENDOR_PATH_APPEND_SCRIPT)

    runtime_package_names = []
    # copy dist infos (licenses etc.) and all provided top level packages
    for dist in (
        dev_tools_config.runtime_distributions
        + dev_tools_config.extra_runtime_distributions
    ):
        dist_info_path = Path(dist._path)  # type: ignore
        if (
            Path(sys.base_prefix) in dist_info_path.parent.parents
            and dist in dev_tools_config.extra_runtime_distributions
        ):
            # If build enviroment system packages include a dependency
            # resolved via recursive flag, assume it does not have
            # to be bundled (possibly dangerous, if build is made on
            # a different system package set than runtime)
            LOGGER.warning(
                "skipping recursively found runtime requirement %s "
                "because it is included in system packages",
                dist.metadata["Name"],
            )
            continue

        LOGGER.debug(
            "bundling runtime requirement %s",
            dist.metadata["Name"],
        )

        dist_top_level_packages = get_distribution_top_level_package_names(dist)
        dist_top_level_scripts = get_distribution_top_level_script_names(dist)

        # don't vendor self, but allow to vendor other packages provided
        # from plugin distribution. if "-e ." installs "my-plugin-name" distribution
        # containing my_plugin & my_util_package top level packages, bundling is only
        # needed for my_util_package
        dist_top_level_packages = [
            name for name in dist_top_level_packages if name != plugin_package_name
        ]

        LOGGER.debug(
            "bundling %s top level packages and %s top level scripts",
            dist_top_level_packages,
            dist_top_level_scripts,
        )

        runtime_package_names.extend(dist_top_level_packages)
        runtime_package_names.extend(dist_top_level_scripts)

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

        for package_name in dist_top_level_packages + dist_top_level_scripts:
            _copy_package(
                build_directory_path,
                dist,
                dist_info_path,
                package_name,
                plugin_package_name,
            )

    if dev_tools_config.append_distributions_to_path:
        plugin_init_file = (build_directory_path / plugin_package_name) / "__init__.py"
        insert_as_first_import(plugin_init_file, f"{plugin_package_name}._vendor")
        return

    for package_name in runtime_package_names:
        LOGGER.debug("rewriting imports for %s", package_name)

        py_files = list((build_directory_path / plugin_package_name).rglob("*.py"))
        ui_files = list((build_directory_path / plugin_package_name).rglob("*.ui"))

        for source_file in py_files + ui_files:
            rewrite_imports_in_source_file(
                source_file,
                rewritten_package_name=package_name,
                container_package_name=f"{plugin_package_name}._vendor",
            )


def _copy_package(
    build_directory_path: Path,
    dist: Distribution,
    dist_info_path: Path,
    original_top_level_name: str,
    plugin_package_name: str,
) -> None:
    LOGGER.debug(
        "bundling runtime requirement %s package %s",
        dist.metadata["Name"],
        original_top_level_name,
    )

    # top-level package
    dist_package_src = dist_info_path.parent / original_top_level_name
    if dist_package_src.exists():
        LOGGER.debug(
            "copying %s to build directory",
            dist_package_src.resolve(),
        )
        shutil.copytree(
            src=dist_package_src,
            dst=(
                build_directory_path
                / plugin_package_name
                / "_vendor"
                / original_top_level_name
            ),
            ignore=IGNORED_FILES,
        )
        return

    # top level script
    dist_script_src = dist_info_path.parent / f"{original_top_level_name}.py"
    if dist_script_src.exists():
        LOGGER.debug(
            "copying %s to build directory",
            dist_script_src.resolve(),
        )
        shutil.copy(
            src=dist_script_src,
            dst=build_directory_path / plugin_package_name / "_vendor",
        )
        return

    # pyd file
    pyd_files = list(dist_info_path.parent.glob(f"{original_top_level_name}*.pyd"))
    if pyd_files:
        for dist_binary_src in pyd_files:
            shutil.copy(
                src=dist_binary_src,
                dst=build_directory_path / plugin_package_name / "_vendor",
            )
        return

    if not original_top_level_name.startswith("_"):
        raise ValueError(
            f"Sources for {original_top_level_name} "
            f"from runtime requirement {dist.metadata['Name']} "
            f"cannot be found in {dist_info_path.parent}"
        )

    LOGGER.warning("Could not find %s to bundle", original_top_level_name)
