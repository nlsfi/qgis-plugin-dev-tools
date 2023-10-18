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
from typing import Optional, cast

import importlib_metadata
from importlib_metadata import Distribution, distribution
from packaging.requirements import Requirement

LOGGER = logging.getLogger(__name__)


def get_distribution_top_level_names(dist: Distribution) -> set[str]:
    if (file_paths := dist.files) is None:
        LOGGER.warning("could not resolve %s top level names", dist.name)
        return set()

    return {
        top_level_directory_name
        for path in file_paths
        if (
            len(path.parts) > 1
            and not (top_level_directory_name := path.parts[0]).endswith(
                (".dist-info", ".egg-info")
            )
            and top_level_directory_name not in ("..", "__pycache__")
        )
    } | {
        path.stem
        for path in file_paths
        if len(path.parts) == 1 and path.suffix in (".py", ".pyd")
    }


def get_distribution_requirements(dist: Distribution) -> dict[str, Distribution]:
    requirement_distributions: dict[str, Distribution] = {}

    requirements = [
        Requirement(requirement.split(" ")[0])
        for requirement in dist.requires or []
        if "extra ==" not in requirement
    ]
    for requirement in requirements:
        try:
            requirement_distributions[requirement.name] = distribution(requirement.name)
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

    nested_requirement_distributions: dict[str, Distribution] = {}
    for requirement_distribution in requirement_distributions.values():
        nested_requirement_distributions.update(
            get_distribution_requirements(requirement_distribution)
        )
    requirement_distributions.update(nested_requirement_distributions)

    return requirement_distributions
