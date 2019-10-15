from typing import Union
from MyCapytain.common.reference import URN, BaseReferenceSet, BaseReference
from MyCapytain.common.constants import RDF_NAMESPACES
from ..metadata import Collection
from rdflib import Literal

from .inventory import CtsTextMetadata
from ..text import InteractiveTextualNode


__all__ = [
    "PrototypeCtsNode",
    "PrototypeCtsText",
    "PrototypeCtsPassage"
]


class PrototypeCtsNode(InteractiveTextualNode):
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

    def __init__(self, urn: Union[URN, str] = None, **kwargs):
        super(PrototypeCtsNode, self).__init__(identifier=str(urn), **kwargs)
        self._urn = None

        if urn is not None:
            self.urn = urn

    @property
    def urn(self) -> URN:
        """ URN Identifier of the object

        """
        return self._urn

    @urn.setter
    def urn(self, value: Union[URN, str]):
        """ Set the urn

        :param value: URN to be saved
        :raises: *TypeError* when the value is not URN compatible

        """
        if isinstance(value, str):
            value = URN(value)
        elif not isinstance(value, URN):
            raise TypeError("New urn must be string or {} instead of {}".format(type(URN), type(value)))
        self._urn = value

    def get_cts_metadata(self, key: str, lang: str = None) -> Literal:
        """ Get easily a metadata from the CTS namespace

        :param key: CTS property to retrieve
        :param lang: Language in which it should be
        :return: Literal value of the CTS graph property
        """
        return self.metadata.get_single(RDF_NAMESPACES.CTS.term(key), lang)

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

    def set_metadata_from_collection(self, text_metadata: CtsTextMetadata):
        """ Set the object metadata using its collections recursively

        :param text_metadata: Object representing the current text as a collection
        :type text_metadata: CtsTextMetadata
        """
        edition, work, textgroup = tuple(([text_metadata] + text_metadata.parents)[:3])

        for node in textgroup.metadata.get(RDF_NAMESPACES.CTS.groupname):
            lang = node.language
            self.metadata.add(RDF_NAMESPACES.CTS.groupname, lang=lang, value=str(node))
            self.set_creator(str(node), lang)

        for node in work.metadata.get(RDF_NAMESPACES.CTS.title):
            lang = node.language
            self.metadata.add(RDF_NAMESPACES.CTS.title, lang=lang, value=str(node))
            self.set_title(str(node), lang)

        for node in edition.metadata.get(RDF_NAMESPACES.CTS.label):
            lang = node.language
            self.metadata.add(RDF_NAMESPACES.CTS.label, lang=lang, value=str(node))
            self.set_subject(str(node), lang)

        for node in edition.metadata.get(RDF_NAMESPACES.CTS.description):
            lang = node.language
            self.metadata.add(RDF_NAMESPACES.CTS.description, lang=lang, value=str(node))
            self.set_description(str(node), lang)

        if not self.citation.is_set() and edition.citation.is_set():
            self.citation = edition.citation


class PrototypeCtsPassage(PrototypeCtsNode):
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
        super(PrototypeCtsPassage, self).__init__(**kwargs)

    @property
    def reference(self) -> BaseReference:
        return self.urn.reference


class PrototypeCtsText(PrototypeCtsNode):
    """ A CTS CtsText
    """

    def __init__(self, citation=None, metadata=None, **kwargs):
        super(PrototypeCtsText, self).__init__(citation=citation, metadata=metadata, **kwargs)
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
