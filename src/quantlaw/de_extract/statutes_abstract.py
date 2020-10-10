class StatusMatch:
    """
    Base class to report the areas of citations to German statutes and regulations
    (also if a trigger e.g. '§' is found but it is not followed by a citation).
    """

    def __init__(
        self,
        text: str,
        start: int,
        end: int,
    ):
        """
        Args:
            text: The text the match was found in.
            start: The position in the text where the trigger/main area starts
            end: The position where the trigger/main area ends.
        """
        self.text = text
        self.start = start
        self.end = end

    def has_main_area(self):
        """
        Returns True if the match has a main area and thus its content can be parsed by
        StatutesParser
        """
        return False

    def __str__(self):
        return f"Text:{self.text[self.start:self.end]};"


class StatutesMatchWithMainArea(StatusMatch):
    """
    Class to report the areas of citations to German statutes and regulations where a
    main area is found after the trigger "§ 123" where "123" is the main area.
    """

    def __init__(
        self,
        suffix_len: int,
        law_len: int,
        law_match_type: str,
        *args,
        **kwargs,
    ):
        """
        Args:
            suffix_len: Length of the suffix that may connect the main area of the
                citation to the name of the referenced law
            law_len: Length of the name of the referenced law
            law_match_type: Typ of the reference that depends on the law name.
                E.g. dict, internal, ignore, eu, sgb
            *args:
            **kwargs:
        """
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
    """
    Abstract class to extract and parse statute references.
    The abstract class provides the names of laws they are cited with.
    """

    def __init__(self, laws_lookup: dict):
        """
        Args:
            laws_lookup: See laws_lookup property for details.
        """
        self._laws_lookup = None
        self.laws_lookup_keys = None
        self.laws_lookup = laws_lookup

    @property
    def laws_lookup(self) -> dict:
        """
        A dictionary to find of the law names to extract.
        Keys are names of laws that are used in the source text used to cite
        laws. Values are unique identifiers of laws.
        For optimal results is is recommended to make the list a exhaustive as
        possible to reduce the chance that references are false treated as
        internal references within a law because the name of the referenced law
        is not recognized. The names of the laws should be provided in a
        stemmed format using the stemmer provided in
        `quantlaw.de_extract.stemming.stem_law_name`.
        """
        return self._laws_lookup

    @laws_lookup.setter
    def laws_lookup(self, val: dict):

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
