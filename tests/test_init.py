import unittest
from pkg_resources import DistributionNotFound
from unittest.mock import patch


def version_test_side_effect(args):
    raise DistributionNotFound()


class InitTestCase(unittest.TestCase):
    @patch("pkg_resources.get_distribution")
    def test_version(self, mock):
        mock.side_effect = version_test_side_effect

        import quantlaw as quantlaw_test

        self.assertEqual("unknown", quantlaw_test.__version__)
