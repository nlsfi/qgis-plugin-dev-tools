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

from collections.abc import Callable
from pathlib import Path

import pytest

from qgis_plugin_dev_tools.config.pyproject import read_pyproject_config


@pytest.fixture
def create_pyproject_toml_with_contents(tmpdir: str) -> Callable[[list[str]], Path]:
    toml_file_path = Path(tmpdir) / "test.toml"

    def write_contents_from_list(contents: list[str]) -> Path:
        toml_file_path.write_text("\n".join(contents), encoding="utf-8")
        return toml_file_path

    return write_contents_from_list


def test_section_missing_fails(
    create_pyproject_toml_with_contents: Callable[[list[str]], Path],
):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.not_the_expected_name]",
            'plugin_package_name = "testing"',
        ]
    )

    with pytest.raises(ValueError, match="config invalid"):
        read_pyproject_config(test_file)


def test_package_name_missing_fails(
    create_pyproject_toml_with_contents: Callable[[list[str]], Path],
):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.qgis_plugin_dev_tools]",
            'not_the_package_name_key = "testing"',
        ]
    )

    with pytest.raises(ValueError, match="not_the_package_name_key"):
        read_pyproject_config(test_file)


def test_requires_allowed_missing(
    create_pyproject_toml_with_contents: Callable[[list[str]], Path],
):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.qgis_plugin_dev_tools]",
            'plugin_package_name = "testing"',
        ]
    )

    assert read_pyproject_config(test_file).runtime_requires == []


def test_requires_allowed_empty(
    create_pyproject_toml_with_contents: Callable[[list[str]], Path],
):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.qgis_plugin_dev_tools]",
            'plugin_package_name = "testing"',
            "runtime_requires = []",
        ]
    )

    result = read_pyproject_config(test_file)
    assert result.runtime_requires == []
    assert not result.use_dangerous_vendor_sys_path_append
    assert not result.auto_add_recursive_runtime_dependencies


def test_section_read_to_dataclass(
    create_pyproject_toml_with_contents: Callable[[list[str]], Path],
):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.qgis_plugin_dev_tools]",
            'plugin_package_name = "testing"',
            'runtime_requires = ["one", "another"]',
            "use_dangerous_vendor_sys_path_append = true",
            "auto_add_recursive_runtime_dependencies = true",
            'changelog_file_path = "../../CHANGELOG.md"',
        ]
    )

    result = read_pyproject_config(test_file)

    assert result.plugin_package_name == "testing"
    assert result.runtime_requires == ["one", "another"]
    assert result.use_dangerous_vendor_sys_path_append
    assert result.auto_add_recursive_runtime_dependencies
    assert result.changelog_file_path == "../../CHANGELOG.md"
