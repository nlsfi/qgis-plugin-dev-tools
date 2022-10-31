# flake8: noqa

import sys
from datetime import date
from pathlib import Path

v = sys.argv[1]
d = date.today().isoformat()

# changelog

changelog_file = Path("CHANGELOG.md")

for line in changelog_file.read_text(encoding="utf-8").splitlines():
    if line.startswith("##"):
        if line != "## Unreleased":
            raise ValueError("changelog not in correct format")
        break
else:
    raise ValueError("changelog not in correct format")

link_line = f"[{v}]: https://github.com/nlsfi/qgis-plugin-dev-tools/releases/tag/v{v}\n"

changelog_file.write_text(
    changelog_file.read_text(encoding="utf-8").replace(
        "## Unreleased", f"## [{v}] - {d}", 1
    )
    + link_line,
    encoding="utf-8",
)

# init

init_file = Path("src/qgis_plugin_dev_tools/__init__.py")

init_line_to_replace = None

for line in init_file.read_text(encoding="utf-8").splitlines():
    if line.startswith("__version__ ="):
        init_line_to_replace = line
        break
else:
    raise ValueError("init file not in correct format")

init_file.write_text(
    init_file.read_text(encoding="utf-8").replace(
        init_line_to_replace, f'__version__ = "{v}"', 1
    ),
    encoding="utf-8",
)
