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

import dataclasses
import logging
import pickle
import sys
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Generator

from qgis_plugin_dev_tools.start.bootstrap.template import BootstrapConfig
from qgis_plugin_dev_tools.start.config import DevelopmentModeConfig

LOGGER = logging.getLogger(__name__)


@contextmanager
def create_bootstrap_file(
    development_mode_configuration: DevelopmentModeConfig, daemon_socket_port: int
) -> Generator[Path, None, None]:
    with TemporaryDirectory() as temp_dir:
        bootstrap_config = BootstrapConfig(
            daemon_socket_port=daemon_socket_port,
            runtime_library_paths=development_mode_configuration.runtime_library_paths,
            runtime_environment=development_mode_configuration.runtime_environment,
            plugin_package_path=development_mode_configuration.plugin_package_path,
            plugin_package_name=development_mode_configuration.plugin_package_name,
            plugin_dependency_package_names=development_mode_configuration.plugin_dependency_package_names,  # noqa E501
            debugger_library=development_mode_configuration.debugger_library,
            bootstrap_python_executable_path=Path(sys.executable),
            extra_plugin_package_names=development_mode_configuration.extra_plugin_package_names,  # noqa E501
        )

        LOGGER.debug("using bootstrap config:\n%s", bootstrap_config)

        bootstrap_template_contents = resources.read_text(
            __name__, "template.py", encoding="utf-8"
        ).replace(
            'b"$DATACLASS_AS_PICKLED_DICT$"',
            repr(pickle.dumps(dataclasses.asdict(bootstrap_config))),
        )

        bootstrap_file_path = Path(temp_dir) / "bootstrap.py"
        bootstrap_file_path.write_text(bootstrap_template_contents, encoding="utf-8")

        yield bootstrap_file_path
