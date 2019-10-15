# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.texts.remote.cts
   :synopsis: CtsTextMetadata and CapitainsCtsPassage implementation for dealing with CTS API Responses

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from __future__ import unicode_literals

from MyCapytain.common.metadata import Metadata
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.common.constants import XPATH_NAMESPACES, Mimetypes, RDF_NAMESPACES
from MyCapytain.common.reference import CtsReference, URN
from MyCapytain.resources.collections import cts as CtsCollection
from MyCapytain.resources.prototypes.text import InteractiveTextualNode
from MyCapytain.resources.prototypes.cts.text import PrototypeCtsText, PrototypeCtsPassage
from MyCapytain.resources.texts.base.tei import TeiResource
from MyCapytain.errors import MissingAttribute


__all__ = [
    "CtsPassage",
    "CtsText"
]


class _SharedMethod(InteractiveTextualNode):
    """ Set of methods shared by CtsTextMetadata and CapitainsCtsPassage

    :param retriever: Retriever used to retrieve other data
    :type retriever: MyCapytain.retrievers.PrototypeCitableTextServiceRetriever
    """

    @property
    def depth(self):
        """ Depth of the current opbject

        :return: Int representation of the depth based on URN information
        :rtype: int
        """
        if self.urn.reference:
            return self.urn.reference.depth

    def __init__(self, retriever=None, *args, **kwargs):
        super(_SharedMethod, self).__init__(*args, **kwargs)
        self._retriever = retriever
        self._first = False
        self._last = False
        if retriever is None:
            raise MissingAttribute("Object has not retriever")

    @property
    def retriever(self):
        """ Retriever object used to query for more data

        :rtype: CitableTextServiceRetriever
        """
        return self._retriever

    def getValidReff(self, level=1, reference=None):
        """ Given a resource, CtsText will compute valid reffs

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param reference: CapitainsCtsPassage reference
        :type reference: CtsReference
        :rtype: list(str)
        :returns: List of levels
        """
        if reference:
            urn = "{0}:{1}".format(self.urn, reference)
        else:
            urn = str(self.urn)

        if level == -1:
            level = len(self.citation)

        xml = self.retriever.getValidReff(
            level=level,
            urn=urn
        )
        xml = xmlparser(xml)
        self._parse_request(xml.xpath("//ti:request", namespaces=XPATH_NAMESPACES)[0])

        return [ref.split(":")[-1] for ref in xml.xpath("//ti:reply//ti:urn/text()", namespaces=XPATH_NAMESPACES)]

    def getTextualNode(self, subreference=None):
        """ Retrieve a passage and store it in the object

        :param subreference: CtsReference of the passage (Note : if given a list, this should be a list of string that \
        compose the reference)
        :type subreference: Union[CtsReference, URN, str, list]
        :rtype: CtsPassage
        :returns: Object representing the passage
        :raises: *TypeError* when reference is not a list or a CtsReference
        """
        if isinstance(subreference, URN):
            urn = str(subreference)
        elif isinstance(subreference, CtsReference):
            urn = "{0}:{1}".format(self.urn, str(subreference))
        elif isinstance(subreference, str):
            if ":" in subreference:
                urn = subreference
            else:
                urn = "{0}:{1}".format(self.urn.upTo(URN.NO_PASSAGE), subreference)
        elif isinstance(subreference, list):
            urn = "{0}:{1}".format(self.urn, ".".join(subreference))
        else:
            urn = str(self.urn)

        response = xmlparser(self.retriever.getPassage(urn=urn))

        self._parse_request(response.xpath("//ti:request", namespaces=XPATH_NAMESPACES)[0])
        return CtsPassage(urn=urn, resource=response, retriever=self.retriever)

    def getReffs(self, level=1, subreference=None):
        """ Reference available at a given level

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param subreference: Subreference (optional)
        :type subreference: CtsReference
        :rtype: [text_type]
        :returns: List of levels
        """
        if self.depth is not None:
            level += self.depth

        return self.getValidReff(level, subreference)

    def getPassagePlus(self, reference=None):
        """ Retrieve a passage and informations around it and store it in the object

        :param reference: Reference of the passage
        :type reference: CtsReference or List of text_type
        :rtype: CtsPassage
        :returns: Object representing the passage
        :raises: *TypeError* when reference is not a list or a Reference
        """
        if reference:
            urn = "{0}:{1}".format(self.urn, reference)
        else:
            urn = str(self.urn)

        response = xmlparser(self.retriever.getPassagePlus(urn=urn))

        passage = CtsPassage(urn=urn, resource=response, retriever=self.retriever)
        passage._parse_request(response.xpath("//ti:reply/ti:label", namespaces=XPATH_NAMESPACES)[0])
        self.citation = passage.citation
        return passage

    def _parse_request(self, xml):
        """ Parse a request with metadata information

        :param xml: LXML Object
        :type xml: Union[lxml.etree._Element]
        """
        for node in xml.xpath(".//ti:groupname", namespaces=XPATH_NAMESPACES):
            lang = node.get("xml:lang") or CtsText.DEFAULT_LANG
            self.metadata.add(RDF_NAMESPACES.CTS.groupname, lang=lang, value=node.text)
            self.set_creator(node.text, lang)

        for node in xml.xpath(".//ti:title", namespaces=XPATH_NAMESPACES):
            lang = node.get("xml:lang") or CtsText.DEFAULT_LANG
            self.metadata.add(RDF_NAMESPACES.CTS.title, lang=lang, value=node.text)
            self.set_title(node.text, lang)

        for node in xml.xpath(".//ti:label", namespaces=XPATH_NAMESPACES):
            lang = node.get("xml:lang") or CtsText.DEFAULT_LANG
            self.metadata.add(RDF_NAMESPACES.CTS.label, lang=lang, value=node.text)
            self.set_subject(node.text, lang)

        for node in xml.xpath(".//ti:description", namespaces=XPATH_NAMESPACES):
            lang = node.get("xml:lang") or CtsText.DEFAULT_LANG
            self.metadata.add(RDF_NAMESPACES.CTS.description, lang=lang, value=node.text)
            self.set_description(node.text, lang)

        # Need to code that p
        if not self.citation.is_set() and xml.xpath("//ti:citation", namespaces=XPATH_NAMESPACES):
            self.citation = CtsCollection.XmlCtsCitation.ingest(
                xml,
                xpath=".//ti:citation[not(ancestor::ti:citation)]"
            )

    def getLabel(self):
        """ Retrieve metadata about the text

        :rtype: Metadata
        :returns: Dictionary with label informations
        """
        response = xmlparser(
            self.retriever.getLabel(urn=str(self.urn))
        )

        self._parse_request(
            response.xpath("//ti:reply/ti:label", namespaces=XPATH_NAMESPACES)[0]
        )

        return self.metadata

    def getPrevNextUrn(self, reference):
        """ Get the previous URN of a reference of the text

        :param reference: CtsReference from which to find siblings
        :type reference: Union[CtsReference, str]
        :return: (Previous CapitainsCtsPassage CtsReference,Next CapitainsCtsPassage CtsReference)
        """
        _prev, _next = _SharedMethod.prevnext(
            self.retriever.getPrevNextUrn(
                urn="{}:{}".format(
                    str(
                        URN(
                            str(self.urn)).upTo(URN.NO_PASSAGE)
                    ),
                    str(reference)
                )
            )
        )
        return _prev, _next

    def getFirstUrn(self, reference=None):
        """ Get the first children URN for a given resource

        :param reference: CtsReference from which to find child (If None, find first reference)
        :type reference: CtsReference, str
        :return: Children URN
        :rtype: URN
        """
        if reference is not None:
            if ":" in reference:
                urn = reference
            else:
                urn = "{}:{}".format(
                    str(URN(str(self.urn)).upTo(URN.NO_PASSAGE)),
                    str(reference)
                )
        else:
            urn = str(self.urn)
        _first = _SharedMethod.firstUrn(
            self.retriever.getFirstUrn(
                urn
            )
        )
        return _first

    @property
    def firstId(self):
        """ Children passage

        :rtype: str
        :returns: First children of the graph. Shortcut to self.graph.children[0]
        """
        if self._first is False:
            # Request the next urn
            self._first = self.getFirstUrn()
        return self._first

    @property
    def lastId(self):
        """ Children passage

        :rtype: str
        :returns: First children of the graph. Shortcut to self.graph.children[0]
        """
        if self._last is False:
            # Request the next urn
            self._last = self.childIds[-1]
        return self._last

    @staticmethod
    def firstUrn(resource):
        """ Parse a resource to get the first URN

        :param resource: XML Resource
        :type resource: etree._Element
        :return: Tuple representing previous and next urn
        :rtype: str
        """
        resource = xmlparser(resource)
        urn = resource.xpath("//ti:reply/ti:urn/text()", namespaces=XPATH_NAMESPACES, magic_string=True)

        if len(urn) > 0:
            urn = str(urn[0])
            return urn.split(":")[-1]

    @staticmethod
    def prevnext(resource):
        """ Parse a resource to get the prev and next urn

        :param resource: XML Resource
        :type resource: etree._Element
        :return: Tuple representing previous and next urn
        :rtype: (str, str)
        """
        _prev, _next = False, False
        resource = xmlparser(resource)
        prevnext = resource.xpath("//ti:prevnext", namespaces=XPATH_NAMESPACES)

        if len(prevnext) > 0:
            _next, _prev = None, None
            prevnext = prevnext[0]
            _next_xpath = prevnext.xpath("ti:next/ti:urn/text()", namespaces=XPATH_NAMESPACES, smart_strings=False)
            _prev_xpath = prevnext.xpath("ti:prev/ti:urn/text()", namespaces=XPATH_NAMESPACES, smart_strings=False)

            if len(_next_xpath):
                _next = _next_xpath[0].split(":")[-1]

            if len(_prev_xpath):
                _prev = _prev_xpath[0].split(":")[-1]

        return _prev, _next


