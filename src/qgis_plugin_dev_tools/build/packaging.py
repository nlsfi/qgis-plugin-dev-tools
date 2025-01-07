#  Copyright (C) 2022 National Land Survey of Finland
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

import logging
import shutil
import sys
from typing import Generator, Optional

from importlib_metadata import Distribution
from pathlib import Path

from qgis_plugin_dev_tools.build.rewrite_imports import (
    rewrite_imports_in_source_file,
    insert_as_first_import,
)
from qgis_plugin_dev_tools.config import DevToolsConfig
from qgis_plugin_dev_tools.utils.distributions import get_distribution_top_level_names

IGNORED_FILES = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyi")
LOGGER = logging.getLogger(__name__)

VENDOR_PATH_APPEND_SCRIPT = """
import sys
from pathlib import Path

sys.path.append(Path(__file__).parent.resolve().as_posix())
"""


def copy_plugin_code(
    dev_tools_config: DevToolsConfig, build_directory_path: Path
) -> None:
    LOGGER.debug(
        "copying %s to build directory",
        dev_tools_config.plugin_package_path.resolve(),
    )
    shutil.copytree(
        src=dev_tools_config.plugin_package_path,
        dst=build_directory_path / dev_tools_config.plugin_package_name,
        ignore=IGNORED_FILES,
    )


def copy_runtime_requirements(
    dev_tools_config: DevToolsConfig,
    build_directory_path: Path,
) -> None:
    if len(dev_tools_config.runtime_distributions) == 0:
        return

    plugin_package_name = dev_tools_config.plugin_package_name
    vendor_path = build_directory_path / plugin_package_name / "_vendor"

    vendor_path.mkdir(parents=True)
    vendor_init_file = vendor_path / "__init__.py"
    vendor_init_file.touch()

    if dev_tools_config.append_distributions_to_path:
        vendor_init_file.write_text(VENDOR_PATH_APPEND_SCRIPT)
        insert_as_first_import(
            build_directory_path / plugin_package_name / "__init__.py",
            f"{plugin_package_name}._vendor",
        )

    vendored_runtime_top_level_names: list[str] = []

    for vendored_distribution in (
        dev_tools_config.runtime_distributions
        + dev_tools_config.extra_runtime_distributions
    ):
        # if a recursively found dependency is provided by system packages,
        # assume it does not have to be bundled (this is possibly dangerous,
        # if build is made on a different system package set than runtime)
        if (
            vendored_distribution in dev_tools_config.extra_runtime_distributions
            and Path(
                vendored_distribution._path,  # type: ignore
            ).is_relative_to(Path(sys.base_prefix))
        ):
            LOGGER.warning(
                "skipping recursively found runtime requirement %s "
                "because it is included in system packages",
                vendored_distribution.name,
            )
            continue

        # don't vendor plugin package, but allow to vendor other packages provided
        # from plugin distribution. if "-e ." installs "my-plugin-name" distribution
        # containing my_plugin & my_util_package top level packages, bundling is only
        # needed for my_util_package
        dist_top_level_names = get_distribution_top_level_names(vendored_distribution)
        dist_top_level_names.discard(plugin_package_name)

        LOGGER.debug(
            "bundling runtime requirement %s with top level names %s",
            vendored_distribution.name,
            dist_top_level_names,
        )
        _copy_distribution_files(
            vendored_distribution,
            dist_top_level_names,
            vendor_path,
        )

        vendored_runtime_top_level_names.extend(dist_top_level_names)

    if not dev_tools_config.append_distributions_to_path:
        for package_name in vendored_runtime_top_level_names:
            LOGGER.debug("rewriting imports for %s", package_name)

            py_files = list((build_directory_path / plugin_package_name).rglob("*.py"))
            ui_files = list((build_directory_path / plugin_package_name).rglob("*.ui"))

            for source_file in py_files + ui_files:
                rewrite_imports_in_source_file(
                    source_file,
                    rewritten_package_name=package_name,
                    container_package_name=f"{plugin_package_name}._vendor",
                )


def copy_license(dev_tools_config: DevToolsConfig, build_directory_path: Path) -> None:
    plugin_build_path = build_directory_path / dev_tools_config.plugin_package_name
    target_license_file = plugin_build_path / "LICENSE"
    license_file = dev_tools_config.license_file_path
    if license_file is not None:
        if not license_file.exists():
            LOGGER.error(
                f"Configured license file "
                f"{license_file} "
                f"does not exist. Check the configuration."
            )
            return

        if target_license_file.exists():
            LOGGER.warning(
                f"Overwriting existing license {target_license_file} "
                f"with configured license {license_file}"
            )
        LOGGER.debug(f"Copying license file {license_file} to {build_directory_path}")
        shutil.copy(license_file, target_license_file)
        return

    if target_license_file.exists():
        LOGGER.debug(f"Existing license file {target_license_file} found.")
        return

    # Try finding the license
    license_file = _find_existing_license_file(dev_tools_config.pyproject_path)
    if not license_file:
        LOGGER.warning(
            "Cannot copy LICENSE file since it does not exist. "
            "Configure valid LICENSE file with license_file_path in pyproject.toml"
        )
        return

    LOGGER.debug(f"Copying license file {license_file} to {build_directory_path}")
    shutil.copy(license_file, target_license_file)


def _copy_distribution_files(
    distribution: Distribution,
    top_level_names: set[str],
    target_root_path: Path,
) -> None:
    if (file_paths := distribution.files) is None:
        LOGGER.warning("could not resolve %s contents to bundle", distribution.name)
        return

    # bundle metadata directory first
    distribution_metadata_path = Path(distribution._path)  # type: ignore
    LOGGER.debug(
        "copying %s to build directory",
        distribution_metadata_path.resolve(),
    )
    shutil.copytree(
        src=distribution_metadata_path,
        dst=target_root_path / distribution_metadata_path.name,
        ignore=IGNORED_FILES,
    )

    directories_to_bundle = {
        top_directory_name
        for file_path in file_paths
        if len(file_path.parts) > 1
        and (top_directory_name := file_path.parts[0]) in top_level_names
    }
    files_to_bundle = {
        file_path
        for file_path in file_paths
        if len(file_path.parts) == 1 and file_path.stem in top_level_names
    }

    record_root_path = distribution_metadata_path.parent

    for directory_path in directories_to_bundle:
        original_path = record_root_path / directory_path
        new_path = target_root_path / directory_path

        LOGGER.debug("copying %s to build directory", original_path.resolve())

        shutil.copytree(
            src=original_path,
            dst=new_path,
            ignore=IGNORED_FILES,
        )

    for file_path in files_to_bundle:
        original_path = record_root_path / file_path
        new_path = target_root_path / file_path

        LOGGER.debug("copying %s to build directory", original_path.resolve())

        shutil.copy(
            src=original_path,
            dst=new_path,
        )


def _find_existing_license_file(search_path: Path) -> Optional[Path]:
    def generate_license_candidates() -> Generator[Path, None, None]:
        for base_name in ("LICENSE", "license"):
            for extension in ("", ".md", ".MD"):
                yield search_path / f"{base_name}{extension}"

    for potential_path in generate_license_candidates():
        if potential_path.exists():
            return potential_path
    return None
