from regex import regex

from quantlaw.de_extract.statutes_parse_patterns import (
    fix_errors_in_citation,
    infer_units,
    sgb_dict,
    split_citation_into_enum_parts,
    split_citation_part,
    split_parts_accidently_joined,
)
from quantlaw.de_extract.statutes_patterns import (
    eu_law_name_pattern,
    ignore_law_name_pattern,
    reference_range_pattern,
    sgb_law_name_pattern,
    suffix_ignore_pattern,
)
from quantlaw.de_extract.stemming import stem_law_name


class StatusMatch:
    """
    Class to report the areas of citations to German statutes and regulations
    if a trigger e.g. '§' is found but it is not followed by a citation.
    """

    def __init__(
        self,
        text: str,
        start: int,
        end: int,
    ):
        self.text = text
        self.start = start
        self.end = end

    def has_main_area(self):
        return False


class StatutesMatchWithMainArea(StatusMatch):
    """
    Class to report the areas of citations to German statutes and regulations
    """

    def __init__(
        self,
        suffix_len: int,
        law_len: int,
        law_match_type: str,
        *args,
        **kwargs,
    ):
        self.suffix_len = suffix_len
        self.law_len = law_len
        self.law_match_type = law_match_type
        super().__init__(*args, **kwargs)

    def has_main_area(self):
        return True

    def main_text(self):
        """
        Returns: The main area of a citation, which is the text part that specifies
        the cited part of the statute but omitting the name of the law.
        E.g. "§ 123 Abs. 4, Nr 5 und 6"
        """
        return self.text[self.start : self.end]

    def suffix_text(self):
        """
        Returns: The text joins the main part of the citation with the name of the
        cited law.
        An empty sting is return if no law is specified. This is typically the case
        for references within a law.
        """
        return self.text[self.end : self.end + self.suffix_len]

    def law_text(self):
        """
        Returns: The referenced law.
        """
        law_start_pos = self.end + self.suffix_len
        return self.text[law_start_pos : law_start_pos + self.law_len]

    def __str__(self):
        return (
            f"Main:{self.main_text()};"
            f"Suffix:{self.suffix_text()};"
            f"Law:{self.law_text()};"
            f"Type:{self.law_match_type}"
        )


class StatutesProcessor:
    def __init__(self, laws_lookup: dict):
        self._laws_lookup = None
        self.laws_lookup_keys = None
        self.laws_lookup = laws_lookup

    @property
    def laws_lookup(self) -> dict:
        return self._laws_lookup

    @laws_lookup.setter
    def laws_lookup(self, val: dict):
        """
        Args:
            val: A dictionary to find of the law names to extract.
                Keys are names of laws that are used in the source text used to cite
                laws. Values are unique identifiers of laws.
                For optimal results is is recommended to make the list a exhaustive as
                possible to reduce the chance that references are false treated as
                internal references within a law because the name of the referenced law
                is not recognized. The names of the laws should be provided in a
                stemmed format using the stemmer provided in
                `quantlaw.de_extract.stemming.stem_law_name`.
        """
        self._laws_lookup = val

        # Sort be decreasing string length to favor matches of long law names.
        self.laws_lookup_keys = sorted(val.keys(), reverse=True)

    def match_law_name(self, text: str):
        """
        Checks if the text begins with a law name provided in self.laws_lookup_keys.

        Returns: The matched substring.

        """
        for law in self.laws_lookup_keys:
            if text[: len(law)] == law:
                return law
        return None


class StatutesExtractor(StatutesProcessor):
    """
    Class to find areas of citations to German statutes and regulations
    """

    def search(self, text: str, pos: int = 0) -> StatusMatch:
        """
        Finds the next occurence of a statute reference in a given text

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

    def get_no_suffix_ignore_law_name_len(self, test_str):

        match = ignore_law_name_pattern.match(
            test_str,
        )

        return len(match[0]) if match else 0

    def get_sgb_law_name_len(self, test_str):

        match = sgb_law_name_pattern.match(
            test_str,
        )

        return len(match[0]) if match else 0

    def get_eu_law_name_len(self, test_str):
        match = eu_law_name_pattern.match(
            test_str,
        )
        return len(match[0]) if match else 0

    def get_ignore_law_name_len(self, test_str):
        match = suffix_ignore_pattern.match(test_str)
        return len(match[0]) if match else 0


class ParsedResult:
    def __init__(self):
        pass


class StringCaseException(Exception):
    pass


class StatutesParser(StatutesProcessor):
    def parse_main(self, main_text: str):
        citation = fix_errors_in_citation(main_text.strip())

        enum_parts = split_citation_into_enum_parts(citation)

        reference_paths = []
        for enum_part in enum_parts:
            for string in enum_part:
                splitted_citation_part_list = list(split_citation_part(string))
                if len(splitted_citation_part_list):
                    reference_paths.append(splitted_citation_part_list)
                else:
                    print(f"Empty citation part in {citation} in part {string}")

        reference_paths = split_parts_accidently_joined(reference_paths)

        for reference_path in reference_paths[1:]:
            prev_reference_path = reference_paths[
                reference_paths.index(reference_path) - 1
            ]
            infer_units(reference_path, prev_reference_path)

        return reference_paths

    def parse_law(self, law_text: str, match_type: str, current_lawid: str = None):
        """
        Parses the law information from a references found by StatutesMatchWithMainArea

        Args:
            main_text: E.g. "§ 123 Abs. 4 und 5 Nr. 6"
            law_text: E.g. "BGB"
            match_type: E.g. "dict"

        Returns:

        """

        if match_type == "dict":
            lawname_stem = stem_law_name(law_text)
            match = self.match_law_name(lawname_stem)
            return self.laws_lookup[match]

        elif match_type == "sgb":
            lawid = sgb_dict[stem_law_name(law_text)]
            if type(lawid) is tuple:
                assert len(lawid) == 2
                if lawid[0] in self.laws_lookup_keys:
                    return lawid[0]
                elif lawid[1] in self.laws_lookup_keys:
                    return lawid[1]
                else:
                    return lawid[1]

        elif match_type == "internal":
            if current_lawid is None:
                raise Exception("Current law id must be set for internal reference")
            return current_lawid

        else:
            return None  # match_type: ignore or unknown
