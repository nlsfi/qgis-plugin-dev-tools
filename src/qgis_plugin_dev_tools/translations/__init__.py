import logging
from pathlib import Path

from qgis_plugin_dev_tools.translations.update_translations import update_ts_file

LOGGER = logging.getLogger(__name__)


def update_translation_files(
    language_codes: list[str],
    search_paths: list[Path],
    destination_path: Path,
    pylupdate_command: str | None,
) -> None:
    py_files = []
    ui_files = []

    for search_path in search_paths:
        py_files.extend(list(search_path.glob("**/*.py")))
        ui_files.extend(list(search_path.glob("**/*.ui")))

    translatable_files = [*py_files, *ui_files]

    for language_code in language_codes:
        ts_file = destination_path / f"{language_code}.ts"
        update_ts_file(translatable_files, ts_file, pylupdate_command)
