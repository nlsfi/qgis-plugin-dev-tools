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

from configparser import ConfigParser
from pathlib import Path


def update_metadata_file(
    metadata_file_path: Path, version: str, changelog_contents: str
) -> None:
    parser = ConfigParser()
    parser.read(metadata_file_path, encoding="utf-8")
    parser.set("general", "version", version)
    parser.set("general", "changelog", changelog_contents)
    with open(metadata_file_path, "w", encoding="utf-8") as metadata_file:
        parser.write(metadata_file)
