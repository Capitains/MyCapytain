.. image:: https://travis-ci.org/Capitains/MyCapytain.svg?branch=master 
   :target: https://travis-ci.org/Capitains/MyCapytain
.. image:: https://coveralls.io/repos/Capitains/MyCapytain/badge.svg?branch=master 
   :target: https://coveralls.io/r/Capitains/MyCapytain?branch=master
.. image:: https://gemnasium.com/Capitains/MyCapytain.svg 
   :target: https://gemnasium.com/Capitains/MyCapytain
.. image:: https://badge.fury.io/py/MyCapytain.svg 
   :target: http://badge.fury.io/py/MyCapytain
.. image:: https://readthedocs.org/projects/mycapytain/badge/?version=latest
   :target: http://mycapytain.readthedocs.org
.. image:: https://zenodo.org/badge/3923/Capitains/MyCapytain.svg
   :target: https://zenodo.org/badge/latestdoi/3923/Capitains/MyCapytain
.. image:: https://img.shields.io/pypi/dm/MyCapytain.svg
   :target: https://pypi.python.org/pypi/MyCapytain
.. image:: https://api.codacy.com/project/badge/grade/8e63e69a94274422865e4f275dbf08ea
   :target: https://www.codacy.com/app/leponteineptique/MyCapytain


MyCapytain is a python library which provides a large set of methods to interact with Text Services API  such as the \
Canonical Text Services, the Distributed Text Services. It also provides a programming interface to exploit local \
textual resources developed according to the Capitains Guidelines.

Simple Example of what it does
##############################

The following code and example is badly displayed at the moment on Github. We recommend you to go to \
http://mycapytain.readthedocs.org

On Leipzig DH Chair's Canonical Text Services API, we can find the Epigrammata of Martial. This texts are identified \
by the identifier "urn:cts:latinLit:phi1294.phi002.perseus-lat2". We want to have some information about this text \
so we are gonna ask the API to give its metadata to us :

.. code-block:: python
   :linenos:
   :caption: example.py from the Github Repository

    from MyCapytain.resolvers.cts.api import HttpCtsResolver
    from MyCapytain.retrievers.cts5 import CTS
    from MyCapytain.common.constants import Mimetypes

    # We set up a resolver which communicates with an API available in Leipzig
    resolver = HttpCtsResolver(CTS("http://cts.dh.uni-leipzig.de/api/cts/"))
    # We require some metadata information
    textMetadata = resolver.getMetadata("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
    # Texts in CTS Metadata have one interesting property : its citation scheme.
    # XmlCtsCitation are embedded objects that carries information about how a text can be quoted, what depth it has
    print(type(textMetadata), [citation.name for citation in textMetadata.citation])

This query will return the following information :

.. code-block:: none

   <class 'MyCapytain.resources.collections.cts.Text'> ['book', 'poem', 'line']

.. code-block:: python
   :linenos:
   :lineno-start: 12

   # Now, we want to retrieve the first line of poem seventy two of the second book
   passage = resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="2.72.1")
   # And we want to have its content exported to plain text and have the siblings of this passage (previous and next line)
   print(passage.export(Mimetypes.PLAINTEXT), passage.siblingsId)

And we will get

.. code-block:: none

   Hesterna factum narratur, Postume, cena

If you want to play more with this, like having a list of what can be found in book three, you could go and do

.. code-block:: python
   :linenos:
   :lineno-start: 16

   poemsInBook3 = resolver.getReffs("urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="3")
   print(poemsInBook3)

Which would be equal to :

.. code-block:: none

   ['3.1', '3.2', '3.3', '3.4', '3.5', '3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12', '3.13', ...]

Now, it's your time to work with the resource ! See the CapiTainS Classes page on ReadTheDocs to have a general \
introduction to MyCapytain objects !

Installation and Requirements
#############################

The best way to install MyCapytain is to use pip. MyCapytain tries to support Python over 3.4.

The work needed for supporting Python 2.7 is mostly done, however, since 2.0.0, we are giving up on ensuring that \
MyCapytain will be compatible with Python < 3 while accepting PR which would help doing so.

.. code-block:: shell

   pip install MyCapytain

If you prefer to use setup.py, you should clone and use the following

.. code-block:: shell

   git clone https://github.com/Capitains/MyCapytain.git
   cd MyCapytain
   python setup.py install