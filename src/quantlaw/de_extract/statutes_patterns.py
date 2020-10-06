from regex import regex

# fmt: off


reference_range_pattern_str = (
    r'(?(DEFINE)'
        r'(?<numb>'
            r'('
                r'\d+(?>\.\d+)*[a-z]?|'
                r'[ivx]+|'
                r'[a-z]\)?'
            r')'
            r'(\s?ff?\.|\s?ff\b|\b)'
        r')'
        r'(?<wordnumb>('
            r'erste|'
            r'zweite|'
            r'dritte|'
            r'letzte'
        r')r?s?)'
        r'(?<unit>'
            r'\bArt\b\.?|'
            r'Artikels?n?|'
            r'§{1,2}|'
            r'Nrn?\b\.?|'
            r'Nummer|'
            r'Abs\b\.?|'
            r'Absatz|'
            r'Absätze|'
            r'Unterabsatz|'
            r'Unterabs\b\.?|'
            r'S\b\.?|'
            r'Satz|'
            r'Sätze|'
            r'Ziffern?|'
            r'Ziffn?\b\.?|'
            r'Buchstaben?|'  # Doppelbuchstabe and  DBuchst. missing (Problem in numb)
            r'Buchst\b\.?|'
            r'Halbsatz|'
            r'Teilsatz|'
            r'Abschnitte?|'
            r'Abschn\b\.?|'
            r'Alternativen?|'
            r'Alt\b\.?|'
            r'Anhang|'
            r'Anhänge'
        r')'
        r'(?<conn>,?'
            r'(?>'
                r',\s*|'
                r'\s+und\s+|'
                r'\s+sowie\s+|'
                r'\s+bis\s+|'
                r'\s+oder\s+|'
                    r'(?>\s+jeweils)?'
                    r'(?>\s+auch)?\s+'
                    r'(?>in\s+Verbindung\s+mit|i\.?\s?V\.?\s?m\.?)\s+'
            r')'
            r'(?>nach\s+)?'
            r'(?>(?>der|des|den|die)\s+)?'
        r')'
    r')'  # end DEFINE
    r'(?P<trigger>'
        r'('
            r'§{1,2}|'
            r'\bArt\b\.?|'
            r'Artikels?n?'
        r')\s*'
    r')'
    r'(?P<main>'
        r'(?&numb)'
        r'('
            r'\s*'
            r'('
                r'('
                    r'(?&conn)(?&unit)\s|'
                    r'(?&conn)|'
                    r'(?&unit)\s'
                r')'
                r'(?&numb)'
            r'|'
                r'(?&conn)?'
                r'(?&wordnumb)'
                r'\s+'
                r'(?&unit)'
            r')'
        r')*'
    r')?'
)


# fmt: on


reference_range_pattern = regex.compile(
    reference_range_pattern_str, flags=regex.IGNORECASE
)


# fmt: off


suffix_ignore_pattern_str = (
    r'^('
        r'(Gesetzes|Anordnung) vom \d+. \w+ \d+ \(BGBl\. I S\. \d+\)|'
        r'(G|AnO) v\. \d+\.\s?\d+\.\s?\d+ I+ \d+'
        r'|'
            r'(saarländischen )?Gesetzes Nr\. \d+ ?'
            r'[\w\s\-äöüÄÖÜ]{0,120} vom \d+. \w+ \d+ '
            r'\(Amtsblatt des Saarlande?s S\. \d+\)'
        r'|'
            r'(([\w\-äöüÄÖÜß]+|\d+\.) ){0,5}'
            r'(Durchführungs)?verordnung zum [\w-äöüÄÖÜß]+gesetz'
            r'(( in der Fassung der Bekanntmachung)? vom \d+. \w+ \d+ \(.{8,50}\))?'
        r'|'
            r'([\w\-äöüÄÖÜß]{1,60}\s|\d+\.\s|Nr\.\s){0,8}?'
            r'[\w\-äöüÄÖÜß]{3,60}'
            r'(?<!\bver)(ordnung|gesetz|gesetze?s?buch|übereinkommen|statut|vertrag)'
            r'(er|en|es|s)?(?=\b)'
            r'(?! zum)( (von )?[\d/]+)?(( in der Fassung)?( der Bekanntmachung)? '
            r'vom \d+. \w+ \d+ \(.{8,50}\))?'
        r'|'
        r'[\w-äöüÄÖÜß]*tarifvertr(a|ä)ge?s?|'
        r'(abgelösten )?TV\s\w+|'
        r'Anlage\b|'
        r'('
            r'[\wäöüÄÖÜß]+\s)?[\wäöüÄÖÜß]*('
                r'Gesetz|'
                r'Übereinkommen|'
                r'vereinbarung|'
                r'verordnung|'
                r'Abkommens|'
                r'Vertrag|'
                r'Konvention|'
                r'Protokoll|'
                r'Anordnung|'
                r'Satzung|'
                r'bestimmung|'
                r'Verfassung'
            r')e?s?n?\s\s?'
            r'(zur|über|vom|zum|zu dem|von|zwischen|des|der|betreffend)'
        r'|'
        r'[\wäöüÄÖÜß]*-(vertrag|abkommen)e?s?'
        r'|'
            r'(in\s(?!Artikels?n?)[\w\s\.]{2,100}?\s)?'
            r'(vor)?(genannten|bezeichneten)\s'
            r'\w*(Verordnung|Gesetz)e?s?n?|'
        r'in\s(?='
            r'(Art|§)[\w\s\.§]{2,100}?\s'
            r'(vor)?(genannten|bezeichneten)\s'
            r'\w*(Verordnung|Gesetz)e?s?n?)'
            # Similiar to pattern above,
            # but stops before next reference trigger (Art...|§)
    r')'
)


# fmt: on


suffix_ignore_pattern = regex.compile(suffix_ignore_pattern_str, flags=regex.IGNORECASE)
