from regex import regex

from quantlaw.de_extract.statutes_patterns import (
    reference_range_pattern,
    suffix_ignore_pattern,
)
from quantlaw.de_extract.stemming import stem_law_name


class StatutesMatch:
    """
    Class to report the areas of citations to German statutes and regulations
    """

    def __init__(
        self,
        text: str,
        start: int,
        end: int,
        suffix_len: int,
        law_len: int,
        law_match_type: str,
    ):
        self.text = text
        self.start = start
        self.end = end
        self.suffix_len = suffix_len
        self.law_len = law_len
        self.law_match_type = law_match_type

    def main_text(self):
        return self.text[self.start : self.end]

    def suffix_text(self):
        return self.text[self.end : self.end + self.suffix_len]

    def law_text(self):
        law_start_pos = self.end + self.suffix_len
        return self.text[law_start_pos : law_start_pos + self.law_len]

    def __str__(self):
        return (
            f"Main:{self.main_text()};"
            f"Suffix:{self.suffix_text()};"
            f"Law:{self.law_text()}"
        )


class StatutesExtractor:
    """
    Class to find areas of citations to German statutes and regulations
    """

    def __init__(self, laws_lookup):
        self._laws_lookup = None
        self.laws_lookup_keys = None
        self.laws_lookup = laws_lookup

    @property
    def laws_lookup(self) -> dict:
        return self._laws_lookup

    @laws_lookup.setter
    def laws_lookup(self, val: dict):
        self._laws_lookup = val
        self.laws_lookup_keys = sorted(val.keys(), reverse=True)

    def search(self, text, pos=0):
        match = reference_range_pattern.search(text, pos)

        suffix_len, law_len, law_match_type = self.get_suffix_and_law_name(
            text[match.end() :]
        )

        statutes_match = StatutesMatch(
            text=text,
            start=match.start(),
            end=match.end(),
            suffix_len=suffix_len,
            law_len=law_len,
            law_match_type=law_match_type,
        )

        return statutes_match

    def get_suffix_and_law_name(self, string):
        """
        Returns a tuple containing length of
        1. the article between numbers and law name (eg. " der ")
        2. length of name of law as in the given string
        If not found lengths are 0.
        """
        suffix_match = regex.match(r"^,?\s+?de[sr]\s+", string)

        if suffix_match:

            suffix_len = suffix_match.end()
            law_test = string[suffix_len : suffix_len + 1000]

            dict_suffix_len = self.get_dict_law_name_len(law_test)
            if dict_suffix_len:
                return suffix_len, dict_suffix_len, "dict"

            sgb_suffix_len = self.get_sgb_law_name_len(law_test)
            if sgb_suffix_len:
                return suffix_len, sgb_suffix_len, "sgb"

            eu_suffix_len = self.get_eu_law_name_len(law_test)
            if eu_suffix_len:
                return suffix_len, eu_suffix_len, "eu"

            ignore_suffix_len = self.get_ignore_law_name_len(law_test)
            if ignore_suffix_len:
                return suffix_len, ignore_suffix_len, "ignore"

            return suffix_len, 0, "unknown"

        else:  # no der/des suffix
            suffix_match = regex.match(r"^[\s\n]+", string[:1000])
            if suffix_match:
                suffix_len = len(suffix_match[0])
                law_test = string[suffix_len:1000]

                dict_suffix_len = self.get_dict_law_name_len(law_test)
                if dict_suffix_len:
                    return suffix_len, dict_suffix_len, "dict"

                sgb_suffix_len = self.get_sgb_law_name_len(law_test)
                if sgb_suffix_len:
                    return suffix_len, sgb_suffix_len, "sgb"

                ignore_no_suffix_len = self.get_no_suffix_ignore_law_name_len(law_test)
                if ignore_no_suffix_len:
                    return suffix_len, ignore_no_suffix_len, "ignore"

            return 0, 0, "internal"

    def get_dict_law_name_len(self, test_str):
        test_str_stem = stem_law_name(test_str)
        match = self.match_law_name(test_str_stem)
        if not match:
            return 0
        test_str_splitted = regex.findall(r"[\w']+|[\W']+", test_str)
        match_splitted = regex.findall(r"[\w']+|[\W']+", match)
        match_raw = "".join(test_str_splitted[: len(match_splitted)])
        assert len(test_str_splitted[0].strip()) > 0, (match, test_str, test_str_stem)

        # Filter if last matched word of law name does not continue after match with
        # a string that would not be stemmed
        last_word_test_stemmed = stem_law_name(
            test_str_splitted[len(match_splitted) - 1]
        )
        last_word_match = match_splitted[-1]
        if last_word_match != last_word_test_stemmed:
            return 0

        return len(match_raw)

    def get_no_suffix_ignore_law_name_len(self, test_str):

        # fmt: off
        match = regex.match(
            r"^("
            r"dieser Verordnung|"
            r"(G|AnO)\s?[i\d-\/]* v(om)?\.? \d+\.\s?\d+\.\s?\d+( I+)? [\d-]+"
            r")",
            test_str,
            flags=regex.IGNORECASE,
        )
        # fmt: on

        return len(match[0]) if match else 0

    def get_sgb_law_name_len(self, test_str):

        # fmt: off
        match = regex.match(
            r"^("
            r"("
                r"erst|zweit|dritt|viert|fünft|sechst|siebt|acht|neunt|zehnt|elft|"
                r"zwölft|\d{1,2}\."
            r")"
            r"en?s? buche?s?(( des)? sozialgesetzbuche?s?)?"
            r"|"
            r"SGB"
            r"(\s|\-)"
            r"("
            r"(I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)\b"
            r"|"
            r"\d{1,2}"
            r")"
            r")",
            test_str,
            flags=regex.IGNORECASE,
        )
        # fmt: on

        return len(match[0]) if match else 0

    def get_eu_law_name_len(self, test_str):
        # fmt: off
        match = regex.match(
            r"^("
                r"(Delegierten )?"
                r"(Durchführungs)?"
                r"(Verordnung|Richtlinie)\s?"
                r"\((EU|EW?G|Euratom)\)\s+(Nr\.\s+)?\d+/\d+"
            r"|"
            r"(Durchführungs)?(Richtlinie|Entscheidung)\s+\d+/\d+/(EW?G|EU)\b|"
            r"(Rahmen)?beschlusses\s\d+/\d+/\w\w\b"
            r")",
            test_str,
            flags=regex.IGNORECASE,
        )
        # fmt: on
        return len(match[0]) if match else 0

    def get_ignore_law_name_len(self, test_str):
        match = suffix_ignore_pattern.match(test_str)
        return len(match[0]) if match else 0

    def match_law_name(self, more_stemmed):
        for law in self.laws_lookup_keys:
            if more_stemmed[: len(law)] == law:
                return law
        return None
