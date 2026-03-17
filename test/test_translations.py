import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from qgis_plugin_dev_tools.translations import (
    update_translation_files,
)
from qgis_plugin_dev_tools.translations.update_translations import (
    ensure_pylupdate_main,
    find_pylupdate,
    run_command,
    update_ts_file,
)


@pytest.fixture
def translation_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a test project with Python and UI files."""
    project_dir = tmp_path / "test_plugin"
    project_dir.mkdir()

    # Create Python files
    py_dir = project_dir / "src"
    py_dir.mkdir()
    (py_dir / "module1.py").write_text('tr("Hello")')
    (py_dir / "module2.py").write_text('tr("World")')

    # Create UI files
    ui_dir = project_dir / "ui"
    ui_dir.mkdir()
    (ui_dir / "form1.ui").write_text("<ui></ui>")

    # Create destination path
    i18n_dir = project_dir / "i18n"
    i18n_dir.mkdir()

    return project_dir, py_dir, i18n_dir


def test_update_translation_files_collects_files(
    translation_project: tuple[Path, Path, Path], mocker: MockerFixture
) -> None:
    project_dir, _, i18n_dir = translation_project

    mock_update = mocker.patch("qgis_plugin_dev_tools.translations.update_ts_file")
    update_translation_files(
        language_codes=["fi", "sv"],
        search_paths=[project_dir],
        destination_path=i18n_dir,
        pylupdate_command=None,
    )

    assert mock_update.call_count == 2

    # Check first call for 'fi'
    call_args_fi = mock_update.call_args_list[0]
    translatable_files = call_args_fi[0][0]
    ts_file = call_args_fi[0][1]

    assert len(translatable_files) == 3
    assert any("module1.py" in str(f) for f in translatable_files)
    assert any("module2.py" in str(f) for f in translatable_files)
    assert any("form1.ui" in str(f) for f in translatable_files)
    assert ts_file == i18n_dir / "fi.ts"

    # Check second call for 'sv'
    call_args_sv = mock_update.call_args_list[1]
    ts_file_sv = call_args_sv[0][1]
    assert ts_file_sv == i18n_dir / "sv.ts"


def test_update_translation_files_multiple_search_paths(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    # Create two separate source directories
    dir1 = tmp_path / "src1"
    dir1.mkdir()
    (dir1 / "file1.py").write_text('tr("Test1")')

    dir2 = tmp_path / "src2"
    dir2.mkdir()
    (dir2 / "file2.py").write_text('tr("Test2")')

    i18n_dir = tmp_path / "i18n"
    i18n_dir.mkdir()

    mock_update = mocker.patch("qgis_plugin_dev_tools.translations.update_ts_file")
    update_translation_files(
        language_codes=["en"],
        search_paths=[dir1, dir2],
        destination_path=i18n_dir,
        pylupdate_command=None,
    )

    translatable_files = mock_update.call_args[0][0]
    assert len(translatable_files) == 2
    assert any("file1.py" in str(f) for f in translatable_files)
    assert any("file2.py" in str(f) for f in translatable_files)


def test_run_command_success(mocker: MockerFixture) -> None:
    mock_process = MagicMock()
    mock_process.communicate.return_value = ("output", "")
    mock_popen = mocker.patch("subprocess.Popen", return_value=mock_process)

    run_command(["echo", "test"])

    mock_popen.assert_called_once()


def test_run_command_handles_warnings(mocker: MockerFixture) -> None:
    mock_process = MagicMock()
    mock_process.communicate.return_value = ("", "warning: some warning")
    mocker.patch("subprocess.Popen", return_value=mock_process)

    # Should not raise
    run_command(["command"])


def test_run_command_handles_deprecation_warnings(mocker: MockerFixture) -> None:
    mock_process = MagicMock()
    mock_process.communicate.return_value = ("", "DeprecationWarning: old feature")
    mocker.patch("subprocess.Popen", return_value=mock_process)

    # Should not raise
    run_command(["command"])


def test_run_command_exits_on_error(mocker: MockerFixture) -> None:
    mock_process = MagicMock()
    mock_process.communicate.return_value = ("", "error: something failed")
    mocker.patch("subprocess.Popen", return_value=mock_process)

    with pytest.raises(SystemExit):
        run_command(["command"])


def test_ensure_pylupdate_main_success(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        "sys.modules", {"PyQt5.pylupdate_main": MagicMock(main=lambda: None)}
    )
    # Should not raise
    ensure_pylupdate_main()


def test_ensure_pylupdate_main_missing(mocker: MockerFixture) -> None:
    mocker.patch.dict("sys.modules", {"PyQt5.pylupdate_main": None})
    with pytest.raises(ImportError, match=r"Could not find PyQt5.pylupdate_main"):
        ensure_pylupdate_main()


def test_find_pylupdate_from_env_var(mocker: MockerFixture) -> None:
    fake_path = "/custom/path/pylupdate"
    mocker.patch.dict(os.environ, {"PYLUPDATE_PATH": fake_path})
    mocker.patch("shutil.which", return_value=fake_path)

    result = find_pylupdate()
    assert result == fake_path


def test_find_pylupdate_prefers_qt6(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {}, clear=True)

    def which_side_effect(cmd: str) -> str | None:
        if cmd == "pylupdate6":
            return "/usr/bin/pylupdate6"
        return None

    mocker.patch("shutil.which", side_effect=which_side_effect)

    result = find_pylupdate()
    assert result == "/usr/bin/pylupdate6"


def test_find_pylupdate_falls_back_to_qt5(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {}, clear=True)

    def which_side_effect(cmd: str) -> str | None:
        if cmd == "pylupdate5":
            return "/usr/bin/pylupdate5"
        return None

    mocker.patch("shutil.which", side_effect=which_side_effect)

    result = find_pylupdate()
    assert result == "/usr/bin/pylupdate5"


def test_find_pylupdate_raises_when_not_found(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {}, clear=True)
    mocker.patch("shutil.which", return_value=None)

    with pytest.raises(FileNotFoundError, match="Could not find pylupdate"):
        find_pylupdate()


@pytest.mark.skipif(os.name != "posix", reason="Non-Windows test")
def test_update_ts_file_unix(tmp_path: Path, mocker: MockerFixture) -> None:
    py_file = tmp_path / "test.py"
    py_file.write_text('tr("Test")')
    ts_file = tmp_path / "test.ts"

    mocker.patch(
        "qgis_plugin_dev_tools.translations.update_translations.find_pylupdate",
        return_value="pylupdate5",
    )
    mock_run = mocker.patch(
        "qgis_plugin_dev_tools.translations.update_translations.run_command"
    )

    update_ts_file([py_file], ts_file, pylupdate_command=None)

    mock_run.assert_called_once()
    args = mock_run.call_args[0][0]
    assert args[0] == "pylupdate5"
    assert "-noobsolete" in args
    assert str(py_file) in args
    assert "-ts" in args
    assert str(ts_file) in args


@pytest.mark.skipif(os.name != "posix", reason="Non-Windows test")
def test_update_ts_file_unix_with_custom_command(
    tmp_path: Path, mocker: MockerFixture
) -> None:
    py_file = tmp_path / "test.py"
    py_file.write_text('tr("Test")')
    ts_file = tmp_path / "test.ts"

    mock_run = mocker.patch(
        "qgis_plugin_dev_tools.translations.update_translations.run_command"
    )
    update_ts_file([py_file], ts_file, pylupdate_command="/custom/pylupdate")

    args = mock_run.call_args[0][0]
    assert args[0] == "/custom/pylupdate"


@pytest.mark.skipif(os.name != "nt", reason="Windows-only test")
def test_update_ts_file_windows(tmp_path: Path, mocker: MockerFixture) -> None:
    py_file = tmp_path / "test.py"
    py_file.write_text('tr("Test")')
    ts_file = tmp_path / "test.ts"

    mocker.patch(
        "qgis_plugin_dev_tools.translations.update_translations.ensure_pylupdate_main"
    )
    mock_run = mocker.patch(
        "qgis_plugin_dev_tools.update_translations.translations.run_command"
    )
    mock_temp_file = MagicMock()
    mock_temp_file.name = "temp.bat"
    mock_temp = mocker.patch("tempfile.NamedTemporaryFile")
    mock_temp.__enter__ = MagicMock(return_value=mock_temp_file)
    mock_temp.__exit__ = MagicMock()

    mock_write = mocker.patch("pathlib.Path.write_text")
    update_ts_file([py_file], ts_file, pylupdate_command=None)

    # Should use PyQt5.pylupdate_main on Windows
    mock_write.assert_called_once()
    mock_run.assert_called_once()
    written_content = mock_write.call_args[0][0]
    assert "PyQt5.pylupdate_main" in written_content
