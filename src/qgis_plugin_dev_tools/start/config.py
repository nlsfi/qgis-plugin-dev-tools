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

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class DevelopmentModeConfig:
    qgis_executable_path: Path
    profile_name: Optional[str]
    runtime_environment: Dict[str, str]
    runtime_library_paths: List[Path]
    plugin_package_path: Path
    plugin_package_name: str
    plugin_dependency_package_names: List[str]
    debugger_library: Optional[str]
    extra_plugin_package_names: List[str]
