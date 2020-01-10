from typing import Union
from MyCapytain.common.reference import URN, BaseReferenceSet, BaseReference
from MyCapytain.common.constants import RDF_NAMESPACES
from ..metadata import Collection
from rdflib import Literal
from collections import defaultdict

from .collection import CapitainsReadableMetadata
from ..text import InteractiveTextualNode


__all__ = [
    "PrototypeCapitainsNode",
    "PrototypeCapitainsText",
    "PrototypeCapitainsPassage"
]


class PrototypeCapitainsNode(InteractiveTextualNode):
    """ Initiate a Resource object

    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference._capitains_cts.URN
    :param metadata: Collection Information about the Item
    :type metadata: Collection
    :param citation: XmlCtsCitation system of the text
    :type citation: Citation
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    :param resource: Resource used to navigate through the textual graph

    :cvar default_exclude: Default exclude for exports
    """

    @property
    def urn(self) -> str:
        """ Kept for backward compatibility

        """
        return self.id

    def get_capitains_metadata(self, key: str, lang: str = None) -> Union[dict, list]:
        """ Get easily a metadata from the CAPITAINS namespace

        :param key: CAPITAINS property to retrieve
        :param lang: Language in which it should be
        :return: Dictionary in form {lang: [Literal]} if 'lang' is None else a list in form [Literal]
        """
        x = defaultdict(list)
        for obj in self.metadata.get(RDF_NAMESPACES.CAPITAINS.term(key)):
            x[getattr(obj, 'language', "")].append(obj)
        if lang is not None:
            if lang in x:
                return x[lang]
            return next(iter(x.values()))
        return x

    def getValidReff(self, level: int = 1, reference: BaseReference = None) -> BaseReferenceSet:
        """ Given a resource, CtsText will compute valid reffs

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :param reference: Subreference (optional)
        :returns: List of levels
        """
        raise NotImplementedError()

    def getLabel(self) -> Collection:
        """ Retrieve metadata about the text

        :rtype: Collection
        :returns: Retrieve Label informations in a Collection format
        """
        raise NotImplementedError()

    def set_metadata_from_collection(self, text_metadata: CapitainsReadableMetadata):
        """ Set the object metadata using its collections recursively

        :param text_metadata: Object representing the current text as a collection
        :type text_metadata: CapitainsReadableMetadata
        """
        for p, o in text_metadata.graph.predicate_objects(text_metadata.asNode()):
            self.metadata.add(p, lang=getattr(o, 'language', None), value=o)


class PrototypeCapitainsPassage(PrototypeCapitainsNode):
    """ CapitainsCtsPassage objects possess metadata informations

    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference._capitains_cts.URN
    :param metadata: Collection Information about the Item
    :type metadata: Collection
    :param citation: XmlCtsCitation system of the text
    :type citation: Citation
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    :param resource: Resource used to navigate through the textual graph

    :cvar default_exclude: Default exclude for exports
    """

    def __init__(self, **kwargs):
        super(PrototypeCapitainsPassage, self).__init__(**kwargs)

    @property
    def reference(self) -> BaseReference:
        """ Can we make any assumptions about where the citation reference portion of a passage ID can be found?"""
        raise NotImplementedError()


class PrototypeCapitainsText(PrototypeCapitainsNode):
    """ A CTS CtsText
    """

    def __init__(self, citation=None, metadata=None, **kwargs):
        super(PrototypeCapitainsText, self).__init__(citation=citation, metadata=metadata, **kwargs)
        self._cts = None

    @property
    def reffs(self) -> BaseReferenceSet:
        """ Get all valid reffs for every part of the CtsText

        :rtype: [str]
        """
        if not self._cts:
            self._cts = BaseReferenceSet(
                [reff for reffs in [self.getReffs(level=i) for i in range(1, len(self.citation) + 1)] for reff in reffs]
            )
        return self._cts
