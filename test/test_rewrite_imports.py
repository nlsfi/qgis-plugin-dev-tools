from pathlib import Path
from xml.etree import ElementTree

from qgis_plugin_dev_tools.build.rewrite_imports import rewrite_imports_in_source_file


def _trim_first_line_comment(lines: list[str]) -> list[str]:
    if lines[0].startswith("#"):
        return lines[1:]
    return lines


def test_from_x_import_matching_name_not_rewritten(tmp_path: Path):
    file = tmp_path / "mock.py"

    file.write_text(
        """
    from something import xyz as xyz_alias
    from something import xyz
    """
    )

    rewrite_imports_in_source_file(file, "xyz", "container.package")

    assert (
        _trim_first_line_comment(file.read_text().splitlines())
        == """
    from something import xyz as xyz_alias
    from something import xyz
    """.splitlines()
    )


def test_plain_import_matching_name_rewritten(tmp_path: Path):
    file = tmp_path / "mock.py"

    file.write_text(
        """
    import xyz as alias
    import xyz
    a = 123; import xyz as alias
    a = 123;    import xyz
    a = 123;\timport xyz
    a = 123; import xyz; b = 456
    \timport xyz
    """
    )

    rewrite_imports_in_source_file(file, "xyz", "container.package")

    assert (
        _trim_first_line_comment(file.read_text().splitlines())
        == """
    import container.package.xyz as alias
    import container.package.xyz as xyz
    a = 123; import container.package.xyz as alias
    a = 123;    import container.package.xyz as xyz
    a = 123;\timport container.package.xyz as xyz
    a = 123; import container.package.xyz as xyz; b = 456
    \timport container.package.xyz as xyz
    """.splitlines()
    )


def test_plain_import_with_mathing_prefix_not_replaced(tmp_path: Path):
    file = tmp_path / "mock.py"

    file.write_text(
        """
    import xyz_a as alias
    import xyz_b
    a = 123; import xyz_c as alias
    a = 123;    import xyz_d
    a = 123;\timport xyz_e
    a = 123; import xyz_f; b = 456
    \timport xyz_g
    """
    )

    rewrite_imports_in_source_file(file, "xyz", "container.package")

    assert (
        _trim_first_line_comment(file.read_text().splitlines())
        == """
    import xyz_a as alias
    import xyz_b
    a = 123; import xyz_c as alias
    a = 123;    import xyz_d
    a = 123;\timport xyz_e
    a = 123; import xyz_f; b = 456
    \timport xyz_g
    """.splitlines()
    )


def test_ui_file_custom_widget_imports_are_replaced(tmp_path: Path):
    file = tmp_path / "mock.ui"

    file.write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
    <ui version="4.0">
      <customwidget>
        <class>CustomTreeView</class>
        <extends>QTreeView</extends>
        <header>xyz</header>"
      </customwidget>
      <customwidget>
        <class>CustomTreeView</class>
        <extends>QTreeView</extends>
        <header>xyz.ui.treeview</header>"
      </customwidget>
      <customwidget>
        <class>CustomTreeView</class>
        <extends>QTreeView</extends>
        <header>xyz.something.xyz</header>"
      </customwidget>
      <customwidget>
        <class>CustomTreeView</class>
        <extends>QTreeView</extends>
        <header>xyz_something</header>"
      </customwidget>
    </ui>
    """
    )

    rewrite_imports_in_source_file(file, "xyz", "container.package")

    # validate xml by reading it
    ui_tree = ElementTree.fromstring(file.read_text())
    for index, widget_section in enumerate(ui_tree.iter("customwidget")):
        header_section = widget_section.find("header")
        assert header_section is not None

        if index == 0:
            assert header_section.text == "container.package.xyz"
        elif index == 1:
            assert header_section.text == "container.package.xyz.ui.treeview"
        elif index == 2:
            assert header_section.text == "container.package.xyz.something.xyz"
        else:
            assert header_section.text == "xyz_something"
