=========
Changelog
=========

Version 0.0.1
=============

- Initial version. Code used in Daniel Martin Katz, Corinna Coupette, Janis Beckedorf, and Dirk Hartung,
    Complex Societies and the Growth of the Law, *Sci. Rep.* **10** (2020), https://doi.org/10.1038/s41598-020-73623-x


Version 0.0.2
=============

- Add function to load German law names from https://github.com/QuantLaw/gesetze-im-internet
    that are required for parsing references
- Minor improvements to parse patterns
- Minor improvement to file utils: Results of list_dir are now sorted
- Add zenodo to readme


Version 0.0.3
=============

- Improve performance of networkx utilities


Version 0.0.4
=============

- Add load networkx graph from csv files

Version 0.0.5
=============

- Fix `load_graph_from_csv_files` (attributes evaluating to `False` are now imported)
- Enable edge filtering in `load_graph_from_csv_files` (e.g. to load reference edges or hierarchy edges only)

Version 0.0.6
=============

- Update readme

Version 0.0.7
=============

- Update readme
