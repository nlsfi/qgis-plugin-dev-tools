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

LOGGER = logging.getLogger(__name__)


def get_latest_changelog_sections(changelog_file_path: Path, count: int = 3) -> str:
    LOGGER.debug(
        "finding latest %i section contents from changelog %s",
        count,
        changelog_file_path.resolve(),
    )
    lines = []
    found = 0
    for line in changelog_file_path.read_text(encoding="utf-8").splitlines():
        if found == 0 and not line.startswith("## "):
            continue
        if line.startswith("## "):
            found += 1
        if found > count:
            break
        # since the contents will be inserted into the metadata ini file
        # strip out the leading #'s and replace with dashes instead
        if line.startswith("#"):
            orig_len = len(line)
            line = line.lstrip("#")
            line = "".join(["-"] * (orig_len - len(line))) + line
        lines.append(line)
    return "\n".join(lines).rstrip()


def get_latest_changelog_version_identifier(changelog_file_path: Path) -> str:
    LOGGER.debug(
        "finding latest version tag from changelog %s", changelog_file_path.resolve()
    )
    for line in changelog_file_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            return line.split(" ", maxsplit=2)[1]
    raise ValueError("latest version could not be parsed from changelog")
