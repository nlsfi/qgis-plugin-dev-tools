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
from typing import Dict, List, Optional

from dotenv import dotenv_values

LOGGER = logging.getLogger(__name__)


class DotenvConfig:  # noqa SIM119
    """
    Expected structure for the config keys in the .env.
    """

    QGIS_EXECUTABLE_PATH: Path
    DEBUGGER_LIBRARY: Optional[str]
    DEVELOPMENT_PROFILE_NAME: Optional[str]
    runtime_environment: Dict[str, str]

    def __init__(
        self,
        *,
        QGIS_EXECUTABLE_PATH: str,  # noqa N803
        DEBUGGER_LIBRARY: Optional[str] = None,  # noqa N803
        DEVELOPMENT_PROFILE_NAME: Optional[str] = None,  # noqa N803
        **other_vars: str,
    ) -> None:
        self.QGIS_EXECUTABLE_PATH = Path(QGIS_EXECUTABLE_PATH)
        if not self.QGIS_EXECUTABLE_PATH.exists():
            raise ValueError(
                f"QGIS executable {self.QGIS_EXECUTABLE_PATH.resolve()} does not exist."
            )
        self.DEBUGGER_LIBRARY = DEBUGGER_LIBRARY
        self.DEVELOPMENT_PROFILE_NAME = DEVELOPMENT_PROFILE_NAME
        self.runtime_environment = other_vars


def read_dotenv_configs(dotenv_file_paths: List[Path]) -> DotenvConfig:
    config = {}
    for dotenv_file_path in dotenv_file_paths:
        LOGGER.debug("reading config from %s", dotenv_file_path.resolve())
        config.update(dotenv_values(dotenv_file_path, verbose=False, encoding="utf-8"))
    try:
        return DotenvConfig(**{k: v for k, v in config.items() if v})
    except (KeyError, TypeError) as e:
        raise ValueError(f"dev tools config invalid in .env: {e}")
