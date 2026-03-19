#  Copyright (C) 2026 National Land Survey of Finland
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

# flake8: noqa

import sys
from pathlib import Path

v = sys.argv[1]

# changelog

changelog_file = Path("CHANGELOG.md")
to_find = f"## [{v}]"

found = False
results = []

for line in changelog_file.read_text(encoding="utf-8").splitlines():
    if found and line.startswith("## "):
        break
    elif found:
        results.append(line)
    elif line.startswith(to_find):
        found = True

if len(results) == 0:
    raise ValueError("no changes found")

if results[0] == "":
    results = results[1:]
if results[-1] == "":
    results = results[:-1]

sys.stdout.write("\n".join(results) + "\n")
