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

from typing import Any

import pytest
from importlib_metadata import distribution
from packaging.requirements import Requirement

from qgis_plugin_dev_tools.utils.distributions import get_distribution_requirements


@pytest.fixture
def sample_dist() -> Any:
    return distribution(Requirement("pytest").name)


def test_get_distribution_requirements(sample_dist: Any):
    requirements = get_distribution_requirements(sample_dist)
    assert sorted(requirements.keys()) == [
        "attrs",
        "importlib-metadata",
        "iniconfig",
        "packaging",
        "pluggy",
        "py",
        "toml",
        "zipp",
    ]
