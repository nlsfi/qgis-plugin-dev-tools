from pathlib import Path

from qgis_plugin_dev_tools.build.rewrite_imports import rewrite_imports_in_source_file


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
        file.read_text().splitlines()
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
        file.read_text().splitlines()
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
        file.read_text().splitlines()
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
