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
    r"[Aa][Bb][Ss]\b\.?|Absatz|Absätze": "Abs",
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

# fmt: off
pre_numb_pattern = regex.compile(
    r"("
    r"erste|"
    r"zweite|"
    r"dritte|"
    r"letzte"
    r")r?s?",
    flags=regex.IGNORECASE,
)


numb_pattern = regex.compile(
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
    flags=regex.IGNORECASE,
)


split_citation_into_parts_pattern_str = (
    r"(?>\s*,?(?>" r",\s*|" r"\s+und\s+|" r"\s+sowie\s+|"
    #             r'\s+bis\s+|'
    r"\s+oder\s+|"
    r"(?>\s+jeweils)?(?>\s+auch)?\s+(?>in\s+Verbindung\s+mit|i\.?\s?V\.?\s?m\.?)\s+"
    r"))"
    r"(?>nach\s+)?"
    r"(?>(?>der|des|den|die)\s+)?"
)
# fmt: on

split_citation_into_parts_pattern = regex.compile(
    split_citation_into_parts_pattern_str,
    flags=regex.IGNORECASE,
)

split_citation_into_range_parts_pattern = regex.compile(r"\s*,?\s+bis\s+")

split_unit_number_pattern_str = (
    r"\s|(?<=Art\.|Art\b|Artikeln|Artikel)(?=\d)|(?<=§)(?=[A-Z0-9])"
)
split_unit_number_pattern = regex.compile(
    split_unit_number_pattern_str, flags=regex.IGNORECASE
)
