# flake8: noqa

import sys
from pathlib import Path

v = sys.argv[1]

# changelog

changelog_file = Path("CHANGELOG.md")
changelog_text_to_prepend = f"## [{v}]"
new_section = "## Unreleased\n\n"

changelog_file.write_text(
    changelog_file.read_text(encoding="utf-8").replace(
        changelog_text_to_prepend, new_section + changelog_text_to_prepend, 1
    ),
    encoding="utf-8",
)

# init

init_file = Path("src/qgis_plugin_dev_tools/__init__.py")
init_line_to_replace = f'__version__ = "{v}"'

init_file.write_text(
    init_file.read_text(encoding="utf-8").replace(
        init_line_to_replace, f'__version__ = "{v}.post0"', 1
    ),
    encoding="utf-8",
)
