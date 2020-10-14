import unittest

from quantlaw.de_extract.statutes_parse import (
    NoUnitMatched,
    StatutesParser,
    StringCaseException,
)

sample_laws_lookup = {"buergerlich gesetzbuch": "BGB", "grundgesetz": "GG"}


class DeParseAreasTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.extractor = StatutesParser(sample_laws_lookup)

    def test_basic_extracting_main(self):
        match = self.extractor.parse_main("§ 123 Abs. 3")
        self.assertEqual(
            [[["§", "123"], ["Abs", "3"]]],
            match,
        )

    def test_basic_extracting_law_dict(self):
        match = self.extractor.parse_law("Grundgesetz", "dict")
        self.assertEqual(
            "GG",
            match,
        )

    def test_basic_extracting_law_sgb(self):
        match = self.extractor.parse_law("Dritt Buch Sozialgesetzbuch", "sgb")
        self.assertEqual(
            "SGB-3",
            match,
        )

    def test_basic_extracting_law_sgb_variable_key(self):
        match = self.extractor.parse_law("10. Buch Sozialgesetzbuch", "sgb")
        self.assertEqual(
            "SGB-10",
            match,
        )

        parser = StatutesParser({"nothing": "SGB-IX", "nothing2": "SGB-10"})
        match = parser.parse_law("9. Buch Sozialgesetzbuch", "sgb")
        self.assertEqual(
            "SGB-IX",
            match,
        )

        match = parser.parse_law("10. Buch Sozialgesetzbuch", "sgb")
        self.assertEqual(
            "SGB-10",
            match,
        )

    def test_empty_citation_part(self):
        match = self.extractor.parse_main("§ ")
        self.assertEqual(
            [],
            match,
        )

    def test_infer_unit(self):
        match = self.extractor.parse_main("§ 123, 135")
        self.assertEqual(
            [[["§", "123"]], [["§", "135"]]],
            match,
        )

    def test_law_internal(self):
        match = self.extractor.parse_law(None, "internal", "BGB")
        self.assertEqual("BGB", match)

        with self.assertRaises(Exception):
            self.extractor.parse_law(None, "internal")

    def test_law_ignore(self):
        match = self.extractor.parse_law("Grundgesetz", "ignore")
        self.assertIsNone(match)

    def test_unit_error(self):
        with self.assertRaises(StringCaseException):
            self.extractor.parse_main(
                "§ 123 Chapter 2",
            )

    def test_force_splitting_parts_on_highest_unit(self):
        match = self.extractor.parse_main("§ 123 § 124")
        self.assertEqual(
            [[["§", "123"]], [["§", "124"]]],
            match,
        )

    def test_for_docstring(self):
        match = self.extractor.parse_main("§ 123 Abs. 4 Satz 5 und 6")
        # If this test is changes also change the documentation for parse_main function.
        self.assertEqual(
            [
                [["§", "123"], ["Abs", "4"], ["Satz", "5"]],
                [["§", "123"], ["Abs", "4"], ["Satz", "6"]],
            ],
            match,
        )

    def test_for_readme(self):
        # If this test is changes also change the readme.
        match = self.extractor.parse_main("§ 111d Absatz 1 Satz 2")
        self.assertEqual(
            [[["§", "111d"], ["Abs", "1"], ["Satz", "2"]]],
            match,
        )
        match = self.extractor.parse_main("§ 91")
        self.assertEqual(
            [[["§", "91"]]],
            match,
        )

    def test_infer_units(self):
        match = self.extractor.parse_main("§ 123 Abs. 1, 2")
        self.assertEqual(
            [[["§", "123"], ["Abs", "1"]], [["§", "123"], ["Abs", "2"]]],
            match,
        )

        match = self.extractor.parse_main("§ 123 Abs. 1, Abs. 2")
        self.assertEqual(
            [[["§", "123"], ["Abs", "1"]], [["§", "123"], ["Abs", "2"]]],
            match,
        )

        match = self.extractor.parse_main("§ 123 Abs. 1 S. 2, 3 S. 4")
        self.assertEqual(
            [
                [["§", "123"], ["Abs", "1"], ["Satz", "2"]],
                [["§", "123"], ["Abs", "3"], ["Satz", "4"]],
            ],
            match,
        )

    def test_infer_units_not_matching(self):
        match = self.extractor.parse_main("§ 123 Abs. 1 S. 2, 3 Nr. 4")
        self.assertEqual(
            [
                [["§", "123"], ["Abs", "1"], ["Satz", "2"]],
                [["§", "123"], ["Abs", "1"], ["Satz", "3"], ["Nr", "4"]],
            ],
            match,
        )

        match = self.extractor.parse_main("§ 123 Abs. 1, S. 3 Nr. 4")
        self.assertEqual(
            [
                [["§", "123"], ["Abs", "1"]],
                [["§", "123"], ["Abs", "1"], ["Satz", "3"], ["Nr", "4"]],
            ],
            match,
        )

    def test_number_before_unit(self):
        match = self.extractor.parse_main("§ 234 dritter Halbsatz")
        self.assertEqual(
            [[["§", "234"], ["Halbsatz", "dritter"]]],
            match,
        )

    def test_stem_unit_no_unit(self):
        unit = StatutesParser.stem_unit("Artikel")
        self.assertEqual("Art", unit)
        with self.assertRaises(NoUnitMatched):
            StatutesParser.stem_unit("Clause")

    def test_wrong_pre_numb(self):
        match = self.extractor.parse_main("§ 30 DRITTER ABSCHNITT")
        self.assertEqual(
            [[["§", "30"]]],
            match,
        )
