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
from pathlib import Path

from qgis_plugin_dev_tools.build.rewrite_imports import rewrite_imports_in_source_file, insert_as_first_import
from qgis_plugin_dev_tools.config import DevToolsConfig
from qgis_plugin_dev_tools.utils.distributions import (
    get_distribution_top_level_package_names,
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
    for dist in dev_tools_config.runtime_distributions:
        dist_info_path = Path(dist._path)  # type: ignore
        dist_top_level_packages = get_distribution_top_level_package_names(dist)

        LOGGER.debug(
            "bundling runtime requirement %s",
            dist.metadata["Name"],
        )

        # don't vendor self, but allow to vendor other packages provided
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

    if dev_tools_config.append_distributions_to_path:
        plugin_init_file = (build_directory_path / plugin_package_name) / "__init__.py"
        insert_as_first_import(plugin_init_file, f"{plugin_package_name}._vendor")
        return

    for package_name in runtime_package_names:
        LOGGER.debug("rewriting imports for %s", package_name)

        for source_file in (build_directory_path / plugin_package_name).rglob("*.py"):
            rewrite_imports_in_source_file(
                source_file,
                rewritten_package_name=package_name,
                container_package_name=f"{plugin_package_name}._vendor",
            )
