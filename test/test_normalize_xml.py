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

from pathlib import Path

import pytest

from hooks.normalize_xml import normalize


@pytest.fixture
def simple_xml() -> str:
    """Create a simple unnormalized XML string."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<qgis version="3.0">
  <fieldConfiguration>
    <field name="test"/>
  </fieldConfiguration>
  <editable>
    <field editable="1" name="test"/>
  </editable>
  <feature>
    <field name="test">value</field>
  </feature>
</qgis>
"""


@pytest.fixture
def xml_with_multiple_tags() -> str:
    """Create XML with multiple removable tags."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<qgis version="3.0">
  <fieldConfiguration>
    <field name="id"/>
    <field name="name"/>
  </fieldConfiguration>
  <editable>
    <field editable="1" name="id"/>
    <field editable="1" name="name"/>
  </editable>
  <labelOnTop>
    <field labelOnTop="1" name="id"/>
  </labelOnTop>
  <feature>
    <field name="id">1</field>
    <field name="name">Test</field>
  </feature>
</qgis>
"""


def test_normalize_keeps_content(tmp_path: Path, simple_xml: str) -> None:
    """Test that normalize does not remove tags."""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(simple_xml)

    normalize(xml_file)

    result = xml_file.read_text()
    assert all(tag in result for tag in ["fieldConfiguration", "editable", "feature"])


def test_normalize_removes_custom_tags(tmp_path: Path, simple_xml: str) -> None:
    """Test that normalize removes custom specified tags."""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(simple_xml)

    normalize(xml_file, remove_tags=["fieldConfiguration"])

    result = xml_file.read_text()
    assert "fieldConfiguration" not in result
    assert "editable" in result  # should keep editable since not specified


def test_normalize_canonicalizes_xml(tmp_path: Path) -> None:
    """Test that normalize canonicalizes the XML format."""
    # XML with extra whitespace and formatting
    unformatted_xml = """<?xml version="1.0" encoding="UTF-8"?>
<qgis   version="3.0"   >
  <feature b="2" c="3" a="1">
    <field name="test">value</field>
  </feature>
</qgis>
"""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(unformatted_xml)

    normalize(xml_file, remove_tags=[])

    result = xml_file.read_text()
    # canonicalize content
    assert '<feature a="1" b="2" c="3">' in result


def test_normalize_preserves_content(tmp_path: Path, simple_xml: str) -> None:
    """Test that normalize preserves important content."""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(simple_xml)

    normalize(xml_file)

    result = xml_file.read_text()
    # The feature content should be preserved
    assert 'name="test"' in result
    assert 'editable="1"' in result


def test_normalize_nonexistent_tag_in_remove_list(
    tmp_path: Path, simple_xml: str
) -> None:
    """Test that specifying non-existent tag doesn't cause errors."""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(simple_xml)

    # Should not raise an error
    normalize(xml_file, remove_tags=["nonExistentTag", "fieldConfiguration"])

    result = xml_file.read_text()
    assert "fieldConfiguration" not in result


def test_normalize_idempotent(tmp_path: Path, simple_xml: str) -> None:
    """Test that normalizing twice produces the same result."""
    xml_file = tmp_path / "test.xml"
    xml_file.write_text(simple_xml)

    normalize(xml_file)
    first_result = xml_file.read_text()

    normalize(xml_file)
    second_result = xml_file.read_text()

    assert first_result == second_result


def test_normalize_qml_file_with_non_xml(tmp_path: Path) -> None:
    """Test that QML files with invalid XML content are skipped gracefully."""
    qml_file = tmp_path / "test.qml"
    # Write invalid XML content that would fail parsing
    qml_file.write_text("import QtQuick 2.0\nRectangle { }")

    # Should not raise an error
    normalize(qml_file)

    # Content should remain unchanged
    assert qml_file.read_text() == "import QtQuick 2.0\nRectangle { }"


def test_normalize_xml_with_invalid_content_raises_error(tmp_path: Path) -> None:
    """Test that non-QML files with invalid XML raise an error."""
    xml_file = tmp_path / "test.xml"
    # Write invalid XML
    xml_file.write_text("<?xml version='1.0'?>\n<unclosed>this is not closed")

    # Should raise XMLSyntaxError for non-QML files
    from lxml import etree

    with pytest.raises(etree.XMLSyntaxError):
        normalize(xml_file)


def test_normalize_qml_with_valid_xml(tmp_path: Path, simple_xml: str) -> None:
    """Test that valid XML in QML files is normalized."""
    qml_file = tmp_path / "test.qml"
    qml_file.write_text(simple_xml)

    # Should not raise an error and should normalize the content
    normalize(qml_file)

    result = qml_file.read_text()
    # Should have canonical format with qgis element
    assert "qgis" in result
    assert "fieldConfiguration" in result
