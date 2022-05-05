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
from pathlib import Path
from subprocess import Popen
from typing import Optional

LOGGER = logging.getLogger(__name__)


def launch_qgis_with_bootstrap_script(
    qgis_executable_path: Path,
    bootstrap_script_path: Path,
    profile_name: Optional[str],
) -> None:
    args = [
        str(qgis_executable_path),
        "--code",
        str(bootstrap_script_path),
    ]

    if profile_name:
        LOGGER.info("using profile name %s", profile_name)
        args.extend(["--profile", profile_name])
    else:
        LOGGER.info("using default profile name")

    LOGGER.debug("launch command args %s", args)

    process = Popen(
        args=args,
    )

    # TODO: more optimal way to leave the process open, this only silences warnings
    process.returncode = 0
