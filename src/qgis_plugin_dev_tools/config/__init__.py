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
from enum import Enum, auto
from importlib.util import find_spec
from pathlib import Path
from typing import Optional

from importlib_metadata import Distribution, distribution
from packaging.requirements import Requirement

from qgis_plugin_dev_tools.config.pyproject import read_pyproject_config
from qgis_plugin_dev_tools.utils.distributions import get_distribution_requirements


class VersionNumberSource(Enum):
    CHANGELOG = auto()
    DISTRIBUTION = auto()

    @staticmethod
    def from_config_value(config_value: str) -> "VersionNumberSource":
        try:
            return VersionNumberSource[config_value.upper()]
        except KeyError:
            raise ValueError(f"{config_value=} is not a valid value") from None


class DevToolsConfig:
    pyproject_path: Path
    plugin_package_name: str
    plugin_package_path: Path
    runtime_distributions: list[Distribution]
    changelog_file_path: Path
    append_distributions_to_path: bool
    version_number_source: VersionNumberSource
    disabled_extra_plugins: list[str]
    license_file_path: Optional[Path]

    def __init__(  # noqa: PLR0913
        self,
        pyproject_path: Path,
        plugin_package_name: str,
        runtime_requires: list[str],
        changelog_file_path: Path,
        append_distributions_to_path: bool,
        auto_add_recursive_runtime_dependencies: bool,
        version_number_source: VersionNumberSource,
        disabled_extra_plugins: list[str],
        license_file_path: Optional[Path],
    ) -> None:
        plugin_package_spec = find_spec(plugin_package_name)
        if plugin_package_spec is None or plugin_package_spec.origin is None:
            raise ValueError(
                f"could not find {plugin_package_name=} in the current environment"
            )

        self.pyproject_path = pyproject_path
        self.plugin_package_path = Path(plugin_package_spec.origin).parent
        self.plugin_package_name = plugin_package_name
        # TODO: check versions are satisfied?
        self.runtime_distributions = [
            distribution(Requirement(spec).name) for spec in runtime_requires
        ]
        self.changelog_file_path = changelog_file_path
        self.append_distributions_to_path = append_distributions_to_path
        self.version_number_source = version_number_source
        self.extra_runtime_distributions = []
        self.disabled_extra_plugins = disabled_extra_plugins
        self.license_file_path = license_file_path

        if auto_add_recursive_runtime_dependencies:
            # Add the requirements of the distributions as well
            distributions_versions = {
                dist.name: dist.version for dist in self.runtime_distributions
            }
            self.extra_runtime_distributions = [
                dist
                for dist in ChainMap(
                    *(
                        get_distribution_requirements(dist)
                        for dist in self.runtime_distributions
                    )
                ).values()
                if distributions_versions.get(dist.name) != dist.version
            ]

    @staticmethod
    def from_pyproject_config(pyproject_file_path: Path) -> "DevToolsConfig":
        pyproject_config = read_pyproject_config(pyproject_file_path)
        return DevToolsConfig(
            pyproject_path=pyproject_file_path,
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
            version_number_source=VersionNumberSource.from_config_value(
                pyproject_config.version_number_source
            ),
            disabled_extra_plugins=pyproject_config.disabled_extra_plugins,
            license_file_path=pyproject_file_path.parent
            / pyproject_config.license_file_path
            if pyproject_config.license_file_path
            else None,
        )
