import sys
from pathlib import Path
from typing import List

import pytest

from qgis_plugin_dev_tools.config.dotenv import read_dotenv_config


@pytest.fixture()
def create_dotenv_with_contents(tmpdir):
    dotenv_file_path = Path(tmpdir) / ".env"

    def write_contents_from_list(contents: List[str]):
        dotenv_file_path.write_text("\n".join(contents))
        return dotenv_file_path

    return write_contents_from_list


def test_executable_must_be_given(create_dotenv_with_contents):
    test_file = create_dotenv_with_contents(["QGIS_EXECUTABLE_PATH="])

    with pytest.raises(ValueError):
        read_dotenv_config(test_file)


def test_executable_must_exist(create_dotenv_with_contents):
    test_file = create_dotenv_with_contents(
        ["QGIS_EXECUTABLE_PATH=some-missing-binary"]
    )

    with pytest.raises(ValueError):
        read_dotenv_config(test_file)


def test_optionals_can_be_missing(create_dotenv_with_contents):
    test_file = create_dotenv_with_contents([f"QGIS_EXECUTABLE_PATH={sys.executable}"])

    result = read_dotenv_config(test_file)
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

    result = read_dotenv_config(test_file)
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

    result = read_dotenv_config(test_file)
    assert result.runtime_environment == {"SOME_UNKNOWN_VAR": "thing"}
