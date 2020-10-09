from unittest.case import TestCase

from quantlaw.de_extract.statutes_areas_patterns import reference_range_pattern


class StatuteParsePatternsTextCase(TestCase):
    def test_reference_areas_iVm_Art(self):
        test_str = (
            "nicht ohne Weiteres der Fall. Art. 2 Abs. 1 i.V.m. Art. 1 "
            "Abs. 1 GG bietet nicht scho"
        )
        res = reference_range_pattern.search(test_str)
        self.assertEqual(str(res[0]), "Art. 2 Abs. 1 i.V.m. Art. 1 Abs. 1")
