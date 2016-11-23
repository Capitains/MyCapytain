# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from six import text_type as str

from MyCapytain.common.metadata import Metadata
from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.common.utils import Mimetypes, xmlparser, NS
from MyCapytain.common.reference import Citation, URN, Reference
from MyCapytain.resources.collections import cts as CTSCollection
from MyCapytain.resources.prototypes import text as prototypes
from MyCapytain.resources.texts.encodings import TEIResource
from MyCapytain.retrievers.prototypes import CitableTextServiceRetriever



class Text(prototypes.Text, prototypes.InteractiveTextualNode):
    """ Passage representing object prototype

    :param urn: A URN identifier
    :type urn: URN
    :param resource: An API endpoint
    :type resource: CitableTextServiceRetriever
    :param citation: Citation for children level
    :type citation: Citation
    :param id: Identifier of the subreference without URN informations
    :type id: List

    """

    DEFAULT_LANG = "eng"

    def __init__(self, urn, resource, citation=None, **kwargs):
        super(Text, self).__init__(urn=urn, citation=citation, **kwargs)

        self._cRefPattern = None

        self.resource = resource

        if citation is not None:
            self.citation = citation

        if "metadata" in kwargs and isinstance(kwargs["metadata"], Metadata):
            self.metadata = kwargs["metadata"]
        else:
            self.metadata = Metadata(keys=[
                "groupname", "label", "title"
            ])

        self.passages = []

    def getValidReff(self, level=1, reference=None):
        """ Given a resource, Text will compute valid reffs

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param reference: Passage reference
        :type reference: Reference
        :rtype: list(str)
        :returns: List of levels
        """
        if reference:
            urn = "{0}:{1}".format(self.urn, reference)
        else:
            urn = str(self.urn)

        if level == -1:
            level = len(self.citation)

        xml = self.resource.getValidReff(
            level=level,
            urn=urn
        )
        xml = xmlparser(xml)
        self.__parse_request(xml.xpath("//ti:request", namespaces=NS)[0])

        for ref in xml.xpath(
            "//ti:reply//ti:urn/text()",
            namespaces=NS
        ):
            self.passages.append(ref)

        return self.passages

    def getPassage(self, reference=None):
        """ Retrieve a passage and store it in the object

        :param reference: Reference of the passage
        :type reference: Reference, or URN, or str or list(str)
        :rtype: Passage
        :returns: Object representing the passage
        :raises: *TypeError* when reference is not a list or a Reference
        """
        if isinstance(reference, URN):
            urn = str(reference)
        elif isinstance(reference, Reference):
            urn = "{0}:{1}".format(self.urn, str(reference))
        elif isinstance(reference, str):
            urn = "{0}:{1}".format(self.urn, reference)
        elif isinstance(reference, list):
            urn = "{0}:{1}".format(self.urn, ".".join(reference))
        else:
            urn = str(self.urn)

        response = xmlparser(self.resource.getPassage(urn=urn))

        self.__parse_request(response.xpath("//ti:request", namespaces=NS)[0])
        return Passage(urn=urn, resource=response, parent=self)

    def getPassagePlus(self, reference=None):
        """ Retrieve a passage and informations around it and store it in the object

        :param reference: Reference of the passage
        :type reference: Reference or List of basestring
        :rtype: Passage
        :returns: Object representing the passage
        :raises: *TypeError* when reference is not a list or a Reference
        """
        if reference:
            urn = "{0}:{1}".format(self.urn, reference)
        else:
            urn = str(self.urn)

        response = xmlparser(self.resource.getPassagePlus(urn=urn))

        self.__parse_request(response.xpath("//ti:reply/ti:label", namespaces=NS)[0])
        return Passage(urn=urn, resource=response, parent=self)

    def __parse_request(self, xml):
        """

        :param xml:
        :return:

        .. TODO: Finish self.citation parsing
        """
        for node in xml.xpath(".//ti:groupname", namespaces=NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata.metadata["groupname"][lang] = node.text

        for node in xml.xpath(".//ti:title", namespaces=NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata.metadata["title"][lang] = node.text

        for node in xml.xpath(".//ti:label", namespaces=NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata.metadata["label"][lang] = node.text

        # Need to code that p
        if self.citation.isEmpty():
            self.citation = CTSCollection.Citation.ingest(
                xml,
                xpath=".//ti:citation[not(ancestor::ti:citation)]"
            )

    def getLabel(self):
        """ Retrieve metadata about the text

        :rtype: Metadata
        :returns: Dictionary with label informations
        """
        response = xmlparser(
            self.resource.getLabel(urn=str(self.urn))
        )

        self.__parse_request(response.xpath("//ti:reply/ti:label", namespaces=NS)[0])

        return self.metadata

    def getPrevNextUrn(self, reference):
        """ Get the previous URN of a reference of the text

        :param reference: Reference from which to find siblings
        :type reference: Reference
        :return: (Previous Passage Reference,Next Passage Reference)
        """
        _prev, _next = Passage.prevnext(
            self.resource.getPrevNextUrn(
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

        :param reference: Reference from which to find child (If None, find first reference)
        :type reference: Reference, str
        :return: Children URN
        :rtype: URN
        """
        if reference:
            urn = "{}:{}".format(
                str(URN(str(self.urn)).upTo(URN.NO_PASSAGE)),
                str(reference)
            )
        else:
            urn = self.urn

        _first = Passage.firstUrn(
            self.resource.getFirstUrn(
                urn
            )
        )
        return _first

    @property
    def reffs(self):
        """ Get all valid reffs for every part of the Text

        :rtype: MyCapytain.resources.texts.tei.Citation
        """
        if self.citation is None:
            reffs = [self.getValidReff()]
            return reffs + [
                reff for reffs in [self.getValidReff(level=i) for i in range(2, len(self.citation) + 1)] for reff in reffs
            ]
        else:
            return [
                reff for reffs in [self.getValidReff(level=i) for i in range(1, len(self.citation) + 1)] for reff in reffs
            ]

    def export(self, output=None, exclude=None):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses Mimetypes)
        :type output: str
        :param exclude: Informations to exclude. Specific to implementations
        :type exclude: [str]
        :return: Object using a different representation
        """
        return self.getPassage().export(output, exclude)


class Passage(TEIResource):

    def __init__(self, urn, resource, *args, **kwargs):
        SuperKwargs = {key:value for key, value in kwargs.items() if key not in ["parent"]}
        super(Passage, self).__init__(resource=resource, *args, **SuperKwargs)

        self.urn = urn

        # Could be set during parsing
        self.__next__ = False
        self.__prev__ = False
        self.__first__ = False
        self.__last__ = False

        self.__parse__()

    @property
    def firstId(self):
        """ Children passage

        :rtype: str
        :returns: First children of the graph. Shortcut to self.graph.children[0]
        """
        if self.__first__ is False:
            # Request the next urn
            self.__first__ = Reference(
                identifier=self.parent.getFirstUrn(reference=str(self.urn.reference)),
                depth=len(self.urn.reference.start)+1
            )
            if len(self.graph.children) == 0:
                self.graph.children.append(self.__first__)
        return self.__first__

    @property
    def prev(self):
        """ Previous passage

        :rtype: Passage
        :returns: Previous passage at same level
        """
        if self.__prev__ is False:
            # Request the next urn
            self.__prev__, self.__next__ = self.parent.getPrevNextUrn(reference=self.urn.reference)
            self.graph.prev = NodeId(identifier=self.__prev__)
        return self.__prev__

    @property
    def next(self):
        """ Shortcut for getting the following passage

        :rtype: Reference
        :returns: Following passage reference
        """
        if self.__next__ is False:
            # Request the next urn
            self.__prev__, self.__next__ = self.parent.getPrevNextUrn(reference=self.urn.reference)
        return self.__next__

    def getNext(self):
        """ Shortcut for getting the following passage

        :rtype: Passage
        :returns: Following passage at same level
        """
        if self.next:
            return self.parent.getPassage(reference=self.next)

    def getPrev(self):
        """ Shortcut for getting the preceding passage

        :rtype: Passage
        :returns: Previous passage at same level
        """
        if self.prev:
            return self.parent.getPassage(reference=self.prev)

    def getFirst(self):
        """ Shortcut for getting the first child passage

        :rtype: Passage
        :returns: Previous passage at same level
        """
        if self.first:
            return self.parent.getPassage(reference=self.first)

    def __parse__(self):
        """ Given self.resource, split informations from the CTS API

        :return: None
        """
        self.resource = self.resource.xpath("//ti:passage/tei:TEI", namespaces=NS)[0]

        self.__prev__, self.__next__ = Passage.prevnext(self.resource)

        if self.citation.isEmpty():
            self.__citation__ = CTSCollection.Citation.ingest(
                self.resource,
                xpath=".//ti:citation[not(ancestor::ti:citation)]"
            )

    @staticmethod
    def prevnext(resource):
        """ Parse a resource to get the prev and next urn

        :param resource: XML Resource
        :type resource: etree._Element
        :return: Tuple representing previous and next urn
        :rtype: (URN, URN)
        """
        _prev, _next = False, False
        resource = xmlparser(resource)
        prevnext = resource.xpath("//ti:prevnext", namespaces=NS)

        if len(prevnext) > 0:
            _next, _prev = None, None
            prevnext = prevnext[0]
            _next_xpath = prevnext.xpath("ti:next/ti:urn/text()", namespaces=NS, smart_strings=False)
            _prev_xpath = prevnext.xpath("ti:prev/ti:urn/text()", namespaces=NS, smart_strings=False)

            if len(_next_xpath):
               _next = URN(_next_xpath[0])

            if len(_prev_xpath):
                _prev = URN(_prev_xpath[0])

        return _prev, _next

    @staticmethod
    def firstUrn(resource):
        """ Parse a resource to get the first URN

        :param resource: XML Resource
        :type resource: etree._Element
        :return: Tuple representing previous and next urn
        :rtype: URN
        """
        _child = False
        resource = xmlparser(resource)
        urn = resource.xpath("//ti:reply/ti:urn/text()", namespaces=NS, magic_string=True)

        if len(urn) > 0:
            urn = str(urn[0])

            return URN(urn)

