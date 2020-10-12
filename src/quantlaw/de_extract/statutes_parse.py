import itertools
from collections import Counter

from regex import regex

from quantlaw.de_extract.statutes_abstract import StatutesProcessor
from quantlaw.de_extract.statutes_parse_patterns import (
    numb_pattern,
    pre_numb_pattern,
    sgb_dict,
    split_citation_into_parts_pattern,
    split_citation_into_range_parts_pattern,
    split_unit_number_pattern,
    unit_patterns,
)
from quantlaw.de_extract.stemming import stem_law_name


class StringCaseException(Exception):
    """
    Exception is raised if a unit in a reference cannot be parsed. In this case it is
    often an issue of upper oder lower case formatting.
    """

    pass


class NoUnitMatched(Exception):
    """
    Exception is raised if a unit in a refren cannot be parsed.
    """

    pass


class StatutesParser(StatutesProcessor):
    """
    Class to parse the content of a reference area identified by StatutesExtractor
    """

    def parse_main(self, main_text: str) -> list:
        """
        Parses a string containing a reference to a specific section within a given law.
        E.g. "§ 123 Abs. 4 Satz 5 und 6".
        The parsed informtaion is formatted into lists nested in lists nested in lists.

        The outer list is a list of references.

        References are lists of path components. A path component is e.g. "Abs. 4".

        A path component is represented by a list with two elements: The first
        contains the unit the second the value.

        The example above would be represented as
        `[[['§', '123'], ['Abs', '4'], ['Satz', '5']],
        [['§', '123'], ['Abs', '4'], ['Satz', '6']]]`.

        Args:
            main_text: string to parse

        Returns: The parsed reference.
        """
        citation = self.fix_errors_in_citation(main_text.strip())

        enum_parts = self.split_citation_into_enum_parts(citation)

        reference_paths = []
        for enum_part in enum_parts:
            for string in enum_part:
                splitted_citation_part_list = list(self.split_citation_part(string))
                if len(splitted_citation_part_list):
                    reference_paths.append(splitted_citation_part_list)
                else:
                    print(f"Empty citation part in {citation} in part {string}")

        reference_paths = self.split_parts_accidently_joined(reference_paths)

        for reference_path in reference_paths[1:]:
            prev_reference_path = reference_paths[
                reference_paths.index(reference_path) - 1
            ]
            self.infer_units(reference_path, prev_reference_path)

        return reference_paths

    def parse_law(self, law_text: str, match_type: str, current_lawid: str = None):
        """
        Parses the law information from a references found by StatutesMatchWithMainArea

        Args:
            main_text: E.g. "§ 123 Abs. 4 und 5 Nr. 6"
            law_text: E.g. "BGB"
            match_type: E.g. "dict"

        Returns: The key of a parse law.

        """

        if match_type == "dict":
            lawname_stem = stem_law_name(law_text)
            match = self.match_law_name(lawname_stem)
            return self.laws_lookup[match]

        elif match_type == "sgb":
            lawid = sgb_dict[stem_law_name(law_text)]
            if type(lawid) is tuple:
                assert len(lawid) == 2
                if lawid[0] in self.laws_lookup.values():
                    return lawid[0]
                elif lawid[1] in self.laws_lookup.values():
                    return lawid[1]
                else:
                    return lawid[1]
            else:
                return lawid

        elif match_type == "internal":
            if current_lawid is None:
                raise Exception("Current law id must be set for internal reference")
            return current_lawid

        else:
            return None  # match_type: ignore or unknown

    @staticmethod
    def stem_unit(unit: str):
        """
        Brings a unit into a standard format. E.g. removes abbreviations, grammatical
        differences spelling errors, etc.

        Args:
            unit: A string containing a unit that should be converted into a standard
                format.

        Returns: Unit in a standard format as string. E.g. §, Art, Nr, Halbsatz,
            Anhang, ...
        """
        for unit_pattern in unit_patterns:
            if regex.fullmatch(unit_pattern, unit):
                return unit_patterns[unit_pattern]
        raise NoUnitMatched(unit)

    @staticmethod
    def is_unit(token: str):
        """
        Returns: True if the token is a unit
        """
        return regex.fullmatch("|".join(unit_patterns.keys()), token)

    @staticmethod
    def is_pre_numb(token: str):
        """
        Returns: True if the token is a number that comes *before* the unit.
        E.g. '*erster* Halbsatz'
        """
        return pre_numb_pattern.fullmatch(
            token,
        )

    @staticmethod
    def is_numb(token: str):
        """
        Returns: True if the token is a 'numeric' value of the reference.
        """
        return numb_pattern.fullmatch(
            token,
        )

    @staticmethod
    def fix_errors_in_citation(citation):
        """
        Fix some common inconsistencies in the references such as double spaces.
        """
        result = regex.sub(r"\s+", " ", citation)
        result = regex.sub(r"§(?=\d)", "§ ", result)
        result = regex.sub(r",\sbis\s", " bis ", result)
        return result

    @staticmethod
    def split_citation_into_enum_parts(citation):
        """
        A citation can contain references to multiple parts of the law.
        E.g. '§§ 20 und 35' or 'Art. 3 Abs. 1 Satz 1, Abs. 3 Satz 1'.
        The citation is split into parts so that each referenced section of the law is
        separated. E.g. '§§ 20' and '35' resp. 'Art. 3 Abs. 1 Satz 1' and
        'Abs. 3 Satz 1'.
        However, ranges are not spit: E.g. "§§ 1 bis 10" will not be split.
        """
        enum_parts = split_citation_into_parts_pattern.split(
            citation,
        )

        # Split range
        enum_parts = [
            split_citation_into_range_parts_pattern.split(part) for part in enum_parts
        ]
        return enum_parts

    @staticmethod
    def split_parts_accidently_joined(reference_paths):
        """
        Reformats the parsed references to separate accitently joined references.
        E.g. the original referehence "§ 123 § 126" will not be split by
        split_citation_into_enum_parts because the separation is falsly not indicated by
        a ',', 'or' etc. It come from the unit '§' that it can be inferred that the
        citation contains references to two parts of statutes.
        This function accounts for the case that the unit '§' or 'Art' appears twice in
        the same reference path and split the path into several elements.
        """
        new_reference_paths = []
        main_unit = (
            "Art"
            if Counter([part[0] for part in itertools.chain(*reference_paths)]).get(
                "Art"
            )
            else "§"
        )
        for reference_path in reference_paths:
            temp_path = []
            for part in reference_path:
                if part[0] == main_unit:
                    if len(temp_path):
                        new_reference_paths.append(temp_path)
                    temp_path = []
                temp_path.append(part)
            new_reference_paths.append(temp_path)
        return new_reference_paths

    @staticmethod
    def infer_units(reference_path, prev_reference_path):
        """
        In some cases of an enumeration a numeric value is not directed prefixed by
        the corresponding unit. E.g. "§ 123 Abs. 1 S. 2, 3 S. 4". In this case "3"
        is not prefixed with its unit. Instead it can be inferred by looking at the
        whole citation that it is next higher unit of "S.", hence "Abs.". These
        inferred units are added to parsed data.
        """
        prev_path_units = [o[0] for o in prev_reference_path]
        if reference_path[0][0]:
            pass
        elif len(reference_path) > 1:
            try:
                prev_unit_index = prev_path_units.index(reference_path[1][0])
                # if not prev_unit_index > 0:
                #     print(f'Infer unit error: {citation}')
                reference_path[0][0] = prev_path_units[prev_unit_index - 1]
            except ValueError:
                reference_path[0][0] = prev_path_units[-1]
        else:
            reference_path[0][0] = prev_path_units[-1]

        try:
            prev_unit_index = prev_path_units.index(reference_path[0][0])
            reference_path[0:0] = prev_reference_path[:prev_unit_index]
        except Exception:
            reference_path[0:0] = prev_reference_path

    @staticmethod
    def split_citation_part(string: str):
        """
        A string a tokenizes. Tokens are identified as units or values. Pairs are
        built to connect the units with their respective values. If the unit cannot
        be indentified (and must be inferred later) None is returned.

        Args:
            string: A string that is part of a reference and cites *one* part a statute.

        Retruns: As a generator tuples are returned, each containing the unit (or None)
            and the respecive value.
        """

        # Tokenization

        # fmt: off
        string = regex.sub(
            r"("
            r"\d+(?>\.\d+)?[a-z]?|"
            r"\b[ivx]+|"
            r"\b[a-z]\)?"
            r")"
            r"(\sff?\.|\sff\b)",
            r"\1ff.",
            string,
            flags=regex.IGNORECASE,
        )
        # fmt: on
        tokens = split_unit_number_pattern.split(
            string,
        )

        # Building pairs of units with their resp. values

        while len(tokens) > 0:
            token = tokens.pop(0)
            if StatutesParser.is_unit(token):
                if len(tokens) > 0:
                    unit = StatutesParser.stem_unit(token)
                    token = tokens.pop(0)
                    numb = token
                    assert StatutesParser.is_numb(numb), numb
                else:  # when citation ends with unit
                    print(
                        f"Citation {string} ends with unit {token}. Ignoring last unit."
                    )
                    break

            elif StatutesParser.is_pre_numb(token):
                numb = token
                token = tokens.pop(0)
                if not StatutesParser.is_unit(token):
                    print(token, "is not a unit in", string)
                    continue
                    # to fix citation "§ 30 DRITTER ABSCHNITT"
                    # Last part in now ignored,
                    # but reference areas can still be improved.
                unit = StatutesParser.stem_unit(token)

            elif StatutesParser.is_numb(token):
                unit = None
                numb = token
            else:
                raise StringCaseException(token, "in", string)
            numb = regex.sub(r"(ff?\.|ff|\))$", "", numb)
            yield [unit, numb]
