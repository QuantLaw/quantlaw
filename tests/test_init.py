import unittest
from pkg_resources import DistributionNotFound
from unittest.mock import patch


class InitTestCase(unittest.TestCase):
    @patch("pkg_resources.get_distribution")
    def test_version(self, mock):
        mock.side_effect = DistributionNotFound()
        import quantlaw

        self.assertEqual("unknown", quantlaw.__version__)
