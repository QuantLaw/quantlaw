import re


def stem_law_name(name):
    """
    Stems name of laws to prepare for recognizing laws in the code
    """
    result = re.sub(
        r"(?<!\b)(er|en|es|s|e)(?=\b)", "", name.strip(), flags=re.IGNORECASE
    )
    return clean_name(result)


def clean_name(name):
    result = re.sub(r"\s+", " ", name)
    return (
        result.replace("ß", "ss")
        .lower()
        .replace("ä", "ae")
        .replace("ü", "ue")
        .replace("ö", "oe")
    )
