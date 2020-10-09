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
    pass


class NoUnitMatched(Exception):
    pass


class StatutesParser(StatutesProcessor):
    def parse_main(self, main_text: str):
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
        Brings units into a standard format. E.g. removes abbreviations, grammatical
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
    def is_unit(token):
        return regex.fullmatch("|".join(unit_patterns.keys()), token)

    @staticmethod
    def is_pre_numb(token):
        return pre_numb_pattern.fullmatch(
            token,
        )

    @staticmethod
    def is_numb(token):
        return numb_pattern.fullmatch(
            token,
        )

    @staticmethod
    def fix_errors_in_citation(citation):
        result = regex.sub(r"\s+", " ", citation)
        result = regex.sub(r"§(?=\d)", "§ ", result)
        result = regex.sub(r",\sbis\s", " bis ", result)
        return result

    @staticmethod
    def split_citation_into_enum_parts(citation):
        """
        Citation is into enumerative parts. The enumerative part consists of a list.
        In most cases the list contains only one string.
        If the list contains two strings, the part refers to a range.
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
    def split_citation_part(string):
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
                assert StatutesParser.is_unit(token)
                unit = StatutesParser.stem_unit(token)
            elif StatutesParser.is_numb(token):
                unit = None
                numb = token
            else:
                raise StringCaseException(token, "in", string)
            numb = regex.sub(r"(ff?\.|ff|\))$", "", numb)
            yield [unit, numb]
