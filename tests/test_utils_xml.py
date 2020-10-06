from unittest import TestCase

from quantlaw.utils.xml import hello_world


class UtilsXmlTestCase(TestCase):
    def test_hello_world(self):
        self.assertEqual(hello_world(), "x")
