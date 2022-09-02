from pathlib import Path
from typing import List

import pytest

from qgis_plugin_dev_tools.config.pyproject import read_pyproject_config


@pytest.fixture()
def create_pyproject_toml_with_contents(tmpdir):
    toml_file_path = Path(tmpdir) / "test.toml"

    def write_contents_from_list(contents: List[str]):
        toml_file_path.write_text("\n".join(contents), encoding="utf-8")
        return toml_file_path

    return write_contents_from_list


def test_section_missing_fails(create_pyproject_toml_with_contents):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.not_the_expected_name]",
            'plugin_package_name = "testing"',
        ]
    )

    with pytest.raises(ValueError):
        read_pyproject_config(test_file)


def test_package_name_missing_fails(create_pyproject_toml_with_contents):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.qgis_plugin_dev_tools]",
            'not_the_package_name_key = "testing"',
        ]
    )

    with pytest.raises(ValueError):
        read_pyproject_config(test_file)


def test_requires_allowed_missing(create_pyproject_toml_with_contents):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.qgis_plugin_dev_tools]",
            'plugin_package_name = "testing"',
        ]
    )

    assert read_pyproject_config(test_file).runtime_requires == []


def test_requires_allowed_empty(create_pyproject_toml_with_contents):
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


def test_section_read_to_dataclass(create_pyproject_toml_with_contents):
    test_file = create_pyproject_toml_with_contents(
        [
            "[tool.qgis_plugin_dev_tools]",
            'plugin_package_name = "testing"',
            'runtime_requires = ["one", "another"]',
            "use_dangerous_vendor_sys_path_append = true",
            "auto_add_recursive_runtime_dependencies = true",
        ]
    )

    result = read_pyproject_config(test_file)

    assert result.plugin_package_name == "testing"
    assert result.runtime_requires == ["one", "another"]
    assert result.use_dangerous_vendor_sys_path_append
    assert result.auto_add_recursive_runtime_dependencies
