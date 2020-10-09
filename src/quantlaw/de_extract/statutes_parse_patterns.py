import itertools
from collections import Counter

from regex import regex


def generate_sgb_dict():
    """
    Returns a dictionary, Its keys are different ways how SGB books are cited. They are
    mapped to values that represent the keys to the SGB books.

    """
    sgb_dict_word = [
        "erst",
        "zweit",
        "dritt",
        "viert",
        "fuenft",
        "sechst",
        "siebt",
        "acht",
        "neunt",
        "zehnt",
        "elft",
        "zwoelft",
    ]

    sgb_dict_roman = [
        "i",
        "ii",
        "iii",
        "iv",
        "v",
        "vi",
        "vii",
        "viii",
        "ix",
        "x",
        "xi",
        "xii",
    ]

    sgb_dict = {}

    # Iterate through the 12 books and add different ways to cite them to the sgb_dict
    for idx in range(12):
        nr = idx + 1
        word = sgb_dict_word[idx]
        roman = sgb_dict_roman[idx]

        # Books 9 and 10 appear to have a roman numbering in the abbreviation by
        # juris and gesetze-im-internet. Abbreviations of the other books are always
        # contain arabic numbering.
        if nr in {9, 10}:
            value = (f"SGB-{roman.upper()}", f"SGB-{nr}")
        else:
            value = f"SGB-{nr}"

        sgb_dict[f"{word} buch"] = value
        sgb_dict[f"{word} buch sozialgesetzbuch"] = value
        sgb_dict[f"{word} buch d sozialgesetzbuch"] = value
        sgb_dict[f"sgb {roman}"] = value
        sgb_dict[f"sgb {nr}"] = value
        sgb_dict[f"{nr}. buch sozialgesetzbuch"] = value
        sgb_dict[f"sgb-{roman}"] = value
        sgb_dict[f"sgb-{nr}"] = value

    return sgb_dict


sgb_dict = generate_sgb_dict()


unit_patterns = {
    r"§{1,2}": "§",
    r"Art\b\.?|[Aa]rtikels?n?": "Art",
    r"Nr\b\.?|Nummer|Nrn?\b\.?": "Nr",
    r"[Aa][Bb]s\b\.?|Absatz|Absätze": "Abs",
    r"Unter[Aa]bsatz|Unter[Aa]bs\b\.?": "Uabs",
    r"S\b\.?|Satz|Sätze": "Satz",
    r"Ziffern?|Ziffn?\b\.?": "Ziffer",
    r"Buchstaben?|Buchst\b\.?": "Buchstabe",
    r"Halbsatz": "Halbsatz",
    r"Teilsatz": "Teilsatz",
    r"Abschnitte?|Abschn\b\.?": "Abschnitt",
    r"Alternativen?|Alt\b\.?": "Alternative",
    r"Anhang|Anhänge": "Anhang",
}


class NoUnitMatched(Exception):
    pass


def stem_unit(unit: str):
    """
    Brings units into a standard format. E.g. removes abbreviations, grammatical
    differences spelling errors, etc.

    Args:
        unit: A string containing a unit that should be converted into a standard
            format.

    Returns: Unit in a standard format as string. E.g. §, Art, Nr, Halbsatz, Anhand, ...
    """
    for unit_pattern in unit_patterns:
        if regex.fullmatch(unit_pattern, unit):
            return unit_patterns[unit_pattern]
    raise NoUnitMatched(unit)


def is_unit(token):
    return regex.fullmatch("|".join(unit_patterns.keys()), token)


def is_pre_numb(token):
    # fmt: off
    return regex.fullmatch(
        r"("
        r"erste|"
        r"zweite|"
        r"dritte|"
        r"letzte"
        r")r?s?",
        token,
        flags=regex.IGNORECASE,
    )
    # fmt: on


def is_numb(token):
    # fmt: off
    return regex.fullmatch(
        r"("
        r"\d+(?>\.\d+)*[a-z]?|"
        r"[ivx]+|"
        r"[a-z]\)?"
        r")"
        r"("
        r"ff?\.|"
        r"ff\b|"
        r"(?<=[a-z])\)|"
        r"\b"
        r")",
        token,
        flags=regex.IGNORECASE,
    )
    # fmt: on


def fix_errors_in_citation(citation):
    result = regex.sub(r"\s+", " ", citation)
    result = regex.sub(r"§(?=\d)", "§ ", result)
    result = regex.sub(r",\sbis\s", " bis ", result)
    return result


def split_citation_into_enum_parts(citation):
    """
    Citation is into enumerative parts. The enumerative part consists of a list.
    In most cases the list contains only one string.
    If the list contains two strings, the part refers to a range.
    """
    # fmt: off
    enum_parts = regex.split(
        r"(?>\s*,?(?>" r",\s*|" r"\s+und\s+|" r"\s+sowie\s+|"
        #             r'\s+bis\s+|'
        r"\s+oder\s+|"
        r"(?>\s+jeweils)?(?>\s+auch)?\s+(?>in\s+Verbindung\s+mit|i\.?\s?V\.?\s?m\.?)\s+"
        r"))"
        r"(?>nach\s+)?"
        r"(?>(?>der|des|den|die)\s+)?",
        citation,
        flags=regex.IGNORECASE,
    )
    # fmt: on

    # Split range
    enum_parts = [regex.split(r"\s*,?\s+bis\s+", part) for part in enum_parts]
    return enum_parts


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
    tokens = regex.split(
        r"\s|(?<=Art\.|Art\b|Artikeln|Artikel)(?=\d)|(?<=§)(?=[A-Z0-9])",
        string,
        flags=regex.IGNORECASE,
    )
    while len(tokens) > 0:
        token = tokens.pop(0)
        if is_unit(token):
            if len(tokens) > 0:
                unit = stem_unit(token)
                token = tokens.pop(0)
                numb = token
                assert is_numb(numb), numb
            else:  # when citation ends with unit
                print(f"Citation {string} ends with unit {token}. Ignoring last unit.")
                break

        elif is_pre_numb(token):
            numb = token
            token = tokens.pop(0)
            assert is_unit(token)
            unit = stem_unit(token)
        elif is_numb(token):
            unit = None
            numb = token
        else:
            from quantlaw.de_extract.statutes import StringCaseException

            raise StringCaseException(token, "in", string)
        numb = regex.sub(r"(ff?\.|ff|\))$", "", numb)
        yield [unit, numb]


def split_parts_accidently_joined(reference_paths):
    new_reference_paths = []
    main_unit = (
        "Art"
        if Counter([part[0] for part in itertools.chain(*reference_paths)]).get("Art")
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
