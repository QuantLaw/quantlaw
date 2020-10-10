import unittest

from quantlaw.de_extract.statutes_areas import StatutesExtractor

sample_laws_lookup = {"buergerlich gesetzbuch": "BGB", "grundgesetz": "GG"}


class DeExtractAreasTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = StatutesExtractor(sample_laws_lookup)

    def test_basic_extracting(self):
        extractor = StatutesExtractor(sample_laws_lookup)
        match = extractor.search(
            "Lorem ipsum § 123 Abs. 3 des Bürgerliches Gesetzbuches"
        )
        self.assertEqual(
            "Main:§ 123 Abs. 3;Suffix: des ;Law:Bürgerliches Gesetzbuches;Type:dict",
            str(match),
        )
        self.assertTrue(match.has_main_area())

    def test_dict(self):
        match = self.extractor.search("Art. 20a Abs. 1 Grundgesetz")
        self.assertEqual(
            "Main:Art. 20a Abs. 1;Suffix: ;Law:Grundgesetz;Type:dict",
            str(match),
        )

    def test_immediate_end(self):
        match = self.extractor.search(
            "Art. 20a Abs. 1",
        )
        self.assertEqual(
            "Main:Art. 20a Abs. 1;Suffix:;Law:;Type:internal",
            str(match),
        )

    def test_sgb(self):
        match = self.extractor.search("§ 123 Drittes Buch Sozialgesetzbuch")
        self.assertEqual(
            "Main:§ 123;Suffix: ;Law:Drittes Buch Sozialgesetzbuch;Type:sgb",
            str(match),
        )

    def test_sgb_suffix(self):
        match = self.extractor.search("§ 123 des Drittes Buch Sozialgesetzbuch")
        self.assertEqual(
            "Main:§ 123;Suffix: des ;Law:Drittes Buch Sozialgesetzbuch;Type:sgb",
            str(match),
        )

    def test_eu(self):
        match = self.extractor.search("Art. 123 der Richtlinie 12/34/EU")
        self.assertEqual(
            "Main:Art. 123;Suffix: der ;Law:Richtlinie 12/34/EU;Type:eu",
            str(match),
        )

    def test_ignore(self):
        match = self.extractor.search(
            "Art. 123 des Gesetzes vom 3. April 2020 (BGBl. I S. 999)"
        )
        self.assertEqual(
            "Main:Art. 123;"
            "Suffix: des ;"
            "Law:Gesetzes vom 3. April 2020 (BGBl. I S. 999);"
            "Type:ignore",
            str(match),
        )

    def test_ignore_suffix(self):
        match = self.extractor.search("§ 123a dieser Verordnung")
        self.assertEqual(
            "Main:§ 123a;Suffix: ;Law:dieser Verordnung;Type:ignore",
            str(match),
        )

    def test_internal(self):
        match = self.extractor.search("zxczc § 123a ihfkjsdfhkjshf jhkjh kdsjfhksdjf ")
        self.assertEqual(
            "Main:§ 123a;Suffix:;Law:;Type:internal",
            str(match),
        )

    def test_last_word_not_matching(self):
        match = self.extractor.search("Art. 123a Grundgesetzkommentar")
        self.assertEqual(
            "Main:Art. 123a;Suffix:;Law:;Type:internal",
            str(match),
        )

    def test_false_suffix(self):
        match = self.extractor.search("Art. 123a der asdasdasd")
        self.assertEqual(
            "Main:Art. 123a;Suffix: der ;Law:;Type:unknown",
            str(match),
        )

    def test_no_match(self):
        match = self.extractor.search("Lorem ipsum")
        self.assertIsNone(match)

    def test_trigger_without_main(self):
        match = self.extractor.search("Lorem § ipsum")
        self.assertFalse(match.has_main_area())

    def test_find_all(self):
        matches = self.extractor.find_all(
            "Art. 123a der asdasdasd df f sdf  § df dfdf  § 123 Grundgesetz"
        )
        self.assertEqual(
            [
                "Main:Art. 123a;Suffix: der ;Law:;Type:unknown",
                "Text:§ ;",
                "Main:§ 123;Suffix: ;Law:Grundgesetz;Type:dict",
            ],
            [str(m) for m in matches],
        )
