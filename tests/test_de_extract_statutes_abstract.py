import unittest

from quantlaw.de_extract.statutes_abstract import StatutesProcessor

sample_laws_lookup = {"buergerlich gesetzbuch": "BGB", "grundgesetz": "GG"}


class DeExtractAreasTestCase(unittest.TestCase):
    def test_laws_lookup_property(self):
        extractor = StatutesProcessor(sample_laws_lookup)
        self.assertEqual(
            sample_laws_lookup,
            extractor.laws_lookup,
        )
        self.assertEqual(
            ["grundgesetz", "buergerlich gesetzbuch"], extractor.laws_lookup_keys
        )
        another_dict = {"abc": "efg"}
        extractor.laws_lookup = another_dict
        self.assertEqual(another_dict, extractor.laws_lookup)
        self.assertEqual(["abc"], extractor.laws_lookup_keys)
