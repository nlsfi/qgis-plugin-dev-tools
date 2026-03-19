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

import argparse
import logging
import sys
from io import StringIO
from pathlib import Path

from lxml import etree

LOGGER = logging.getLogger(__name__)


def normalize(path: Path, remove_tags: list[str] | None = None) -> None:
    """Normalize XML file by canonicalizing and optionally removing tags."""
    try:
        with path.open(encoding="utf-8") as f:
            xml = f.read()
            f.seek(0)
            tree = etree.parse(f)
    except etree.XMLSyntaxError as e:
        if path.suffix.lower() == ".qml":
            # QML files may contain non-XML content so ignore parsing errors
            LOGGER.info(f"Non-XML content found in {path}, skipping normalization.")
            return
        else:
            raise e

    normalized_xml = etree.canonicalize(tree, with_comments=True)

    normalized_tree = etree.parse(StringIO(normalized_xml))

    # Remove specified tags.
    if remove_tags:
        xpath_expr = " | ".join(f"//{tag}" for tag in remove_tags)
        for element in normalized_tree.xpath(xpath_expr):
            element.getparent().remove(element)

    # canonicalize drops doctype info so add it from the original xml
    normalized_str = etree.tostring(
        normalized_tree, doctype=tree.docinfo.doctype, encoding="unicode"
    )
    if xml != normalized_str:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"{normalized_str}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Normalize and clean up XML files by canonicalizing "
        "and removing specified tags."
    )
    parser.add_argument(
        "--remove-tag",
        action="append",
        metavar="TAG",
        help="Tag names to remove from the XML",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="XML files to normalize",
    )
    args = parser.parse_args()
    if not args.files:
        sys.exit(0)

    remove_tags = args.remove_tag if args.remove_tag else None

    for file in args.files:
        normalize(Path(file), remove_tags=remove_tags)
