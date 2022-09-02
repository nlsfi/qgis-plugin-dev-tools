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

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Optional

from importlib_metadata import entry_points

from qgis_plugin_dev_tools import LOGGER as ROOT_LOGGER
from qgis_plugin_dev_tools.build import make_plugin_zip
from qgis_plugin_dev_tools.config import DevToolsConfig
from qgis_plugin_dev_tools.config.dotenv import read_dotenv_configs
from qgis_plugin_dev_tools.start import launch_development_qgis
from qgis_plugin_dev_tools.start.config import DevelopmentModeConfig
from qgis_plugin_dev_tools.utils.distributions import (
    get_distribution_top_level_package_names,
)

LOGGER = logging.getLogger(__name__)


def start(dotenv_file_paths: List[Path]) -> None:
    # TODO: allow choosing pyproject file from cli?
    dev_tools_config = DevToolsConfig.from_pyproject_config(Path("pyproject.toml"))
    # TODO: allow setting debugger flag from cli?
    # TODO: find default executable paths to allow zero-config .env?
    # TODO: rglob('metadata.txt') from cwd to allow zero-config pyproject.toml?
    dotenv_config = read_dotenv_configs(dotenv_file_paths)
    LOGGER.info(
        "launching development qgis for plugin %s", dev_tools_config.plugin_package_name
    )

    entry_points_found_from_python_env = entry_points(group="qgis_plugin_dev_tools")

    launch_development_qgis(
        DevelopmentModeConfig(
            qgis_executable_path=dotenv_config.QGIS_EXECUTABLE_PATH,
            profile_name=dotenv_config.DEVELOPMENT_PROFILE_NAME,
            runtime_environment=dotenv_config.runtime_environment,
            runtime_library_paths=[Path(p) for p in sys.path],
            plugin_package_path=dev_tools_config.plugin_package_path,
            plugin_package_name=dev_tools_config.plugin_package_name,
            plugin_dependency_package_names=[
                name
                for dist in dev_tools_config.runtime_distributions
                for name in get_distribution_top_level_package_names(dist)
            ],
            debugger_library=dotenv_config.DEBUGGER_LIBRARY,
            extra_plugin_package_names=[
                entry_point.name
                for entry_point in entry_points_found_from_python_env
                if entry_point.name != dev_tools_config.plugin_package_name
            ],
        )
    )


def build(plugin_version: Optional[str]) -> None:
    # TODO: allow choosing pyproject file from cli?
    dev_tools_config = DevToolsConfig.from_pyproject_config(Path("pyproject.toml"))
    LOGGER.info("building plugin package %s", dev_tools_config.plugin_package_name)
    LOGGER.debug(
        "building plugin package from %s",
        dev_tools_config.plugin_package_path.resolve(),
    )
    # TODO: allow choosing output path from cli?
    make_plugin_zip(
        dev_tools_config,
        target_directory_path=Path("dist"),
        plugin_version=plugin_version,
    )


parser = argparse.ArgumentParser(description="QGIS plugin dev tools cli")

common_parser = argparse.ArgumentParser(add_help=False)
common_parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="use debug logging level",
)

commands = parser.add_subparsers(required=True, dest="subcommand")

start_parser = commands.add_parser(
    "start",
    aliases=["s"],
    help="start QGIS with plugin in development mode",
    parents=[common_parser],
)
start_parser.add_argument(
    "-e",
    "--env-file",
    action="append",
    metavar="<file>",
    dest="extra_dotenv_files",
    default=[],
    help="read config from a .env file (can be specified multiple times)",
)

build_parser = commands.add_parser(
    "build",
    aliases=["b"],
    help="build the plugin",
    parents=[common_parser],
)
build_parser.add_argument(
    "--version",
    metavar="<version>",
    dest="plugin_version",
    type=str,
    default="",
    help="version of the plugin (leave empty to get the version from the CHANGELOG.md)",
)


def run() -> None:
    result = vars(parser.parse_args())

    ROOT_LOGGER.setLevel(logging.DEBUG if result.get("verbose") else logging.INFO)

    LOGGER.debug(f"parsed cli args {result}")

    if result.get("subcommand") in ["start", "s"]:
        dotenv_file_paths = [Path(".env")] + [
            Path(f) for f in result.get("extra_dotenv_files", [])
        ]
        start(dotenv_file_paths)

    elif result.get("subcommand") in ["build", "b"]:
        plugin_version = str(result.get("plugin_version"))
        build(plugin_version)

    else:
        parser.print_usage()
