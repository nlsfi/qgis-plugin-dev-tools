import pytest
from importlib_metadata import distribution
from packaging.requirements import Requirement

from qgis_plugin_dev_tools.utils.distributions import get_distribution_requirements


@pytest.fixture()
def sample_dist():
    return distribution(Requirement("pytest").name)


def test_get_distribution_requirements(sample_dist):
    requirements = get_distribution_requirements(sample_dist)
    assert sorted(requirements.keys()) == [
        "atomicwrites",
        "attrs",
        "colorama",
        "importlib-metadata",
        "iniconfig",
        "packaging",
        "pluggy",
        "py",
        "pyparsing",
        "toml",
        "typing-extensions",
        "zipp",
    ]
