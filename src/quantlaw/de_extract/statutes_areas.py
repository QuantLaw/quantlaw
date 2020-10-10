from regex import regex

from quantlaw.de_extract.statutes_abstract import (
    StatusMatch,
    StatutesMatchWithMainArea,
    StatutesProcessor,
)
from quantlaw.de_extract.statutes_areas_patterns import (
    eu_law_name_pattern,
    ignore_law_name_pattern,
    reference_range_pattern,
    sgb_law_name_pattern,
    suffix_ignore_pattern,
)
from quantlaw.de_extract.stemming import stem_law_name


class StatutesExtractor(StatutesProcessor):
    """
    Class to find areas of citations to German statutes and regulations
    """

    def search(self, text: str, pos: int = 0) -> StatusMatch:
        """
        Finds the next occurrence of a statute reference in a given text

        Args:
            text: The text to search in.
            pos: Position to start searching.

        Returns: The match or None if no references are found.
        """

        # Find the main area of the reference
        match = reference_range_pattern.search(text, pos)

        if not match:
            return None

        # Found a trigger e.g "§" not no citation follows
        if not match.groupdict()["main"]:
            return StatusMatch(
                text=text,
                start=match.start(),
                end=match.end(),
            )

        # Get length of optional suffix and law name that may follow the main area.
        # and categorize the reference type.
        suffix_len, law_len, law_match_type = self.get_suffix_and_law_name(
            text[match.end() :]
        )

        # Create a return object
        statutes_match = StatutesMatchWithMainArea(
            text=text,
            start=match.start(),
            end=match.end(),
            suffix_len=suffix_len,
            law_len=law_len,
            law_match_type=law_match_type,
        )

        return statutes_match

    def find_all(self, text: str, pos: int = 0):
        """
        Like search but returns a generator of all matches found in text
        """
        curr_pos = pos
        match = self.search(text, curr_pos)
        while match:
            yield match
            curr_pos = match.end
            if match.has_main_area():
                curr_pos += match.suffix_len + match.law_len
            match = self.search(text, curr_pos)

    def get_suffix_and_law_name(self, string: str):
        """
        Returns: A tuple containing length of

            1. the article between numbers and law name (eg. " der ")
            2. length of name of law as in the given string
            3. The type of the reference.

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
        """
        Determines if the test_str starts with a law name given with self.laws_lookup.

        Returns: The length matched law name or 0.
        """

        # Stem the test_str as the law names are already stemmed
        test_str_stem = stem_law_name(test_str)

        # Look for matching law names
        match = self.match_law_name(test_str_stem)
        if not match:
            return 0

        # Transpose the area of the matched law name in the stemmed text to the
        # original text by splitting the original and the raw text into words (tokens)
        # and define the area of the original string that it contains of the same number
        # of tokens as the matched area in the stemmed string.
        test_str_splitted = regex.findall(r"[\w']+|[\W']+", test_str)
        match_splitted = regex.findall(r"[\w']+|[\W']+", match)
        match_raw = "".join(test_str_splitted[: len(match_splitted)])
        assert len(test_str_splitted[0].strip()) > 0, (match, test_str, test_str_stem)

        # If last matched word of law name does continue after match with
        # a string that would not be stemmed, return no match
        # TODO look for other matches before returning no match
        last_word_test_stemmed = stem_law_name(
            test_str_splitted[len(match_splitted) - 1]
        )
        last_word_match = match_splitted[-1]
        if last_word_match != last_word_test_stemmed:
            return 0

        return len(match_raw)

    @staticmethod
    def get_no_suffix_ignore_law_name_len(test_str) -> int:
        """
        Returns: Length of the law name in chars, if no suffix is present that connects
            the main area with the law name or 0 if no law name of this type was found
        """

        match = ignore_law_name_pattern.match(
            test_str,
        )

        return len(match[0]) if match else 0

    @staticmethod
    def get_sgb_law_name_len(test_str) -> int:
        """
        Returns: The length of the SGB law name in chars or 0 if no law name of this
            type was found
        """

        match = sgb_law_name_pattern.match(
            test_str,
        )

        return len(match[0]) if match else 0

    @staticmethod
    def get_eu_law_name_len(test_str) -> int:
        """
        Returns: The length of the law name of european legislation in chars or
            0 if no law name of this type was found
        """
        match = eu_law_name_pattern.match(
            test_str,
        )
        return len(match[0]) if match else 0

    @staticmethod
    def get_ignore_law_name_len(test_str):
        """
        Returns: Th length of a law name to ignore in chars or 0 if no law name of
            this type was found
        """
        match = suffix_ignore_pattern.match(test_str)
        return len(match[0]) if match else 0
