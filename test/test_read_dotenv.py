import sys
from typing import List

import pytest

from qgis_plugin_dev_tools.config.dotenv import read_dotenv_configs


@pytest.fixture()
def create_dotenv_with_contents(tmp_path_factory):
    def write_contents_from_list(contents: List[str]):
        dotenv_file_path = tmp_path_factory.mktemp(basename="env") / ".env"
        dotenv_file_path.write_text("\n".join(contents), encoding="utf-8")
        return dotenv_file_path

    return write_contents_from_list


def test_executable_must_be_given(create_dotenv_with_contents):
    test_file = create_dotenv_with_contents(["QGIS_EXECUTABLE_PATH="])

    with pytest.raises(ValueError):
        read_dotenv_configs([test_file])


def test_executable_must_exist(create_dotenv_with_contents):
    test_file = create_dotenv_with_contents(
        ["QGIS_EXECUTABLE_PATH=some-missing-binary"]
    )

    with pytest.raises(ValueError):
        read_dotenv_configs([test_file])


def test_optionals_can_be_missing(create_dotenv_with_contents):
    test_file = create_dotenv_with_contents([f"QGIS_EXECUTABLE_PATH={sys.executable}"])

    result = read_dotenv_configs([test_file])
    assert result.DEVELOPMENT_PROFILE_NAME is None
    assert result.DEBUGGER_LIBRARY is None


def test_other_vars_saved_as_runtime_env(create_dotenv_with_contents):
    test_file = create_dotenv_with_contents(
        [
            f"QGIS_EXECUTABLE_PATH={sys.executable}",
            "DEBUGGER_LIBRARY=something",
            "SOME_UNKNOWN_VAR=thing",
            "OTHER_UNKNOWN=1",
        ]
    )

    result = read_dotenv_configs([test_file])
    assert result.runtime_environment == {
        "SOME_UNKNOWN_VAR": "thing",
        "OTHER_UNKNOWN": "1",
    }


def test_empty_vars_not_saved_in_runtime_env(create_dotenv_with_contents):
    test_file = create_dotenv_with_contents(
        [
            f"QGIS_EXECUTABLE_PATH={sys.executable}",
            "DEBUGGER_LIBRARY=something",
            "SOME_UNKNOWN_VAR=thing",
            "OTHER_UNKNOWN=",
        ]
    )

    result = read_dotenv_configs([test_file])
    assert result.runtime_environment == {"SOME_UNKNOWN_VAR": "thing"}


def test_multiple_files_last_overrides(create_dotenv_with_contents):
    test_file_1 = create_dotenv_with_contents(
        [
            f"QGIS_EXECUTABLE_PATH={sys.executable}",
            "DEBUGGER_LIBRARY=something",
            "SOMETHING=thing",
            "FIRST_ONLY=1",
        ]
    )
    test_file_2 = create_dotenv_with_contents(
        [
            "DEBUGGER_LIBRARY=something-else",
            "SOMETHING=123",
            "SECOND_ONLY=2",
        ]
    )

    result = read_dotenv_configs([test_file_1, test_file_2])
    assert result.runtime_environment == {
        "SOMETHING": "123",
        "FIRST_ONLY": "1",
        "SECOND_ONLY": "2",
    }
    assert result.DEBUGGER_LIBRARY == "something-else"
