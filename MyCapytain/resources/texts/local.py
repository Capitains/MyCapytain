# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml


Local files handler for CTS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

import warnings

from MyCapytain.errors import DuplicateReference, MissingAttribute
from MyCapytain.common.utils import xmlparser, NS, copyNode, passageLoop, normalizeXpath
from MyCapytain.common.reference import URN, Citation, Reference

from MyCapytain.resources.prototypes import text
from MyCapytain.resources.texts import encodings

from MyCapytain.errors import InvalidSiblingRequest, InvalidURN
import MyCapytain.resources.texts.encodings
from lxml import etree


def __makePassageKwargs__(urn, reference):
    """ Little helper used by Passage here to comply with parents args

    :param urn:
    :param reference:
    :return:
    """
    kwargs = {}
    if urn is not None:
        if reference is not None:
            kwargs["urn"] = URN("{}:{}".format(urn.upTo(URN.VERSION), reference))
        else:
            kwargs["urn"] = urn
    return kwargs


class __SharedMethods__:
    class SimplePassage(encodings.TEIResource, text.Passage):
        def __init__(self, resource, reference, citation, urn=None):
            super(__SharedMethods__.SimplePassage, self).__init__(resource=resource, **__makePassageKwargs__(urn, reference))

    def getPassage(self, reference=None, simple=False):
        """ Finds a passage in the current text

        :param reference: Identifier of the subreference / passages
        :type reference: Union[list, Reference]
        :param hypercontext: If set to true, retrieves nodes up to the given one, cleaning non required siblings.
        :type hypercontext: boolean
        :rtype: Passage, ContextPassage
        :returns: Asked passage
t
        .. note :: As of MyCapytain 0.1.0, Text().getPassage() returns by default a ContextPassage, thus being able
            to handle range. This design change also means that the returned tree is way different that a classic
             Passage. To retrieve MyCapytain<=0.0.9 behaviour, use `hypercontext=False`.
        """

        if reference is None:
            return self._getSimplePassage(reference)

        if isinstance(reference, list):
            start, end = reference, reference
            reference = Reference(".".join(reference))
        elif not reference.end:
            start, end = reference.start.list, reference.start.list
        else:
            start, end = reference.start.list, reference.end.list

        if len(start) > len(self.citation):
            raise ReferenceError("URN is deeper than citation scheme")

        if simple is True:
            return self._getSimplePassage(reference)

        citation_start = [citation for citation in self.citation][len(start)-1]
        citation_end = [citation for citation in self.citation][len(end)-1]
        start, end = citation_start.fill(passage=start), citation_end.fill(passage=end)
        start, end = normalizeXpath(start.split("/")[2:]), normalizeXpath(end.split("/")[2:])

        if isinstance(self.xml, etree._Element):
            root = copyNode(self.xml)
        else:
            root = copyNode(self.xml.getroot())

        root = passageLoop(self.xml, root, start, end)

        if self.urn:
            urn, reference = URN("{}:{}".format(self.urn, reference)), reference
        else:
            urn, reference = None, reference
        return Passage(
            urn=urn,
            resource=root,
            text=self,
            citation=self.citation,
            reference=reference
        )

    def _getSimplePassage(self, reference):
        """ Retrieve a single node representing the passage.

        .. warning:: Range support is awkward.

        :param reference: Identifier of the subreference / passages
        :type reference: list, reference
        :returns: Asked passage
        :rtype: Passage
        """
        if reference is None:
            return self.SimplePassage(self.resource, reference=None, urn=self.urn, citation=self.citation)

        resource = self.resource.xpath(
            self.citation[len(reference)-1].fill(reference),
            namespaces=NS
        )

        if len(resource) != 1:
            raise InvalidURN
        return self.SimplePassage(
            resource[0],
            reference=None,
            urn=self.urn,
            citation=self.citation
        )

    def getValidReff(self, level=None, reference=None, _debug=False):
        """ Retrieve valid passages directly

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: int
        :param reference: Passage Reference
        :type reference: Reference
        :param _debug: Check on passages duplicates
        :type _debug: bool
        :returns: List of levels
        :rtype: list(basestring, str)

        .. note:: GetValidReff works for now as a loop using Passage, subinstances of Text, to retrieve the valid
        informations. Maybe something is more powerfull ?

        """
        depth = 0
        xml = self.xml
        if reference:
            if isinstance(reference, Reference):
                if reference.end is None:
                    passages = [reference.list]
                    depth = len(passages[0])
                else:
                    xml = self.getPassage(reference=reference)
                    common = []
                    for index in range(0, len(reference.start.list)):
                        if index == (len(common) - 1):
                            common.append(reference.start.list[index])
                        else:
                            break

                    passages = [common]
                    depth = len(common)
                    if not level:
                        level = len(reference.start.list) + 1

            else:
                raise TypeError()
        else:
            passages = [[]]

        if not level:
            level = 1
        if level <= len(passages[0]) and reference is not None:
            level = len(passages[0]) + 1
        if level > len(self.citation):
            return []

        nodes = [None] * (level - depth)

        citations = [citation for citation in self.citation]

        while len(nodes) >= 1:
            passages = [
                refs + [node.get("n")]
                for xpath_result, refs in [
                        (
                            xml.xpath(
                                citations[len(filling)-1].fill(filling),
                                namespaces=NS
                            ),
                            refs
                        )
                        for filling, refs in
                        [(refs + [None], refs) for refs in passages]
                    ]
                for node in xpath_result
            ]
            nodes.pop(0)

            if len(passages) == 0:
                msg = "Unknown reference {}".format(reference)
                raise KeyError(msg)

        passages = [".".join(passage) for passage in passages]

        if _debug:
            duplicates = set([n for n in passages if passages.count(n) > 1])
            if len(duplicates) > 0:
                message = ", ".join(duplicates)
                warnings.warn(message, DuplicateReference)
            del duplicates

        return passages

    def xpath(self, *args, **kwargs):
        """ Perform XPath on the passage XML

        :param args: Ordered arguments for etree._Element().xpath()
        :param kwargs: Named arguments
        :return: Result list
        :rtype: list(etree._Element)
        """
        if "smart_strings" not in kwargs:
            kwargs["smart_strings"] = False
        return self.resource.xpath(*args, **kwargs)

    def tostring(self, *args, **kwargs):
        """ Transform the Passage in XML string

        :param args: Ordered arguments for etree.tostring() (except the first one)
        :param kwargs: Named arguments
        :return:
        """
        return etree.tostring(self.resource, *args, **kwargs)


