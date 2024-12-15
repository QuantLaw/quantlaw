[![PyPI](https://img.shields.io/pypi/v/quantlaw)](https://pypi.org/project/quantlaw/)
[![Build Status](https://travis-ci.com/QuantLaw/quantlaw.svg?branch=master)](https://travis-ci.com/QuantLaw/quantlaw)
[![Maintainability](https://api.codeclimate.com/v1/badges/dabd1718d48dbf669d32/maintainability)](https://codeclimate.com/github/QuantLaw/quantlaw/maintainability)
[![codecov](https://codecov.io/gh/QuantLaw/quantlaw/branch/master/graph/badge.svg?token=XCLX5460R8)](https://codecov.io/gh/QuantLaw/quantlaw)
[![Documentation Status](https://readthedocs.org/projects/quantlaw/badge/?version=latest)](https://quantlaw.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.4079451.svg)](https://doi.org/10.5281/zenodo.4079451)

# quantlaw

This package contains coding utilities for quantitative legal studies.

## Modules

The package currently consists of two modules.

### de_extract

`quantlaw.de_extract` is an extractor for references to statutes in German legal texts.
In contrast to most other named entity recognition packages, this module not only
identifies the references but also extracts their content. This can, e.g., be used to
quantitatively analyze the structure of the law.

For example, we can extract the content of two references in the following text.

Source text:

"In den Fällen des **§ 111d Absatz 1 Satz 2** der *Strafprozessordnung* findet **§ 91**
der *Insolvenzordnung* keine Anwendung."

The extracted data would be:

1. `[[['§', '111d'], ['Abs', '1'], ['Satz', '2']]]` for the law `StPO`
2. `[[['§', '91']]]` for the law `InsO`

Getting started in the documentation contains a minimal example.

### utils

`quantlaw.utils` contains several utilities that are helpful to analyze the structure of
the law with `BeautifulSoup` and `networkx`. The documentation contains further
information about the individual usages.

## Installation

Python 3.7.9 is recommended. Our package is provided via `pip install quantlaw`.

## Related Projects and Publications

It is, inter alia, used to produce the results reported in the following publications:

- Daniel Martin Katz, Corinna Coupette, Janis Beckedorf, and Dirk Hartung, Complex Societies and the Growth of the Law, *Sci. Rep.* **10** (2020), [https://doi.org/10.1038/s41598-020-73623-x](https://doi.org/10.1038/s41598-020-73623-x)
- Corinna Coupette, Janis Beckedorf, Dirk Hartung, Michael Bommarito, and Daniel Martin Katz, Measuring Law Over Time, *Front. Phys.* **9:658463** (2021), https://doi.org/10.3389/fphy.2021.658463
- Corinna Coupette, and Dirk Hartung, Rechtsstrukturvergleichung, *RabelsZ* **86**, 935-975 (2022), https://doi.org/10.1628/rabelsz-2022-0082
- Corinna Coupette, Dirk Hartung, Janis Beckedorf, Maximilian Böther, and Daniel Martin Katz, Law Smells, *Artif Intell Law* **31**, 335-368 (2023), https://doi.org/10.1007/s10506-022-09315-w
- Janis Beckedorf, Komplexität des Rechts, Mohr Siebeck, to appear (2025), https://doi.org/10.1628/978-3-16-164476-4

Related Repositories:
- [Complex Societies and the Growth of the Law](https://github.com/QuantLaw/Complex-Societies-and-Growth) ([Publication Release](https://doi.org/10.5281/zenodo.4070769))
- [Measuring Law Over Time](https://github.com/QuantLaw/Measuring-Law-Over-Time) ([Publication Release](https://doi.org/10.5281/zenodo.4660191))
- [Law Smells](https://github.com/QuantLaw/law-smells) ([Publication Release](https://doi.org/10.5281/zenodo.6468193))
- [Komplexität des Rechts](https://github.com/beckedorf/komplexitaet-des-rechts) ([Publication Release](https://doi.org/10.1628/978-3-16-164476-4-appendix))
- [Legal Data Preprocessing](https://github.com/QuantLaw/legal-data-preprocessing) ([Latest Publication Release](https://doi.org/10.5281/zenodo.4070772))
- [Legal Data Clustering](https://github.com/QuantLaw/legal-data-clustering) ([Latest Publication Release](https://doi.org/10.5281/zenodo.4070774))

Related Data: 
- [Preprocessed Input Data for *Sci. Rep.* **10** (2020)](https://doi.org/10.5281/zenodo.4070767)
- [Preprocessed Input Data for *Measuring Law Over Time*, *Front. Phys.* **9:658463** (2021)](https://doi.org/10.5281/zenodo.4660133)
- [Preprocessed Input Data for *Komplexität des Rechts*, Mohr Siebeck, to appear (2025)](https://doi.org/10.1628/978-3-16-164476-4-appendix)
- [Preprocessed Input Data for *Law Smells*, *Artif Intell Law* **31**, 335–368 (2023)](https://doi.org/10.5281/zenodo.6468191)

## Collaboration

Please format the code using `isort`, `black`, and `flake8`. A convenient option to
ensure correct formatting of the code is to
[pip install pre-commit](https://pypi.org/project/pre-commit/) and run
`pre-commit install` to add code checking and reformatting as git pre-commit hook.