class CtsText(_SharedMethod, PrototypeCtsText):
    """ API CtsTextMetadata object

    :param urn: A URN identifier
    :type urn: Union[URN, str, unicode]
    :param resource: An API endpoint
    :type resource: CitableTextServiceRetriever
    :param citation: XmlCtsCitation for children level
    :type citation: XmlCtsCitation
    :param id: Identifier of the subreference without URN informations
    :type id: List

    """

    DEFAULT_LANG = "eng"

    def __init__(self, urn, retriever, citation=None, **kwargs):
        super(CtsText, self).__init__(retriever=retriever, urn=urn, citation=citation, **kwargs)

    @property
    def reffs(self):
        """ Get all valid reffs for every part of the CtsText

        :rtype: MyCapytain.resources.texts.tei.XmlCtsCitation
        """
        if not self.citation.is_set():
            self.getLabel()
        return [
            reff for reffs in [self.getValidReff(level=i) for i in range(1, len(self.citation) + 1)] for reff in reffs
        ]

    @property
    def nextId(self):
        raise NotImplementedError

    @property
    def next(self):
        raise NotImplementedError

    @property
    def prev(self):
        raise NotImplementedError

    @property
    def prevId(self):
        raise NotImplementedError

    @property
    def siblingsId(self):
        raise NotImplementedError

    def export(self, output=Mimetypes.PLAINTEXT, exclude=None, **kwargs):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses Mimetypes)
        :type output: str
        :param exclude: Informations to exclude. Specific to implementations
        :type exclude: [str]
        :return: Object using a different representation
        """
        return self.getTextualNode().export(output, exclude)


class CtsPassage(_SharedMethod, PrototypeCtsPassage, TeiResource):
    """ CapitainsCtsPassage representing

    :param urn:
    :param resource:
    :param retriever:
    :param args:
    :param kwargs:
    """

    def __init__(self, urn, resource, *args, **kwargs):
        SuperKwargs = {key: value for key, value in kwargs.items() if key not in ["parent"]}
        super(CtsPassage, self).__init__(resource=resource, *args, **SuperKwargs)
        self.urn = urn

        # Could be set during parsing
        self._next_id = False
        self._prev_id = False
        self._first_id = False
        self._last = False

        self._parse()

    @property
    def id(self):
        return str(self.urn.reference)

    @property
    def prevId(self):
        """ Previous passage Identifier

        :rtype: CtsPassage
        :returns: Previous passage at same level
        """
        if self._prev_id is False:
            # Request the next urn
            self._prev_id, self._next_id = self.getPrevNextUrn(reference=self.urn.reference)
        return self._prev_id

    @property
    def parentId(self):
        """ Shortcut for getting the parent passage identifier

        :rtype: CtsReference
        :returns: Following passage reference
        """
        return str(self.urn.reference.parent)

    @property
    def nextId(self):
        """ Shortcut for getting the following passage identifier

        :rtype: CtsReference
        :returns: Following passage reference
        """
        if self._next_id is False:
            # Request the next urn
            self._prev_id, self._next_id = self.getPrevNextUrn(reference=self.urn.reference)
        return self._next_id

    @property
    def siblingsId(self):
        """ Shortcut for getting the previous and next passage identifier

        :rtype: CtsReference
        :returns: Following passage reference
        """
        if self._next_id is False or self._prev_id is False:
            self._prev_id, self._next_id = self.getPrevNextUrn(reference=self.urn.reference)
        return self._prev_id, self._next_id

    def _parse(self):
        """ Given self.resource, split information from the CTS API

        :return: None
        """
        self.response = self.resource
        self.resource = self.resource.xpath("//ti:passage/tei:TEI", namespaces=XPATH_NAMESPACES)[0]

        self._prev_id, self._next_id = _SharedMethod.prevnext(self.response)

        if not self.citation.is_set() and len(self.resource.xpath("//ti:citation", namespaces=XPATH_NAMESPACES)):
            self.citation = CtsCollection.XmlCtsCitation.ingest(
                self.response,
                xpath=".//ti:citation[not(ancestor::ti:citation)]"
            )
