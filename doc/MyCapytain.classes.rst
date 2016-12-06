MyCapytain's Objects Explained
==============================

Resolvers
#########

Description
***********

Resolvers were introduced in 2.0.0b0 and came as a solution to build tools around Text Services APIs where you \
can seamlessly switch a resolver for another and not changing your code, join together multiple resolvers, etc. \
The principle behind resolver is to provide native python object based on API-Like methods which are restricted to \
four simple commands :

- getPassage
- getMetadata
- getSiblings
- getReffs

These function will always return objects derived from the major classes, *i.e.* Passage and Collection for the two \
firsts and simple collections of strings for the two others. Resolvers fills the hole between these base objects \
and the original retriever objects that were designed to return plain strings from remote or local APIs.

The base functions are represented in the prototype, and only getMetadata might be expanded in terms of arguments \
depending on what filtering can be offered. Though, any additional filter has not necessarily effects with other \
resolvers.

A point of history
******************

The original incentive to build resolvers was the situation with retrievers, in the context of the Nautilus \
    API and Nemo UI : Nemo took a retriever as object, which means that, based on the prototype, Nemo was retrieving \
    string objects. That made sense as long as Nemo was running with HTTP remote API because it was actually receiving \
    string objects which were not even (pre-)processed by the Retriever object. But since Nautilus was developed (a \
    fully native python CTS API), we had the situation where Nemo was parsing strings that were exported from python \
    etree objects by Nautilus which parsed strings.

.. image:: doc/_static/images/Resolvers.Before.svg
    :target: doc/_static/images/Resolvers.Before.dia
    :alt: Diagram of operations before resolvers : there is duplication of processing

Introducing Resolvers, we managed to avoid this double parsing effect in any situation : MyCapytain now provides a \
    default class to provide access to querying text no matter what kind of transactions there is behind the Python \
    object. At the same time, Resolvers provide a now unified system to retrieve texts independently from the retriever\
    standard type (CTS, DTS, Proprietary, etc.).


.. image:: _static/images/Resolvers.After.svg
    :target: _static/images/Resolvers.After.dia
    :alt: Diagram of operations with resolvers : duplicated steps have been removed


Trait
*****

.. autoclass:: MyCapytain.resolvers.prototypes.Resolver
    :members:

Example
*******

.. code-block:: python
    :linenos:
    :caption: Retrieving a passage and manipulating it

    from MyCapytain.resolvers.cts.api import HttpCTSResolver
    from MyCapytain.retrievers.cts5 import CTS
    from MyCapytain.common.utils import Mimetypes

    # We set up a resolver which communicates with an API available in Leipzig
    resolver = HttpCTSResolver(CTS("http://cts.dh.uni-leipzig.de/api/cts/"))
    # We require a passage : passage is now a Passage object
    passage = resolver.getPassage("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.1")
    # We need an export as plaintext
    print(passage.export(
        output=Mimetypes.PLAINTEXT
    ))
    """
        I
        Hic est quem legis ille, quem requiris,
        Toto notus in orbe Martialis
        Argutis epigrammaton libellis:
        Cui, lector studiose, quod dedisti
        Viventi decus atque sentienti,
        Rari post cineres habent poetae.
    """
    # We need an export as LXML ETREE object to perform XPath
    print(
        passage.export(
            output=Mimetypes.PYTHON.ETREE
        ).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False)
    )
    ["Hic est quem legis ille, quem requiris, "]