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
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import tomli

LOGGER = logging.getLogger(__name__)


@dataclass
class PyprojectConfig:
    """
    Expected structure for the config keys under the tool section.
    """

    DEV_TOOLS_SECTION_LOCATOR = "qgis_plugin_dev_tools"

    plugin_package_name: str
    runtime_requires: List[str] = field(default_factory=list)
    use_dangerous_vendor_sys_path_append: bool = False
    auto_add_recursive_runtime_dependencies: bool = False


def read_pyproject_config(pyproject_file_path: Path) -> PyprojectConfig:
    LOGGER.debug("reading config from %s", pyproject_file_path.resolve())
    with open(pyproject_file_path, "rb") as pyproject_file:
        config = tomli.load(pyproject_file)
        try:
            dev_tools_configuration = config.get("tool", {})[
                PyprojectConfig.DEV_TOOLS_SECTION_LOCATOR
            ]
            return PyprojectConfig(**dev_tools_configuration)
        except (KeyError, TypeError) as e:
            raise ValueError(f"dev tools config invalid in pyproject.toml: {e}")
