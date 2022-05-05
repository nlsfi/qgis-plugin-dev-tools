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

from qgis_plugin_dev_tools.start.bootstrap import create_bootstrap_file
from qgis_plugin_dev_tools.start.config import DevelopmentModeConfig
from qgis_plugin_dev_tools.start.daemon_server import start_daemon_server
from qgis_plugin_dev_tools.start.launch import launch_qgis_with_bootstrap_script

LOGGER = logging.getLogger(__name__)


def launch_development_qgis(
    development_mode_config: DevelopmentModeConfig,
) -> None:
    LOGGER.info("starting daemon server")
    with start_daemon_server() as (port, handle_single_request):

        LOGGER.info("creating a bootstrap file")
        with create_bootstrap_file(
            development_mode_config,
            port,
        ) as bootstrap_file_path:

            LOGGER.info("launching qgis")
            launch_qgis_with_bootstrap_script(
                development_mode_config.qgis_executable_path,
                bootstrap_file_path,
                development_mode_config.profile_name,
            )

            LOGGER.info("waiting for qgis to connect")
            is_timeout = handle_single_request()

    if is_timeout:
        LOGGER.error("qgis did not connect within timeout period")
    else:
        LOGGER.info("qgis connected")
        LOGGER.info("closed daemon server")
