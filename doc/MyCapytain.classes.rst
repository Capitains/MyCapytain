MyCapytain's Main Objects Explained
===================================

.. toctree::
   :maxdepth: 2

Retrievers
##########

Description
***********

Retrievers are classes that help build requests to API and return standardized responses from them. There is no real \
perfect prototypes. The only requirements for a Retriever is that its query function should returns string only. It is \
not the role of the retrievers to parse response. It is merely to facilitate the communication to remote API most of \
the time.

Recommendations
***************

For Textual API, it is recommended to implement the following requests

- getTextualNode(textId[str], subreference[str], prevnext[bool], metadata[bool])
- getMetadata(objectId[str], \*\*kwargs)
- getSiblings(textId[str], subreference[str])
- getReffs(textId[str], subreference[str], depth[int])


Example of implementation : CTS 5
*********************************

.. code-block:: python
    :linenos:
    :caption: Retrieving a CTS API Reply

    from MyCapytain.retrievers.cts5 import CTS

    # We set up a retriever which communicates with an API available in Leipzig
    retriever = CTS("http://cts.dh.uni-leipzig.de/api/cts/")
    # We require a passage : passage is now a Passage object
    passage = retriever.getPassage("urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
    # Passage is now equal to the string content of http://cts.dh.uni-leipzig.de/api/cts/?request=GetPassage&urn=urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1
    print(passage)


Text and Passages
#################

Needs to be written


Collection
##########

CTS Collections
***************

Needs to be written

Resolvers
#########

Description
***********

Resolvers were introduced in 2.0.0b0 and came as a solution to build tools around Text Services APIs where you \
can seamlessly switch a resolver for another and not changing your code, join together multiple resolvers, etc. \
The principle behind resolver is to provide native python object based on API-Like methods which are restricted to \
four simple commands :

- getTextualNode(textId[str], subreference[str], prevnext[bool], metadata[bool]) -> Passage
- getMetadata(objectId[str], \*\*kwargs) -> Collection
- getSiblings(textId[str], subreference[str]) -> tuple([str, str])
- getReffs(textId[str], subreference[str], depth[int]) -> list([str])

These function will always return objects derived from the major classes, *i.e.* Passage and Collection for the two \
firsts and simple collections of strings for the two others. Resolvers fills the hole between these base objects \
and the original retriever objects that were designed to return plain strings from remote or local APIs.

The base functions are represented in the prototype, and only getMetadata might be expanded in terms of arguments \
depending on what filtering can be offered. Though, any additional filter has not necessarily effects with other \
resolvers.

Historical Perspective
**********************

The original incentive to build resolvers was the situation with retrievers, in the context of the Nautilus \
API and Nemo UI : Nemo took a retriever as object, which means that, based on the prototype, Nemo was retrieving \
string objects. That made sense as long as Nemo was running with HTTP remote API because it was actually receiving \
string objects which were not even (pre-)processed by the Retriever object. But since Nautilus was developed (a \
fully native python CTS API), we had the situation where Nemo was parsing strings that were exported from python \
etree objects by Nautilus which parsed strings.

.. image:: _static/images/Resolvers.Before.svg
    :target: _static/images/Resolvers.Before.dia
    :alt: Diagram of operations before resolvers : there is duplication of processing

Introducing Resolvers, we managed to avoid this double parsing effect in any situation : MyCapytain now provides a \
default class to provide access to querying text no matter what kind of transactions there is behind the Python \
object. At the same time, Resolvers provide a now unified system to retrieve texts independently from the retriever\
standard type (CTS, DTS, Proprietary, etc.).


.. image:: _static/images/Resolvers.After.svg
    :target: _static/images/Resolvers.After.dia
    :alt: Diagram of operations with resolvers : duplicated steps have been removed


Prototype
*********

.. autoclass:: MyCapytain.resolvers.prototypes.Resolver
    :members:

Example
*******

.. code-block:: python
    :linenos:
    :caption: Retrieving a passage and manipulating it

    from MyCapytain.resolvers.cts.api import HttpCTSResolver
    from MyCapytain.retrievers.cts5 import CTS
    from MyCapytain.common.utils import Mimetypes, NS

    # We set up a resolver which communicates with an API available in Leipzig
    resolver = HttpCTSResolver(CTS("http://cts.dh.uni-leipzig.de/api/cts/"))
    # We require a passage : passage is now a Passage object
    # This is an entry from the Smith Myth Dictionary
    # The inner methods will resolve to the URI http://cts.dh.uni-leipzig.de/api/cts/?request=GetPassage&urn=urn:cts:pdlrefwk:viaf88890045.003.perseus-eng1:A.abaeus_1
    # And parse it into interactive objects
    passage = resolver.getTextualNode("urn:cts:pdlrefwk:viaf88890045.003.perseus-eng1", "A.abaeus_1")
    # We need an export as plaintext
    print(passage.export(
        output=Mimetypes.PLAINTEXT
    ))
    """
        Abaeus ( Ἀβαῖος ), a surname of Apollo
         derived from the town of Abae in Phocis, where the god had a rich temple. (Hesych. s. v.
         Ἄβαι ; Hdt. 8.33 ; Paus. 10.35.1 , &c.) [ L.S ]
    """
    # We want to find bibliographic information in the passage of this dictionary
    # We need an export as LXML ETREE object to perform XPath
    print(
        passage.export(
            output=Mimetypes.PYTHON.ETREE
        ).xpath(".//tei:bibl/text()", namespaces=NS, magic_string=False)
    )
    ["Hdt. 8.33", "Paus. 10.35.1"]