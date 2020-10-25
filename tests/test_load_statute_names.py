from unittest import TestCase

from quantlaw.de_extract.load_statute_names import load_law_names


class LoadStatueNamesTestCase(TestCase):
    def test_load_statue_names(self):
        load_law_names("2020-10-20", "test_law_names.json")
