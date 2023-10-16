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
import importlib.util
import logging
from importlib.machinery import SourceFileLoader
from typing import Dict, List, Optional, cast

import importlib_metadata
from importlib_metadata import Distribution, distribution
from packaging.requirements import Requirement

LOGGER = logging.getLogger(__name__)


def get_distribution_top_level_package_names(dist: Distribution) -> List[str]:
    if (
        top_level_contents := cast(
            Optional[str],
            dist.read_text("top_level.txt"),
        )
    ) is None:
        LOGGER.debug("%s has no top level packages", dist.name)
        return []

    return top_level_contents.split()


def get_distribution_top_level_script_names(dist: Distribution) -> List[str]:
    if (file_paths := dist.files) is None:
        LOGGER.warning("%s file catalog missing", dist.name)
        return []

    return [
        file_path.stem
        for file_path in file_paths
        if len(file_path.parts) == 1 and file_path.match("*.py")
    ]


def get_distribution_requirements(dist: Distribution) -> Dict[str, Distribution]:
    requirements = [
        Requirement(requirement.split(" ")[0])
        for requirement in dist.requires or []
        if "extra ==" not in requirement
    ]
    distributions = {}
    for requirement in requirements:
        try:
            distributions[requirement.name] = distribution(requirement.name)
        except importlib_metadata.PackageNotFoundError:
            LOGGER.warning(
                "Getting distribution for %s failed. "
                "This may be caused by including builtin "
                "packages as requirements.",
                requirement.name,
            )
            spec = importlib.util.find_spec(requirement.name)
            loader = cast(Optional[SourceFileLoader], spec.loader) if spec else None
            if spec and loader and loader.is_package(requirement.name):
                LOGGER.error("Could not find package %s", requirement.name)
            continue

    sub_requirements = {}
    for requirement in distributions.values():
        sub_requirements.update(get_distribution_requirements(requirement))
    distributions.update(sub_requirements)
    return distributions
