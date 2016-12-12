# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.texts.locals.tei

This module contains methods to parse local resources using TEI/Epidoc guidelines of CapiTainS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

import warnings

from MyCapytain.errors import DuplicateReference, MissingAttribute, RefsDeclError
from MyCapytain.common.utils import NS, copyNode, passageLoop, normalizeXpath
from MyCapytain.common.reference import URN, Citation, Reference

from MyCapytain.resources.prototypes import text
from MyCapytain.resources.texts import encodings

from MyCapytain.errors import InvalidSiblingRequest, InvalidURN
from lxml import etree


def __makePassageKwargs__(urn, reference):
    """ Little helper used by Passage here to comply with parents args

    :param urn: URN String
    :param reference: Reference String
    :return: Dictionary of arguments with URN based on identifier and reference
    """
    kwargs = {}
    if urn is not None:
        if reference is not None:
            kwargs["urn"] = URN("{}:{}".format(urn.upTo(URN.VERSION), reference))
        else:
            kwargs["urn"] = urn
    return kwargs


class __SharedMethods__:
    """ Set of shared methods between objects in locals TEI. Avoid recoding functions
    """

    def getPassage(self, reference=None, simple=False):
        """ Finds a passage in the current text

        :param reference: Identifier of the subreference / passages
        :type reference: Union[list, Reference]
        :param simple: If set to true, retrieves nodes up to the given one, cleaning non required siblings.
        :type simple: boolean
        :rtype: Passage, ContextPassage
        :returns: Asked passage
        """

        if reference is None:
            return self._getSimplePassage()

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

    def _getSimplePassage(self, reference=None):
        """ Retrieve a single node representing the passage.

        .. warning:: Range support is awkward.

        :param reference: Identifier of the subreference / passages
        :type reference: list, reference
        :returns: Asked passage
        :rtype: Passage
        """
        if reference is None:
            return __SimplePassage__(self.resource, reference=None, urn=self.urn, citation=self.citation)

        resource = self.resource.xpath(
            self.citation[len(reference)-1].fill(reference),
            namespaces=NS
        )

        if len(resource) != 1:
            raise InvalidURN

        return __SimplePassage__(
            resource[0],
            reference=reference,
            urn=self.urn,
            citation=self.citation,
            text=self.textObject
        )

    @property
    def textObject(self):
        """ Textual Object with full capacities (Unlike Simple Passage)

        :rtype: Text, Passage
        :return: Textual Object with full capacities (Unlike Simple Passage)
        """
        text = None
        if isinstance(self, Text):
            text = self
        elif hasattr(self, "__text__") and self.__text__ is not None:
            text = self.__text__
        return text

    def getReffs(self, level=1, reference=None):
        """ Reference available at a given level

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param passage: Subreference (optional)
        :type passage: Reference
        :rtype: List.basestring
        :returns: List of levels
        """
        if hasattr(self, "__depth__"):
            level = level + self.depth
        if not reference:
            if hasattr(self, "reference"):
                reference = self.reference

        return self.getValidReff(level, reference)

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

        .. note:: GetValidReff works for now as a loop using Passage, subinstances of Text, to retrieve the valid \
        informations. Maybe something is more powerfull ?
        """
        depth = 0
        xml = self.textObject.xml
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


class __SimplePassage__(__SharedMethods__, encodings.TEIResource, text.Passage):
    """ Passage for simple and quick parsing of texts

    :param resource: Element representing the passage
    :type resource: etree._Element
    :param reference: Passage reference
    :type reference: Reference
    :param urn: URN of the source text or of the passage
    :type urn: URN
    :param citation: Citation scheme of the text
    :type citation: Citation
    :param text: Text containing the passage
    :type text: Text
    """
    def __init__(self, resource, reference, citation, urn=None, text=None):
        super(__SimplePassage__, self).__init__(
            resource=resource,
            citation=citation,
            **__makePassageKwargs__(urn, reference)
        )
        self.__text__ = text
        self.__reference__ = reference
        self.__children__ = None
        self.__depth__ = None
        if reference is not None:
            self.__depth__ = len(reference)
        self.__prevnext__ = None

    @property
    def reference(self):
        """ URN Passage Reference

        :return: Reference
        :rtype: Reference
        """
        return self.__reference__

    @reference.setter
    def reference(self, value):
        self.__reference__ = value

    @property
    def childIds(self):
        """ Children of the passage

        :rtype: None, Reference
        :returns: Dictionary of chidren, where key are subreferences
        """
        if self.depth >= len(self.citation):
            return []
        elif self.__children__ is not None:
            return self.__children__
        else:
            self.__children__ = self.getReffs()
            return self.__children__

    def getReffs(self, level=1, reference=None):
        """ Reference available at a given level

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param reference: Subreference (optional)
        :type reference: Reference
        :rtype: List.basestring
        :returns: List of levels
        """
        level = self.depth + level
        if not reference:
            reference = self.reference
        return __SharedMethods__.getValidReff(self, level, reference=reference)

    def getPassage(self, reference=None, simple=True):
        """ Special GetPassage implementation for SimplePassage (Simple is True by default)

        :param reference:
        :param simple:
        :return:
        """
        if not isinstance(reference, Reference):
            reference = Reference(reference)
        return __SharedMethods__.getPassage(self, reference, simple)

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

    @property
    def siblingsId(self):
        """ Siblings Identifiers of the passage

        :rtype: (str, str)
        """

        if not self.__text__:
            raise MissingAttribute("Passage was iniated without Text object")
        if self.__prevnext__ is not None:
            return self.__prevnext__

        document_references = list(map(str, self.__text__.getReffs(level=self.depth)))
        range_length = len(self.getReffs())

        start = str(self.reference.start)

        start = document_references.index(start)

        if start == 0:
            # If the passage is already at the beginning
            _prev = None
        elif start - range_length < 0:
            _prev = Reference(document_references[0])
        else:
            _prev = Reference(document_references[start-1])

        if start + 1 == len(document_references):
            # If the passage is already at the end
            _next = None
        elif start + range_length > len(document_references):
            _next = Reference(document_references[-1])
        else:
            _next = Reference(document_references[start +1])

        self.__prevnext__ = (_prev, _next)
        return self.__prevnext__


class Text(__SharedMethods__, encodings.TEIResource, text.CitableText):
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
            citation = xml.xpath("//tei:refsDecl[@n='CTS']", namespaces=NS),
            if len(citation):
                self.citation = Citation.ingest(resource=citation[0], xpath=".//tei:cRefPattern")

    def test(self):
        """ Parse the object and generate the children
        """
        try:
            xml = self.xml.xpath(self.citation.scope, namespaces=NS)
            if len(xml) == 0:
                msg = "Main citation scope does not result in any result ({0})".format(self.citation.scope)
                raise RefsDeclError(msg)
        except Exception as E:
            raise E


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

        :param reference: Passage reference
        :type reference: Reference
        :param urn: URN of the source text or of the passage
        :type urn: URN
        :param citation: Citation scheme of the text
        :type citation: Citation
        :param resource: Element representing the passage
        :type resource: etree._Element
        :param text: Text containing the passage
        :type text: Text

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
        if urn is not None and urn.reference is not None:
            reference = urn.reference
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
    def childIds(self):
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
            self.__children__ = self.getReffs()
            return self.__children__

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
            raise MissingAttribute("Passage was initiated without Text object")
        if self.__prevnext__:
            return self.__prevnext__

        document_references = list(map(str, self.__text__.getReffs(level=self.depth)))
        range_length = len(self.getReffs(level=0))

        if self.reference.end:
            start, end = str(self.reference.start), str(self.reference.end)
        else:
            start = end = str(self.reference.start)

        start = document_references.index(start)
        end = document_references.index(end)

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
                    "{}-{}".format(document_references[end+1], document_references[-1])
                )
        else:
            if start == end:
                _next = Reference(document_references[end+1])
            else:
                _next = Reference(
                    "{}-{}".format(document_references[end+1], document_references[end + range_length])
                )

        self.__prevnext__ = (_prev, _next)
        return self.__prevnext__

    @property
    def next(self):
        if self.nextId is not None:
            return __SharedMethods__.getPassage(self.__text__, self.nextId)

    @property
    def prev(self):
        if self.prevId is not None:
            return __SharedMethods__.getPassage(self.__text__, self.prevId)

    def getPassage(self, reference, simple=False):
        __doc__ = __SharedMethods__.__doc__
        if not isinstance(reference, Reference):
            reference = Reference(reference)
        X = __SharedMethods__.getPassage(self, reference, simple)
        X.__text__ = self.__text__
        return X
