from __future__ import unicode_literals
from six import text_type as str

from lxml import etree

import MyCapytain.resources.proto.text
import MyCapytain.resources.texts.tei
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

        self._cRefPattern = MyCapytain.common.reference.Citation()

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
        :param passage: Subreference (optional)
        :type passage: Reference
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
        for ref in MyCapytain.common.utils.xmlparser(xml).xpath(
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

        self.__parse_request(response)
        return Passage(urn=urn, resource=response, parent=self)

    def __parse_request(self, xml):
        for node in xml.xpath("//ti:request/ti:groupname", namespaces=MyCapytain.common.utils.NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata["groupname"][lang] = node.text

        for node in xml.xpath("//ti:request/ti:title", namespaces=MyCapytain.common.utils.NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata["title"][lang] = node.text

        for node in xml.xpath("//ti:request/ti:label", namespaces=MyCapytain.common.utils.NS):
            lang = node.get("xml:lang") or Text.DEFAULT_LANG
            self.metadata["label"][lang] = node.text

        # Need to code that
        if self.citation is None:
            self.citation = ""

    def getLabel(self):
        """ Retrieve metadata about the text

        :rtype: dict
        :returns: Dictionary with label informations
        """
        raise NotImplementedError()

    @property
    def reffs(self):
        """ Get all valid reffs for every part of the Text

        :rtype: MyCapytain.resources.texts.tei.Citation
        """
        return [reff for reffs in [self.getValidReff(level=i) for i in range(1, len(self.citation) + 1)] for reff in reffs]

    @property
    def citation(self):
        """ Get the lowest cRefPattern in the hierarchy

        :rtype: MyCapytain.common.reference.Citation
        """
        return self._cRefPattern

    @citation.setter
    def citation(self, value):
        """ Set the cRefPattern

        :param value: Citation to be saved
        :type value:  MyCapytain.common.reference.Citation
        """
        if isinstance(value, MyCapytain.common.reference.Citation):
            self._cRefPattern = value


class Passage(MyCapytain.resources.texts.tei.Passage):

    def __init__(self, urn, resource, *args, **kwargs):
        super(Passage, self).__init__(resource=resource, *args, **kwargs)

        self.urn = urn

        # Could be set during parsing
        self.__next = None
        self.__prev = None
        self.__first = None
        self.__last = None

        self.__parse()

    @property
    def next(self):
        """ Following passage

        :rtype: Passage
        :returns: Following passage at same level
        """
        if self.__next is not None:
            _next = self.__next
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
        if self.__prev is not None:
           _prev = self.__prev
        else:
            # Request the next urn
            _prev, _next = Passage.prevnext(
                self.parent.resource.getPrevNextUrn(urn=str(self.urn))
            )

        return self.parent.resource.getPassage(urn=_prev)

    @property
    def first(self):
        """ First child of current Passage

        :rtype: None or Passage
        :returns: None if current Passage has no children,  first child passage if available
        """
        raise NotImplementedError()

    @property
    def last(self):
        """ Last child of current Passage

        :rtype: None or Passage
        :returns: None if current Passage has no children, last child passage if available
        """
        raise NotImplementedError()

    def __parse(self):
        """ Given self.resource, split informations from the CTS API

        :return: None
        """
        self.resource = self.resource.xpath("//ti:passage/tei:TEI", namespaces=MyCapytain.common.utils.NS)[0]
        if not self.urn:
            self.urn = self.resource.xpath("//ti:reply/ti:urn/text()", namespaces=MyCapytain.common.utils.NS)[0]

        self.__prev, self.__next = Passage.prevnext(self.resource)

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
            _next = prevnext.xpath("ti:next/ti:urn/text()", namespaces=MyCapytain.common.utils.NS)
            _prev = prevnext.xpath("ti:prev/ti:urn/text()", namespaces=MyCapytain.common.utils.NS)

            if len(_next):
               _next = _next[0]

            if len(_prev):
                _prev = _prev[0]

        return _prev, _next

