MyCapytain

[![Build Status](https://travis-ci.org/Capitains/MyCapytain.svg)](https://travis-ci.org/Capitains/MyCapytain)
[![Coverage Status](https://coveralls.io/repos/Capitains/MyCapytain/badge.svg?branch=master)](https://coveralls.io/r/Capitains/MyCapytain?branch=master)
[![Dependency Status](https://gemnasium.com/Capitains/MyCapytain.svg)](https://gemnasium.com/Capitains/MyCapytain)
[![PyPI version](https://badge.fury.io/py/MyCapytain.svg)](http://badge.fury.io/py/MyCapytain)
[![Documentation Status](https://readthedocs.org/projects/mycapytain/badge/?version=latest)](https://readthedocs.org/projects/mycapytain/?badge=latest)
[![DOI](https://zenodo.org/badge/3923/Capitains/MyCapytain.svg)](https://zenodo.org/badge/latestdoi/3923/Capitains/MyCapytain)

MyCapytain is a python package which provides a large set of tools to deal with CTS and Capitains Guidelines in Python.


## Known issues and recommendations

- lxml, which is the package powering xml support here, does not accept XPath notations such as `/div/(a or b)[@n]`.
    - Solution for this edge case is `/div/*[self::a or self::b][@n]`