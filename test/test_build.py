import os
import sys
import textwrap
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Set

import pytest

from qgis_plugin_dev_tools.build import make_plugin_zip

if TYPE_CHECKING:
    from qgis_plugin_dev_tools.config import DevToolsConfig


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
def dev_tools_config(plugin_dir: Path):
    from qgis_plugin_dev_tools.config import DevToolsConfig

    return DevToolsConfig(
        plugin_package_name="Plugin",
        runtime_requires=["pytest"],
        changelog_file_path=plugin_dir / "CHANGELOG.md",
        append_distributions_to_path=True,
        auto_add_recursive_runtime_dependencies=True,
    )


@pytest.fixture()
def dev_tools_config_minimal(plugin_dir: Path):
    # No python path append and not recursive deps
    from qgis_plugin_dev_tools.config import DevToolsConfig

    return DevToolsConfig(
        plugin_package_name="Plugin",
        runtime_requires=["pytest"],
        changelog_file_path=plugin_dir / "CHANGELOG.md",
        append_distributions_to_path=False,
        auto_add_recursive_runtime_dependencies=False,
    )


def test_make_zip(dev_tools_config: "DevToolsConfig", plugin_dir: Path, tmp_path: Path):
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
        "packaging-21.3.dist-info",
        "pluggy",
        "pluggy-1.0.0.dist-info",
        "py",
        "py-1.11.0.dist-info",
        "pyparsing-3.0.8.dist-info",
        "pytest",
        "pytest-6.2.5.dist-info",
        "toml",
        "toml-0.10.2.dist-info",
        "typing_extensions-4.2.0.dist-info",
        "zipp-3.8.0.dist-info",
        "zipp.py",
    }


def test_make_zip_with_minimal_config(
    dev_tools_config_minimal: "DevToolsConfig", plugin_dir: Path, tmp_path: Path
):
    target_path = tmp_path / "dist"
    expected_zip = target_path / "Plugin-test-version.zip"

    make_plugin_zip(
        dev_tools_config_minimal, target_path, plugin_version="test-version"
    )

    assert target_path.exists()
    assert expected_zip.exists()

    plugin_init_file_contents = _get_file_from_zip(expected_zip, "Plugin/__init__.py")
    vendor_init_file_contents = _get_file_from_zip(
        expected_zip, "Plugin/_vendor/__init__.py"
    )
    vendor_files = _get_file_names(expected_zip, "Plugin/_vendor/")

    assert "import Plugin._vendor" not in plugin_init_file_contents
    assert vendor_init_file_contents == ""
    assert vendor_files == {
        "__init__.py",
        "_pytest",
        "pytest",
        "pytest-6.2.5.dist-info",
    }


def _get_file_names(zip_file: Path, prefix: str) -> Set[str]:
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
