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
