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

import os
import sys
import textwrap
import zipfile
from pathlib import Path

import pytest

from qgis_plugin_dev_tools.build import copy_license, make_plugin_zip
from qgis_plugin_dev_tools.config import DevToolsConfig, VersionNumberSource


@pytest.fixture
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

    license_file = tmp_path / "LICENSE"
    license_file.touch()

    os.chdir(tmp_path.resolve())
    sys.path.append(tmp_path.resolve().as_posix())

    return plugin_dir


@pytest.fixture
def dev_tools_config(tmp_path: Path, plugin_dir: Path) -> DevToolsConfig:
    from qgis_plugin_dev_tools.config import DevToolsConfig

    return DevToolsConfig(
        pyproject_path=tmp_path,
        plugin_package_name="Plugin",
        runtime_requires=["pytest"],
        changelog_file_path=plugin_dir / "CHANGELOG.md",
        append_distributions_to_path=True,
        auto_add_recursive_runtime_dependencies=True,
        version_number_source=VersionNumberSource.CHANGELOG,
        disabled_extra_plugins=[],
        license_file_path=None,
        env_file_path=None,
        translation_language_codes=[],
        translation_search_paths=[],
        translation_destination_path=None,
        translation_pylupdate_command=None,
    )


@pytest.fixture
def dev_tools_config_with_duplicate_dependencies(
    tmp_path: Path, plugin_dir: Path
) -> DevToolsConfig:
    from qgis_plugin_dev_tools.config import DevToolsConfig

    return DevToolsConfig(
        pyproject_path=tmp_path,
        plugin_package_name="Plugin",
        runtime_requires=["pytest-cov"],
        changelog_file_path=plugin_dir / "CHANGELOG.md",
        append_distributions_to_path=True,
        auto_add_recursive_runtime_dependencies=True,
        version_number_source=VersionNumberSource.CHANGELOG,
        disabled_extra_plugins=[],
        license_file_path=None,
        env_file_path=None,
        translation_language_codes=[],
        translation_search_paths=[],
        translation_destination_path=None,
        translation_pylupdate_command=None,
    )


@pytest.fixture
def dev_tools_config_minimal(tmp_path: Path, plugin_dir: Path) -> DevToolsConfig:
    # No python path append and not recursive deps
    from qgis_plugin_dev_tools.config import DevToolsConfig

    return DevToolsConfig(
        pyproject_path=tmp_path,
        plugin_package_name="Plugin",
        runtime_requires=["pytest"],
        changelog_file_path=plugin_dir / "CHANGELOG.md",
        append_distributions_to_path=False,
        auto_add_recursive_runtime_dependencies=False,
        version_number_source=VersionNumberSource.CHANGELOG,
        disabled_extra_plugins=[],
        license_file_path=None,
        env_file_path=None,
        translation_language_codes=[],
        translation_search_paths=[],
        translation_destination_path=None,
        translation_pylupdate_command=None,
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
    plugin_files = _get_file_names(expected_zip, "Plugin/")
    assert "LICENSE" in plugin_files

    assert "import Plugin._vendor" in plugin_init_file_contents
    assert "sys.path.append" in vendor_init_file_contents
    assert vendor_files == {
        "__init__.py",
        "_pytest",
        "attr",
        "attrs",
        "attrs-25.4.0.dist-info",
        "importlib_metadata",
        "importlib_metadata-8.7.1.dist-info",
        "iniconfig",
        "iniconfig-2.3.0.dist-info",
        "packaging",
        "packaging-26.0.dist-info",
        "pluggy",
        "pluggy-1.6.0.dist-info",
        "py",
        "py-1.11.0.dist-info",
        "pytest",
        "pytest-6.2.5.dist-info",
        "toml",
        "toml-0.10.2.dist-info",
        "zipp",  #  top-level.txt in .dist-info, includes zipp
        "zipp-3.23.0.dist-info",
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
        "attr",
        "attrs",
        "attrs-25.4.0.dist-info",
        "coverage",
        "coverage-7.6.1.dist-info",
        "importlib_metadata",
        "importlib_metadata-8.7.1.dist-info",
        "iniconfig",
        "iniconfig-2.3.0.dist-info",
        "packaging",
        "packaging-26.0.dist-info",
        "pluggy",
        "pluggy-1.6.0.dist-info",
        "py",
        "py-1.11.0.dist-info",
        "pytest",
        "pytest-6.2.5.dist-info",
        "pytest_cov",
        "pytest_cov-4.1.0.dist-info",
        "toml",
        "toml-0.10.2.dist-info",
        "zipp",
        "zipp-3.23.0.dist-info",
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


@pytest.mark.parametrize("licence_file_name", ["LICENSE", "license.md"])
def test_make_zip_copies_license_from_custom_path(
    dev_tools_config_minimal: "DevToolsConfig", tmp_path: Path, licence_file_name: str
):
    # Remove original
    original_license = tmp_path / "LICENSE"
    os.remove(original_license)

    license_dir = tmp_path / "license"
    license_dir.mkdir()
    license_file = license_dir / licence_file_name
    license_file.touch()
    dev_tools_config_minimal.license_file_path = license_file
    target_path = tmp_path / "dist"
    expected_zip = target_path / "Plugin-test-version.zip"

    make_plugin_zip(
        dev_tools_config_minimal, target_path, override_plugin_version="test-version"
    )

    assert target_path.exists()
    assert expected_zip.exists()
    plugin_files = _get_file_names(expected_zip, "Plugin/")
    assert "LICENSE" in plugin_files


def test_make_zip_copies_license_with_different_name(
    dev_tools_config_minimal: "DevToolsConfig",
    tmp_path: Path,
    plugin_dir: Path,
):
    # Remove original
    original_license = tmp_path / "LICENSE"
    os.remove(original_license)

    license_file = tmp_path / "license.md"
    license_file.touch()

    copy_license(dev_tools_config_minimal, plugin_dir.parent)

    assert (plugin_dir / "LICENSE").exists()


def test_make_zip_does_not_create_license_if_it_does_not_exist(
    dev_tools_config_minimal: "DevToolsConfig", tmp_path: Path
):
    # Remove original
    original_license = tmp_path / "LICENSE"
    os.remove(original_license)

    target_path = tmp_path / "dist"
    expected_zip = target_path / "Plugin-test-version.zip"

    make_plugin_zip(
        dev_tools_config_minimal, target_path, override_plugin_version="test-version"
    )

    assert target_path.exists()
    assert expected_zip.exists()
    plugin_files = _get_file_names(expected_zip, "Plugin/")
    assert "LICENSE" not in plugin_files


def test_make_zip_does_not_create_license_if_configured_one_does_not_exist(
    dev_tools_config_minimal: "DevToolsConfig", tmp_path: Path
):
    dev_tools_config_minimal.license_file_path = tmp_path / "non-existing-license"

    original_license = tmp_path / "LICENSE"
    os.remove(original_license)

    target_path = tmp_path / "dist"
    expected_zip = target_path / "Plugin-test-version.zip"

    make_plugin_zip(
        dev_tools_config_minimal, target_path, override_plugin_version="test-version"
    )

    assert target_path.exists()
    assert expected_zip.exists()
    plugin_files = _get_file_names(expected_zip, "Plugin/")
    assert "LICENSE" not in plugin_files


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
