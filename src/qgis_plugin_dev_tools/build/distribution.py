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