class Text(__SharedMethods__, encodings.TEIResource, text.Text):
    """ Implementation of CTS tools for local files

    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param citation: Highest Citation level
    :type citation: Citation
    :param autoreffs: Parse references on load (default : True)
    :type autoreffs: bool
    :ivar resource: lxml
    """

    def __init__(self, urn=None, citation=None, resource=None):
        super(Text, self).__init__(urn=urn, citation=citation, resource=resource)

        if self.resource is not None:
            self.__findCRefPattern(self.resource)

    def __findCRefPattern(self, xml):
        """ Find CRefPattern in the text and set object.citation
        :param xml: Xml Resource
        :type xml: lxml.etree._Element
        :return: None
        """
        if self.citation.isEmpty():
            citation = xml.xpath("//tei:refsDecl[@n='CTS']", namespaces=MyCapytain.common.utils.NS),
            if len(citation):
                self.citation = Citation.ingest(resource=citation[0], xpath=".//tei:cRefPattern")


class Passage(__SharedMethods__, encodings.TEIResource, text.Passage):
    """ Passage class for local texts which rebuilds the tree up to the passage.

        For design purposes, some people would prefer the output of GetPassage to be consistent. ContextPassage rebuilds
        the tree of the text up to the passage, keeping attributes of original nodes

        **Example** :  for a text with a citation scheme with following refsDecl :
        `/TEI/text/body/div[@type='edition']/div[@n='$1']/div[@n='$2']/l[@n='$3']` and a passage 1.1.1-1.2.3, this
        class will build an XML tree looking like the following

         .. code-block:: xml

            <TEI ...>
                <text ...>
                    <body ...>
                        <div type='edition' ...>
                            <div n='1' ...>

                                <div n='1' ...>
                                    <l n='1'>...</l>
                                    ...
                                </div>
                                <div n='2' ...>
                                    <l n='3'>...</l>
                                </div>
                            </div>
                        </div>
                    </body>
                </text>
            </TEI>

        :param urn: URN of the source text or of the passage
        :type urn: URN
        :param resource: Element representing the passage
        :type resource: etree._Element, Text
        :param text: Text containing the passage
        :type text: Text
        :param citation: Citation scheme of the text
        :type citation: Citation
        :param reference: Passage reference
        :type reference: Reference

        .. note::
            .prev, .next, .first and .last won't run on passage with a range made of two different level, such as
            1.1-1.2.3 or 1-a.b. Those will raise `InvalidSiblingRequest`

    """
    def __init__(self, reference, urn=None, citation=None, resource=None, text=None):

        super(Passage, self).__init__(
            citation=citation,
            resource=resource,
            **__makePassageKwargs__(urn, reference)
        )

        self.__reference__ = reference
        self.__text__ = text
        self.__children__ = None
        self.__depth__ = self.__depth_2__ = 1

        if self.reference.start:
            self.__depth_2__ = self.__depth__ = len(self.reference.start)
        if self.reference and self.reference.end:
            self.__depth_2__ = len(self.reference.end)

        self.__prevnext__ = None  # For caching purpose

    @property
    def reference(self):
        return self.__reference__

    @property
    def children(self):
        """ Children of the passage

        :rtype: None, Reference
        :returns: Dictionary of chidren, where key are subreferences
        """
        self.__raiseDepth__()
        if self.depth >= len(self.citation):
            return []
        elif self.__children__ is not None:
            return self.__children__
        else:
            self.__children__ = self.getValidReff(level=self.depth+1)
            return self.__children__

    @property
    def firstId(self):
        return self.children[0]

    @property
    def lastId(self):
        return self.children[-1]

    @property
    def nextId(self):
        """ Next passage

        :returns: Next passage at same level
        :rtype: None, Reference
        """
        return self.siblingsId[1]

    @property
    def prevId(self):
        """ Get the Previous passage reference

        :returns: Previous passage reference at the same level
        :rtype: None, Reference
        """
        return self.siblingsId[0]

    def __raiseDepth__(self):
        """ Simple check that raises an exception if the passage cannot run first, last, next or prev

        See object notes

        :raise: InvalidSiblingRequest
        """
        if self.__depth__ != self.__depth_2__:
            raise InvalidSiblingRequest()

    @property
    def siblingsId(self):
        """ Siblings Identifiers of the passage

        :rtype: (str, str)
        """
        self.__raiseDepth__()

        if not self.__text__:
            raise MissingAttribute("Passage was iniated without Text object")
        if self.__prevnext__:
            return self.__prevnext__

        document_references = list(map(lambda x: str(x), self.__text__.getValidReff(level=self.depth)))
        range_length = len(self.getValidReff(level=self.depth))

        if self.reference.end:
            start, end = str(self.reference.start), str(self.reference.end)
        else:
            start = end = str(self.reference.start)

        start = document_references.index(start)
        end = document_references.index(end)

        _prev, _next = None, None

        if start == 0:
            # If the passage is already at the beginning
            _prev = None
        elif start - range_length < 0:
            if start == end:
                _prev = Reference(document_references[0])
            else:
                _prev = Reference(
                    "{}-{}".format(document_references[0], document_references[start-1])
                )
        else:
            if start == end:
                _prev = Reference(document_references[start-1])
            else:
                _prev = Reference(
                    "{}-{}".format(document_references[start-range_length], document_references[start-1])
                )

        if start + 1 == len(document_references) or end + 1 == len(document_references):
            # If the passage is already at the end
            _next = None
        elif end + range_length > len(document_references):
            if start == end:
                _next = Reference(document_references[-1])
            else:
                _next = Reference(
                    "{}-{}".format(document_references[end +1], document_references[-1])
                )
        else:
            if start == end:
                _next = Reference(document_references[end +1])
            else:
                _next = Reference(
                    "{}-{}".format(document_references[end + 1], document_references[end + range_length])
                )

        self.__prevnext__ = (_prev, _next)
        return self.__prevnext__