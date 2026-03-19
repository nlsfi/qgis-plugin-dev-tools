#  Copyright (C) 2026 National Land Survey of Finland
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

from importlib_metadata import packages_distributions, version

LOGGER = logging.getLogger(__name__)


def get_package_version_from_distribution(package_name: str) -> str:
    LOGGER.debug("finding version for %s from distribution metadata", package_name)

    provided_by_distributions = packages_distributions().get(package_name)
    if provided_by_distributions is not None:
        if len(provided_by_distributions) > 1:
            LOGGER.warning(
                "found multiple distributions %s that provide %s,"
                " using version from %s",
                provided_by_distributions,
                package_name,
                provided_by_distributions[0],
            )

        return version(provided_by_distributions[0])

    raise ValueError("version not found from distribution metadata")
