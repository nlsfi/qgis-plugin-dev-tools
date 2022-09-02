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

from typing import Dict, List

from importlib_metadata import Distribution, distribution
from packaging.requirements import Requirement


def get_distribution_top_level_package_names(dist: Distribution) -> List[str]:
    return (dist.read_text("top_level.txt") or "").split()


def get_distribution_requirements(dist: Distribution) -> Dict[str, Distribution]:
    requirements = [
        Requirement(requirement.split(" ")[0])
        for requirement in dist.requires or []
        if "extra ==" not in requirement
    ]
    distributions = {
        requirement.name: distribution(requirement.name) for requirement in requirements
    }
    sub_requirements = {}
    for requirement in distributions.values():
        sub_requirements.update(get_distribution_requirements(requirement))
    distributions.update(sub_requirements)
    return distributions
