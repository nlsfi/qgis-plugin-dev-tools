import logging
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def update_ts_file(
    translatable_files: list[Path],
    ts_output_file_path: Path,
    pylupdate_command: str | None,
) -> None:
    if os.name == "nt":
        ensure_pylupdate_main()
        args = [
            ".venv\\Scripts\\python.exe",
            "-m",
            "PyQt5.pylupdate_main",
            *map(str, translatable_files),
            "-ts",
            str(ts_output_file_path),
        ]

        # Use temporary bat-file to by-pass "command line too long"
        # error in subprocess.Popen
        with tempfile.NamedTemporaryFile(mode="w", suffix=".bat") as temp_bat:
            temp_bat_path = Path(temp_bat.name)
            temp_bat_path.write_text(" ".join(args))
            LOGGER.info("Updating ts-file %s...", ts_output_file_path)
            run_command([str(temp_bat_path)])
    else:
        if not pylupdate_command:
            pylupdate_command = find_pylupdate()

        args = [
            pylupdate_command,
            "-noobsolete",
            *map(str, translatable_files),
            "-ts",
            str(ts_output_file_path),
        ]
        LOGGER.info("Updating ts-file %s...", ts_output_file_path)
        run_command(args)


def run_command(args: list[str]) -> None:
    command: str | list[str] = args if os.name == "nt" else " ".join(args)
    pros = subprocess.Popen(
        command,
        cwd=None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True,
    )
    _, stderr = pros.communicate()
    if (
        stderr
        and not stderr.startswith("warning")
        and "DeprecationWarning" not in stderr
    ):
        LOGGER.error(stderr)
        sys.exit(1)


def ensure_pylupdate_main() -> None:
    """Check if PyQt5.pylupdate_main can be executed with python -m."""
    try:
        from PyQt5.pylupdate_main import main as pylupdate_main  # noqa: F401, QGS103
    except ImportError:
        raise ImportError(
            "Could not find PyQt5.pylupdate_main in environment."
        ) from None


def find_pylupdate() -> str:
    candidates: list[str] = []

    env_var = os.environ.get("PYLUPDATE_PATH")
    if env_var:
        candidates.append(env_var)

    # Prefer Qt6, then Qt5
    candidates.extend(["pylupdate6", "pylupdate5", "pylupdate"])

    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path

    raise FileNotFoundError("Could not find pylupdate (Qt5/Qt6). Set PYLUPDATE_PATH.")


def get_unfinished_string_count(ts_file: Path) -> int:
    """Get the number of unfinished strings in the ts-file."""
    data = ts_file.read_text(encoding="utf-8")
    return data.count('<translation type="unfinished">')
