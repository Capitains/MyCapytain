from __future__ import unicode_literals
from six import text_type as str

import MyCapytain.resources.proto.text
import MyCapytain.resources.texts.tei
import MyCapytain.resources.inventory
import MyCapytain.endpoints.proto
import MyCapytain.common.metadata
import MyCapytain.common.utils


class Text(MyCapytain.resources.proto.text.Text):
    """ Passage representing object prototype

    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: An API endpoint
    :type resource: MyCapytain.endpoints.proto.CTS
    :param citation: Citation for children level
    :type citation: MyCapytain.resources.texts.tei.Citation
    :param id: Identifier of the subreference without URN informations
    :type id: List

    """

    DEFAULT_LANG = "eng"

    def __init__(self, urn, resource, citation=None, **kwargs):
        __doc__ = Text.__doc__
        super(Text, self).__init__(urn=urn, citation=citation, **kwargs)

        self._cRefPattern = None

        self.resource = resource

        if citation is not None:
            self.citation = citation

        if "metadata" in kwargs and isinstance(kwargs["metadata"], MyCapytain.common.metadata.Metadata):
            self.metadata = kwargs["metadata"]
        else:
            self.metadata = MyCapytain.common.metadata.Metadata([
                "groupname", "label", "title"
            ])

        self.passages = []

    def getValidReff(self, level=1, reference=None):
        """ Given a resource, Text will compute valid reffs

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param reference: Subreference (optional)
        :type reference: Reference
        :rtype: List.basestring
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
        xml = MyCapytain.common.utils.xmlparser(xml)
        self.__parse_request(xml.xpath("//ti:request", namespaces=MyCapytain.common.utils.NS)[0])

        for ref in xml.xpath(
            "//ti:reply//ti:urn/text()",
            namespaces=MyCapytain.common.utils.NS
        ):
            self.passages.append(ref)

        return self.passages

    def getPassage(self, reference=None):
        """ Retrieve a passage and store it in the object

        :param reference: Reference of the passage
        :type reference: MyCapytain.common.reference.Reference or List of basestring
        :rtype: Passage
        :returns: Object representing the passage
        :raises: *TypeError* when reference is not a list or a Reference
        """
        if reference:
            urn = "{0}:{1}".format(self.urn, reference)
        else:
            urn = str(self.urn)

        response = MyCapytain.common.utils.xmlparser(self.resource.getPassage(urn=urn))

        self.__parse_request(response.xpath("//ti:request", namespaces=MyCapytain.common.utils.NS)[0])
        return Passage(urn=urn, resource=response, parent=self)

    def getPassagePlus(self, reference=None):
        """ Retrieve a passage and informations around it and store it in the object

        :param reference: Reference of the passage
        :type reference: MyCapytain.common.reference.Reference or List of basestring
        :rtype: Passage
        :returns: Object representing the passage
        :raises: *TypeError* when reference is not a list or a Reference
        """
        if reference:
            urn = "{0}:{1}".format(self.urn, reference)
        else:
            urn = str(self.urn)

        response = MyCapytain.common.utils.xmlparser(self.resource.getPassagePlus(urn=urn))

        self.__parse_request(response.xpath("//ti:reply/ti:label", namespaces=MyCapytain.common.utils.NS)[0])
        return Passage(urn=urn, resource=response, parent=self)

    def __parse_request(self, xml):
        """

        :param xml:
        :return:

        .. TODO: Finish self.citation parsing
        """
        for node in xml.xpath(".//ti:groupname", namespaces=MyCapytain.common.utils.NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata["groupname"][lang] = node.text

        for node in xml.xpath(".//ti:title", namespaces=MyCapytain.common.utils.NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata["title"][lang] = node.text

        for node in xml.xpath(".//ti:label", namespaces=MyCapytain.common.utils.NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata["label"][lang] = node.text

        # Need to code that p
        if self.citation is None:
            self.citation = MyCapytain.resources.inventory.Citation.ingest(
                xml,
                xpath=".//ti:citation[not(ancestor::ti:citation)]"
            )

    def getLabel(self):
        """ Retrieve metadata about the text

        :rtype: Metadata
        :returns: Dictionary with label informations
        """
        response = MyCapytain.common.utils.xmlparser(
            self.resource.getLabel(urn=str(self.urn))
        )

        self.__parse_request(response.xpath("//ti:reply/ti:label", namespaces=MyCapytain.common.utils.NS)[0])

        return self.metadata

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


class Passage(MyCapytain.resources.texts.tei.Passage):

    def __init__(self, urn, resource, *args, **kwargs):
        super(Passage, self).__init__(resource=resource, *args, **kwargs)

        self.urn = urn

        # Could be set during parsing
        self._next = None
        self._prev = None
        self.__first = None
        self.__last = None

        self.__parse()

    @property
    def next(self):
        """ Following passage

        :rtype: Passage
        :returns: Following passage at same level
        """
        if self._next is not None:
            _next = self._next
        else:
            # Request the next urn
            _prev, _next = Passage.prevnext(
                self.parent.resource.getPrevNextUrn(urn=str(self.urn))
            )

        self.parent.resource.getPassage(urn=_next)

    @property
    def prev(self):
        """ Previous passage

        :rtype: Passage
        :returns: Previous passage at same level
        """
        if self._prev is not None:
           _prev = self._prev
        else:
            # Request the next urn
            _prev, _next = Passage.prevnext(
                self.parent.resource.getPrevNextUrn(urn=str(self.urn))
            )

        return self.parent.resource.getPassage(urn=_prev)

    def __parse(self):
        """ Given self.resource, split informations from the CTS API

        :return: None
        """
        self.resource = self.resource.xpath("//ti:passage/tei:TEI", namespaces=MyCapytain.common.utils.NS)[0]

        self._prev, self._next = Passage.prevnext(self.resource)

    @staticmethod
    def prevnext(resource):
        """ Parse a resource to get the prev and next urn

        :param resource: XML Resource
        :type resource: etree._Element
        :return: Tuple representing previous and next urn
        :rtype: (str, str)
        """
        _prev, _next = None, None
        resource = MyCapytain.common.utils.xmlparser(resource)
        prevnext = resource.xpath("//ti:prevnext", namespaces=MyCapytain.common.utils.NS)

        if len(prevnext) > 0:
            prevnext = prevnext[0]
            _next_xpath = prevnext.xpath("ti:next/ti:urn/text()", namespaces=MyCapytain.common.utils.NS)
            _prev_xpath = prevnext.xpath("ti:prev/ti:urn/text()", namespaces=MyCapytain.common.utils.NS)

            if len(_next_xpath):
               _next = _next_xpath[0]

            if len(_prev_xpath):
                _prev = _prev_xpath[0]

        return _prev, _next

