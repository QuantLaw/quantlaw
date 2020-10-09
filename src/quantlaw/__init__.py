# -*- coding: utf-8 -*-

dist_name = __name__


def get_quantlaw_package_version():
    from pkg_resources import DistributionNotFound, get_distribution

    try:
        # Change here if project is renamed and does not equal the package name
        version = get_distribution(dist_name).version
    except DistributionNotFound:
        version = "unknown"

        return version


__version__ = get_quantlaw_package_version()
