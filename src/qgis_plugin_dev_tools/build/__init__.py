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
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Optional

from qgis_plugin_dev_tools.build.changelog_parser import (
    get_latest_changelog_sections,
    get_latest_changelog_version_identifier,
)
from qgis_plugin_dev_tools.build.metadata import update_metadata_file
from qgis_plugin_dev_tools.build.packaging import (
    copy_plugin_code,
    copy_runtime_requirements,
)
from qgis_plugin_dev_tools.config import DevToolsConfig

LOGGER = logging.getLogger(__name__)


def make_plugin_zip(
    dev_tools_config: DevToolsConfig,
    target_directory_path: Path,
    plugin_version: Optional[str] = None,
) -> None:
    # TODO: make setuptools wrapper and use this code when creating the sdist/wheel?

    changelog_contents = get_latest_changelog_sections(
        dev_tools_config.changelog_file_path
    )
    version = plugin_version or get_latest_changelog_version_identifier(
        dev_tools_config.changelog_file_path
    )
    zip_name = f"{dev_tools_config.plugin_package_name}-{version}"

    with TemporaryDirectory() as build_directory:
        build_directory_path = Path(build_directory)

        LOGGER.debug("building plugin in %s", build_directory_path.resolve())

        copy_plugin_code(dev_tools_config, build_directory_path)
        update_metadata_file(
            (
                Path(build_directory)
                / dev_tools_config.plugin_package_name
                / "metadata.txt"
            ),
            version,
            changelog_contents,
        )
        copy_runtime_requirements(dev_tools_config, build_directory_path)

        LOGGER.debug("creating built plugin zip file from build directory")

        target_directory_path.mkdir(parents=True, exist_ok=True)
        os.chdir(target_directory_path)
        shutil.make_archive(base_name=zip_name, format="zip", root_dir=build_directory)

        LOGGER.info(
            "created %s",
            (Path(zip_name + ".zip")).resolve(),
        )
