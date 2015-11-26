.. image:: https://travis-ci.org/Capitains/MyCapytain.svg?branch=master 
   :target: https://travis-ci.org/Capitains/MyCapytain
.. image:: https://coveralls.io/repos/Capitains/MyCapytain/badge.svg?branch=master 
   :target: https://coveralls.io/r/Capitains/MyCapytain?branch=master
.. image:: https://gemnasium.com/Capitains/MyCapytain.svg 
   :target: https://gemnasium.com/Capitains/MyCapytain
.. image:: https://badge.fury.io/py/MyCapytain.svg 
   :target: http://badge.fury.io/py/MyCapytain
.. image:: https://readthedocs.org/projects/mycapytain/badge/?version=latest
   :target: https://readthedocs.org/projects/mycapytain/badge/?version=latest
.. image:: https://zenodo.org/badge/3923/Capitains/MyCapytain.svg
   :target: https://zenodo.org/badge/latestdoi/3923/Capitains/MyCapytain

MyCapytain is a python package which provides a large set of tools to deal with CTS and Capitains Guidelines in Python.

Installation and Requirements
#############################

The best way to install MyCapytain is to use pip. MyCapytain tries to support both Python 2.7 and Python 3.4.

.. code-block:: shell

   pip install MyCapytain

If you prefer to use setup.py, you should clone and use the following

.. code-block:: shell

   git clone https://github.com/Capitains/MyCapytain.git
   cd MyCapytain
   python setup.py install


Known issues and recommendations
################################
- lxml, which is the package powering xml support here, does not accept XPath notations such as `/div/(a or b)[@n]`.
    - Solution for this edge case is `/div/*[self::a or self::b][@n]`