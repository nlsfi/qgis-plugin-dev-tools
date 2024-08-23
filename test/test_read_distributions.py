from typing import Any

import pytest
from importlib_metadata import distribution
from packaging.requirements import Requirement
from qgis_plugin_dev_tools.utils.distributions import get_distribution_requirements


@pytest.fixture()
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
        "typing-extensions",
        "zipp",
    ]
