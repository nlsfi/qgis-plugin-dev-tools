import logging
import shutil
import tempfile
from pathlib import Path

from qgis_plugin_dev_tools.translations.update_translations import (
    get_unfinished_translations_count,
    run_command,
    update_ts_file,
)

LOGGER = logging.getLogger(__name__)


def update_translation_files(
    language_codes: list[str],
    search_paths: list[Path],
    destination_path: Path,
    pylupdate_command: str | None,
    check_changes: bool,
) -> None:
    py_files = []
    ui_files = []

    for search_path in search_paths:
        py_files.extend(list(search_path.glob("**/*.py")))
        ui_files.extend(list(search_path.glob("**/*.ui")))

    translatable_files = [file_path.resolve() for file_path in [*py_files, *ui_files]]

    for language_code in language_codes:
        ts_file = destination_path / f"{language_code}.ts"

        with tempfile.TemporaryDirectory() as tmpdir:
            backup_ts_file: Path | None = None
            if check_changes and ts_file.exists():
                backup_ts_file = Path(tmpdir) / "qpdt-backup.ts"
                initial_unfinished_count = get_unfinished_translations_count(ts_file)
                shutil.copy(ts_file, backup_ts_file)

            update_ts_file(translatable_files, ts_file, pylupdate_command)

            if backup_ts_file is None:
                LOGGER.info("Updated translations in %s", ts_file)
                continue

            # Move the original back if there changes
            new_unfinished_count = get_unfinished_translations_count(ts_file)
            if new_unfinished_count == initial_unfinished_count:
                LOGGER.info("No relevant changes in %s, restoring backup", ts_file)
                shutil.copy(backup_ts_file, ts_file)
            else:
                LOGGER.info("Updated translations in %s", ts_file)


def compile_translations(
    language_codes: list[str],
    source_path: Path,
) -> None:
    for language_code in language_codes:
        ts_file = source_path / f"{language_code}.ts"
        qm_file = source_path / f"{language_code}.qm"
        if ts_file.exists():
            LOGGER.debug("compiling %s into %s...", ts_file, qm_file)
            run_command(["lrelease", str(ts_file), "-qm", str(qm_file)])
        else:
            LOGGER.warning(
                "No translation file found for %s in %s", language_code, source_path
            )
