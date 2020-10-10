import json

from quantlaw.de_extract.statutes_areas import StatutesExtractor
from quantlaw.de_extract.statutes_parse import StatutesParser
from quantlaw.de_extract.stemming import stem_law_name

# Load test that will be analyzed
with open("paragraph_120_gvg.txt", encoding="utf8") as f:
    text = f.read()

# Load a list of law names
with open("law_names.json", encoding="utf8") as f:
    law_names_raw = json.load(f)

# Stem law names and also allow discovery by abbreviations
law_names = {}

for law_name, law_abbreviation in law_names_raw.items():
    law_names[stem_law_name(law_name)] = law_abbreviation
    law_names[stem_law_name(law_abbreviation)] = law_abbreviation

# Instantiate extractor
extractor = StatutesExtractor(laws_lookup=law_names)

# Extract areas
matches = list(extractor.find_all(text))

# Instantiate parser
parser = StatutesParser(law_names)

# Parse each reference
for match in matches:
    if match.has_main_area():
        main_area_data = parser.parse_main(match.main_text())
        law_name_area_data = parser.parse_law(
            match.law_text(), match.law_match_type, current_lawid="GVG"
        )
        print(main_area_data, "-", law_name_area_data)
