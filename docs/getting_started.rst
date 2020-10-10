.. _getting_started:

===============
Getting Started
===============

------------
Installation
------------

You need to have python installed. Python 3.7 is recommended but other versions
will likely work as well.

Install with

::

    pip install quantlaw


--------------------------------------------------
Minimal example of the statute reference extractor
--------------------------------------------------

Below we provided a minimal example to use the statute extractor.


.. literalinclude:: ../example/example.py


To run it a text to analyze is required and in the example above imported from a file:


.. literalinclude:: ../example/paragraph_120_gvg.txt


Also a list of law names is required to identify laws.


.. literalinclude:: ../example/law_names.json
