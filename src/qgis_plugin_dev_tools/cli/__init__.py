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
from typing import Callable, Optional, cast

from qgis_plugin_dev_tools import LOGGER as ROOT_LOGGER
from qgis_plugin_dev_tools.build import make_plugin_zip
from qgis_plugin_dev_tools.config import DevToolsConfig
from qgis_plugin_dev_tools.config.dotenv import read_dotenv_config
from qgis_plugin_dev_tools.start import launch_development_qgis
from qgis_plugin_dev_tools.start.config import DevelopmentModeConfig
from qgis_plugin_dev_tools.utils.distributions import (
    get_distribution_top_level_package_names,
)

LOGGER = logging.getLogger(__name__)


def run() -> None:
    parser = argparse.ArgumentParser(description="QGIS plugin dev tools cli")

    commands = parser.add_subparsers(
        title="commands",
    )

    start_parser = commands.add_parser(
        "start",
        aliases=["s"],
        help="start QGIS with plugin in development mode",
    )
    start_parser.add_argument("--verbose", "-v", action="count", default=0)
    start_parser.set_defaults(callback=start)

    build_parser = commands.add_parser(
        "build",
        aliases=["b"],
        help="build the plugin",
    )
    build_parser.add_argument("--verbose", "-v", action="count", default=0)
    build_parser.set_defaults(callback=build)

    result = parser.parse_args()

    ROOT_LOGGER.setLevel(logging.DEBUG if result.verbose > 0 else logging.INFO)

    callback = cast(Optional[Callable[[], None]], getattr(result, "callback", None))
    if callback is None:
        parser.print_help()
    else:
        callback()


def start() -> None:
    # TODO: allow choosing pyproject file from cli?
    dev_tools_config = DevToolsConfig.from_pyproject_config(Path("pyproject.toml"))
    # TODO: allow choosing .env file from cli?
    # TODO: allow setting debugger flag from cli?
    # TODO: find default executable paths to allow zero-config .env?
    # TODO: rglob('metadata.txt') from cwd to allow zero-config pyproject.toml?
    dotenv_config = read_dotenv_config(Path(".env"))
    LOGGER.info(
        "launching development qgis for plugin %s", dev_tools_config.plugin_package_name
    )
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
        )
    )


def build() -> None:
    # TODO: allow choosing pyproject file from cli?
    dev_tools_config = DevToolsConfig.from_pyproject_config(Path("pyproject.toml"))
    LOGGER.info("building plugin package %s", dev_tools_config.plugin_package_name)
    LOGGER.debug(
        "building plugin package from %s",
        dev_tools_config.plugin_package_path.resolve(),
    )
    # TODO: allow choosing output path from cli?
    make_plugin_zip(dev_tools_config, target_directory_path=Path("dist"))
