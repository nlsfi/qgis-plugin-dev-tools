import os
import sys
import textwrap
import zipfile
from pathlib import Path

import pytest
from qgis_plugin_dev_tools.build import make_plugin_zip
from qgis_plugin_dev_tools.config import DevToolsConfig, VersionNumberSource


@pytest.fixture()
def plugin_dir(tmp_path: Path) -> Path:
    plugin_dir = tmp_path / "Plugin"
    plugin_dir.mkdir()

    changelog_file = plugin_dir / "CHANGELOG.md"
    changelog_file.write_text(
        textwrap.dedent(
            """\
    # CHANGELOG

    ## 0.1.0 - First release

    - new feature
    """
        )
    )

    metadata_file = plugin_dir / "metadata.txt"
    metadata_file.write_text(
        textwrap.dedent(
            """\
    [general]
    name=Plugin
    description=
    about=
    version=0.0.1
    author=
    email=
    changelog=
    tags=
    category=Plugins
    experimental=True
    deprecated=False"""
        )
    )

    main_file = plugin_dir / "__init__.py"
    main_file.touch()

    os.chdir(tmp_path.resolve())
    sys.path.append(tmp_path.resolve().as_posix())

    return plugin_dir


@pytest.fixture()
def dev_tools_config(plugin_dir: Path) -> DevToolsConfig:
    from qgis_plugin_dev_tools.config import DevToolsConfig

    return DevToolsConfig(
        plugin_package_name="Plugin",
        runtime_requires=["pytest"],
        changelog_file_path=plugin_dir / "CHANGELOG.md",
        append_distributions_to_path=True,
        auto_add_recursive_runtime_dependencies=True,
        version_number_source=VersionNumberSource.CHANGELOG,
        disabled_extra_plugins=[],
    )


@pytest.fixture()
def dev_tools_config_with_duplicate_dependencies(plugin_dir: Path) -> DevToolsConfig:
    from qgis_plugin_dev_tools.config import DevToolsConfig

    return DevToolsConfig(
        plugin_package_name="Plugin",
        runtime_requires=["pytest-cov"],
        changelog_file_path=plugin_dir / "CHANGELOG.md",
        append_distributions_to_path=True,
        auto_add_recursive_runtime_dependencies=True,
        version_number_source=VersionNumberSource.CHANGELOG,
        disabled_extra_plugins=[],
    )


@pytest.fixture()
def dev_tools_config_minimal(plugin_dir: Path) -> DevToolsConfig:
    # No python path append and not recursive deps
    from qgis_plugin_dev_tools.config import DevToolsConfig

    return DevToolsConfig(
        plugin_package_name="Plugin",
        runtime_requires=["pytest"],
        changelog_file_path=plugin_dir / "CHANGELOG.md",
        append_distributions_to_path=False,
        auto_add_recursive_runtime_dependencies=False,
        version_number_source=VersionNumberSource.CHANGELOG,
        disabled_extra_plugins=[],
    )


def test_make_zip(dev_tools_config: "DevToolsConfig", tmp_path: Path):
    target_path = tmp_path / "dist"
    expected_zip = target_path / "Plugin-0.1.0.zip"

    make_plugin_zip(dev_tools_config, target_path)

    assert target_path.exists()
    assert expected_zip.exists()

    plugin_init_file_contents = _get_file_from_zip(expected_zip, "Plugin/__init__.py")
    vendor_init_file_contents = _get_file_from_zip(
        expected_zip, "Plugin/_vendor/__init__.py"
    )
    vendor_files = _get_file_names(expected_zip, "Plugin/_vendor/")

    assert "import Plugin._vendor" in plugin_init_file_contents
    assert "sys.path.append" in vendor_init_file_contents
    assert vendor_files == {
        "__init__.py",
        "_pytest",
        "atomicwrites",
        "atomicwrites-1.4.0.dist-info",
        "attr",
        "attrs",
        "attrs-21.4.0.dist-info",
        "colorama",
        "colorama-0.4.4.dist-info",
        "importlib_metadata",
        "importlib_metadata-4.11.3.dist-info",
        "iniconfig",
        "iniconfig-1.1.1.dist-info",
        "packaging",
        "packaging-23.2.dist-info",
        "pluggy",
        "pluggy-1.0.0.dist-info",
        "py",
        "py-1.11.0.dist-info",
        "pytest",
        "pytest-6.2.5.dist-info",
        "toml",
        "toml-0.10.2.dist-info",
        "typing_extensions-4.2.0.dist-info",
        "typing_extensions.py",  # no top-level.txt in .dist-info, parsed from record
        "zipp-3.8.0.dist-info",
        "zipp.py",  # top-level.txt in .dist-info, includes zipp
    }


