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

from collections import ChainMap
from pathlib import Path
from typing import List

from importlib_metadata import Distribution, distribution
from packaging.requirements import Requirement

from qgis_plugin_dev_tools.config.pyproject import read_pyproject_config
from qgis_plugin_dev_tools.utils.distributions import get_distribution_requirements


class DevToolsConfig:
    plugin_package_name: str
    plugin_package_path: Path
    runtime_distributions: List[Distribution]
    changelog_file_path: Path
    append_distributions_to_path: bool

    def __init__(
        self,
        plugin_package_name: str,
        runtime_requires: List[str],
        changelog_file_path: Path,
        append_distributions_to_path: bool,
        auto_add_recursive_runtime_dependencies: bool,
    ) -> None:
        self.plugin_package_name = plugin_package_name
        self.plugin_package_path = Path(
            __import__(self.plugin_package_name).__file__  # type: ignore
        ).parent
        # TODO: check versions are satisfied?
        self.runtime_distributions = [
            distribution(Requirement(spec).name) for spec in runtime_requires
        ]
        self.changelog_file_path = changelog_file_path
        self.append_distributions_to_path = append_distributions_to_path
        self.extra_runtime_distributions = []

        if auto_add_recursive_runtime_dependencies:
            # Add the requirements of the distributions as well
            self.extra_runtime_distributions = list(
                ChainMap(
                    *(
                        get_distribution_requirements(dist)
                        for dist in self.runtime_distributions
                    )
                ).values()
            )

    @staticmethod
    def from_pyproject_config(pyproject_file_path: Path) -> "DevToolsConfig":
        pyproject_config = read_pyproject_config(pyproject_file_path)
        return DevToolsConfig(
            plugin_package_name=pyproject_config.plugin_package_name,
            runtime_requires=pyproject_config.runtime_requires,
            # TODO: allow setting path in pyproject file?
            changelog_file_path=pyproject_file_path.parent / "CHANGELOG.md",
            append_distributions_to_path=(
                pyproject_config.use_dangerous_vendor_sys_path_append
            ),
            auto_add_recursive_runtime_dependencies=(
                pyproject_config.auto_add_recursive_runtime_dependencies
            ),
        )
