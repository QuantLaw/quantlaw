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
Different to most other Named-entity recognition packages this module does not only
identifies the references but also extracts its content. This can e.g. be used to
quantitativly analyze the structure of the law.

For example can the content of two references in the following text be extracted.

Source text:

"In den Fällen des **§ 111d Absatz 1 Satz 2** der *Strafprozessordnung* findet **§ 91**
der *Insolvenzordnung* keine Anwendung."

The extracted data would be:

1. `[[['§', '111d'], ['Abs', '1'], ['Satz', '2']]]` for the law `StPO`
2. `[[['§', '91']]]` for the law `InsO`

Getting started in the documentation contains a minimal example.

### utils

`quantlaw.utils` contains several utilities that are helpful to analyze the structure of
the law with `BeautifulSoup` and `networkx`. The documentation contains furhter
information about the individual usages.

## Installation

Python 3.7 is recommended. Our package is provided via `pip install quantlaw`.

## Further repositories

It is, inter alia, used to produce the results reported in the following publication:

Daniel Martin Katz, Corinna Coupette, Janis Beckedorf, and Dirk Hartung, Complex Societies and the Growth of the Law, *Sci. Rep.* **10** (2020), [https://doi.org/10.1038/s41598-020-73623-x](https://doi.org/10.1038/s41598-020-73623-x)

Related Repositories:
- [Complex Societies and the Growth of the Law](https://github.com/QuantLaw/Complex-Societies-and-Growth) ([First Publication Release](http://dx.doi.org/10.5281/zenodo.4070769))
- [Legal Data Clustering](https://github.com/QuantLaw/legal-data-clustering) ([First Publication Release](http://dx.doi.org/10.5281/zenodo.4070775))

Related Data: [Preprocessed Input Data for *Sci. Rep.* **10** (2020)](http://dx.doi.org/10.5281/zenodo.4070767)

## Collaboration

Please format the code using `isort`, `black`, and `flake8`. An convenient option to
ensure correct formatting of the code is to
[pip install pre-commit](https://pypi.org/project/pre-commit/) and run
`pre-commit install` to add code checking and reformatting as git pre-commit hook.