def test_make_zip_with_duplicate_dependencies(
    dev_tools_config_with_duplicate_dependencies: "DevToolsConfig",
    tmp_path: Path,
):
    target_path = tmp_path / "dist"
    expected_zip = target_path / "Plugin-0.1.0.zip"

    make_plugin_zip(dev_tools_config_with_duplicate_dependencies, target_path)

    assert target_path.exists()
    assert expected_zip.exists()

    plugin_init_file_contents = _get_file_from_zip(expected_zip, "Plugin/__init__.py")
    vendor_init_file_contents = _get_file_from_zip(
        expected_zip, "Plugin/_vendor/__init__.py"
    )
    vendor_files = _get_file_names(expected_zip, "Plugin/_vendor/")

    assert "import Plugin._vendor" in plugin_init_file_contents
    assert "sys.path.append" in vendor_init_file_contents
    assert vendor_files == {
        "__init__.py",
        "_pytest",
        "atomicwrites",
        "atomicwrites-1.4.0.dist-info",
        "attr",
        "attrs",
        "attrs-21.4.0.dist-info",
        "colorama",
        "colorama-0.4.4.dist-info",
        "coverage",
        "coverage-6.3.2.dist-info",
        "importlib_metadata",
        "importlib_metadata-4.11.3.dist-info",
        "iniconfig",
        "iniconfig-1.1.1.dist-info",
        "packaging",
        "packaging-23.2.dist-info",
        "pluggy",
        "pluggy-1.0.0.dist-info",
        "py",
        "py-1.11.0.dist-info",
        "pytest",
        "pytest-6.2.5.dist-info",
        "pytest_cov",
        "pytest_cov-2.12.0.dist-info",
        "toml",
        "toml-0.10.2.dist-info",
        "typing_extensions-4.2.0.dist-info",
        "typing_extensions.py",  # no top-level.txt in .dist-info, parsed from record
        "zipp-3.8.0.dist-info",
        "zipp.py",  # top-level.txt in .dist-info, includes zipp
    }


def test_make_zip_with_minimal_config(
    dev_tools_config_minimal: "DevToolsConfig", tmp_path: Path
):
    target_path = tmp_path / "dist"
    expected_zip = target_path / "Plugin-test-version.zip"

    make_plugin_zip(
        dev_tools_config_minimal, target_path, override_plugin_version="test-version"
    )

    assert target_path.exists()
    assert expected_zip.exists()

    plugin_init_file_contents = _get_file_from_zip(expected_zip, "Plugin/__init__.py")
    vendor_init_file_contents = _get_file_from_zip(
        expected_zip, "Plugin/_vendor/__init__.py"
    )
    vendor_files = _get_file_names(expected_zip, "Plugin/_vendor/")

    assert "import Plugin._vendor" not in plugin_init_file_contents
    assert "sys.path.append" not in vendor_init_file_contents
    assert vendor_files == {
        "__init__.py",
        "_pytest",
        "pytest",
        "pytest-6.2.5.dist-info",
    }


def _get_file_names(zip_file: Path, prefix: str) -> set[str]:
    with zipfile.ZipFile(zip_file) as z:
        namelist = z.namelist()
        return {
            name.replace(prefix, "").split("/")[0]
            for name in namelist
            if name.startswith(prefix) and name != prefix
        }


def _get_file_from_zip(zip_file: Path, file_path: str) -> str:
    with zipfile.ZipFile(zip_file) as z, z.open(file_path) as f:
        return f.read().decode("UTF-8")
