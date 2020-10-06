import unittest

from quantlaw.de_extract.statutes import StatutesExtractor

sample_laws_lookup = {"buergerlich gesetzbuch": "BGB", "grundgesetz": "GG"}


class DeExtractTestCase(unittest.TestCase):
    def test_something(self):
        extractor = StatutesExtractor(sample_laws_lookup)
        match = extractor.search("Lorem ipsum § 123 Abs. 3 Bürgerliches Gesetzbuch")
        self.assertEqual(
            "Main: § 123 Abs. 3;Suffix:  ;Law: Bürgerliches Gesetzbuch",
            str(match),
        )
