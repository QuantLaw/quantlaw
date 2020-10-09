import unittest
from pkg_resources import DistributionNotFound
from unittest.mock import patch

from quantlaw import get_quantlaw_package_version


def version_test_side_effect(args):
    raise DistributionNotFound()


class InitTestCase(unittest.TestCase):
    def test_version(self):
        version = get_quantlaw_package_version()
        self.assertNotEqual("unknown", version)

        with patch("pkg_resources.get_distribution") as mock:
            mock.side_effect = version_test_side_effect
            version = get_quantlaw_package_version()
            self.assertEqual("unknown", version)
