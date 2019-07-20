# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.texts.local.tei

This module contains methods to parse local resources using TEI/Epidoc guidelines of CapiTainS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

import warnings

from typing import Tuple, Optional
from MyCapytain.errors import DuplicateReference, MissingAttribute, RefsDeclError, EmptyReference, CitationDepthError, MissingRefsDecl
from MyCapytain.common.utils.xml import copyNode, normalizeXpath, passageLoop
from MyCapytain.common.constants import XPATH_NAMESPACES
from MyCapytain.common.reference import CtsReference, URN, Citation, CtsReferenceSet

from MyCapytain.resources.prototypes.cts.text import PrototypeCtsPassage, PrototypeCtsText
from MyCapytain.resources.texts.base.tei import TeiResource

from MyCapytain.errors import InvalidSiblingRequest, InvalidURN
import lxml.etree as etree


__all__ = [
    "CapitainsCtsText",
    "CapitainsCtsPassage"
]


def _make_passage_kwargs(urn, reference):
    """ Little helper used by CapitainsCtsPassage here to comply with parents args

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


class _SharedMethods(TeiResource):
    """ Set of shared methods between objects in local TEI. Avoid recoding functions
    """

    def getTextualNode(self, subreference=None, simple=False):
        """ Finds a passage in the current text

        :param subreference: Identifier of the subreference / passages
        :type subreference: Union[list, CtsReference]
        :param simple: If set to true, retrieves nodes up to the given one, cleaning non required siblings.
        :type simple: boolean
        :rtype: CapitainsCtsPassage, ContextPassage
        :returns: Asked passage
        """
        if subreference is None:
            return self._getSimplePassage()

        if not isinstance(subreference, CtsReference):
            if isinstance(subreference, str):
                subreference = CtsReference(subreference)
            elif isinstance(subreference, list):
                subreference = CtsReference(".".join(subreference))

        if len(subreference.start) > self.citation.root.depth:
            raise CitationDepthError("URN is deeper than citation scheme")

        if simple is True:
            return self._getSimplePassage(subreference)

        if not subreference.is_range():
            start = end = subreference.start.list
        else:
            start, end = subreference.start.list, subreference.end.list

        citation_start = self.citation.root[len(start)-1]
        citation_end = self.citation.root[len(end)-1]

        start, end = citation_start.fill(passage=start), citation_end.fill(passage=end)
        start, end = normalizeXpath(start.split("/")[2:]), normalizeXpath(end.split("/")[2:])

        xml = self.textObject.xml

        if isinstance(xml, etree._Element):
            root = copyNode(xml)
        else:
            root = copyNode(xml.getroot())

        root = passageLoop(xml, root, start, end)

        if self.urn:
            urn = URN("{}:{}".format(self.urn, subreference))
        else:
            urn = None

        return CapitainsCtsPassage(
            urn=urn,
            resource=root,
            text=self,
            citation=citation_start,
            reference=subreference
        )

    def _getSimplePassage(self, reference=None):
        """ Retrieve a single node representing the passage.

        .. warning:: Range support is awkward.

        :param reference: Identifier of the subreference / passages
        :type reference: list, reference
        :returns: Asked passage
        :rtype: CapitainsCtsPassage
        """
        if reference is None:
            return _SimplePassage(
                resource=self.resource,
                reference=None,
                urn=self.urn,
                citation=self.citation.root,
                text=self
            )

        subcitation = self.citation.root[reference.depth-1]
        resource = self.resource.xpath(
            subcitation.fill(reference),
            namespaces=XPATH_NAMESPACES
        )

        if len(resource) != 1:
            raise InvalidURN

        return _SimplePassage(
            resource[0],
            reference=reference,
            urn=self.urn,
            citation=subcitation,
            text=self.textObject
        )

    @property
    def textObject(self):
        """ Textual Object with full capacities (Unlike Simple CapitainsCtsPassage)

        :rtype: CtsTextMetadata, CapitainsCtsPassage
        :return: Textual Object with full capacities (Unlike Simple CapitainsCtsPassage)
        """
        text = None
        if isinstance(self, CapitainsCtsText):
            text = self
        return text

    def getReffs(self, level: int=1, subreference: CtsReference=None) -> CtsReferenceSet:
        """ CtsReference available at a given level

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :param subreference: Subreference (optional)
        :returns: List of levels
        """

        if not subreference and hasattr(self, "reference"):
            subreference = self.reference
        elif subreference and not isinstance(subreference, CtsReference):
            subreference = CtsReference(subreference)

        return self.getValidReff(level=level, reference=subreference)

    def getValidReff(self, level: int=1, reference: CtsReference=None, _debug: bool=False) -> CtsReferenceSet:
        """ Retrieve valid passages directly

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: int
        :param reference: CapitainsCtsPassage Reference
        :type reference: CtsReference
        :param _debug: Check on passages duplicates
        :type _debug: bool
        :returns: List of levels

        .. note:: GetValidReff works for now as a loop using CapitainsCtsPassage, subinstances of CtsTextMetadata, to retrieve the valid \
        informations. Maybe something is more powerfull ?
        """

        depth = 0
        xml = self.textObject.xml

        if reference:
            if isinstance(reference, CtsReference):
                if not reference.is_range():
                    passages = [reference.start.list]
                    depth = len(passages[0])
                    if level == 0:
                        level = None
                        if _debug:
                            warnings.warn("Using level=0 with a Non-range Reference is invalid. Autocorrected to 1")
                else:
                    xml = self.getTextualNode(subreference=reference)

                    common = []

                    for index, part in enumerate(reference.start.list):
                        if index <= reference.end.depth:
                            if part == reference.end.list[index]:
                                common.append(part)
                            else:
                                break
                        else:
                            break

                    passages = [common]
                    depth = len(common)

                    if level is None:
                        level = reference.start.depth + depth
                    elif level == 1:
                        level = reference.start.depth + 1
                    elif level == 0:
                        level = reference.start.depth
            else:
                raise TypeError()
        else:
            passages = [[]]

        if level is None:
            level = 1

        if level <= len(passages[0]) and reference is not None:
            level = len(passages[0]) + 1
        if level > len(self.citation.root):
            raise CitationDepthError("The required level is too deep")

        nodes = [None] * (level - depth)

        citations = [citation for citation in self.citation.root]

        while len(nodes) >= 1:
            passages = [
                refs + [node.get(current_citation.attribute.replace("xml:", "{http://www.w3.org/XML/1998/namespace}"))]
                for xpath_result, refs, current_citation in [
                        (
                            xml.xpath(
                                citations[len(filling)-1].fill(filling),
                                namespaces=XPATH_NAMESPACES
                            ),
                            refs,
                            citations[len(filling)-1]
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
            duplicates = set()
            seen = set()
            for n in passages:
                if n in seen:
                    duplicates.add(n)
                else:
                    seen.add(n)
            if len(duplicates) > 0:
                message = ", ".join(duplicates)
                warnings.warn(message, DuplicateReference)
            del duplicates
            empties = [n for n in passages if n.rstrip('.') != n or n == '']
            if len(empties) > 0:
                message = '{} empty reference(s) at citation level {}'.format(len(empties), level)
                warnings.warn(message, EmptyReference)

        references = CtsReferenceSet(
            [CtsReference(reff) for reff in passages],
            citation=self.citation.root[level-1],
            level=level
        )
        return references

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
        """ Transform the CapitainsCtsPassage in XML string

        :param args: Ordered arguments for etree.tostring() (except the first one)
        :param kwargs: Named arguments
        :return:
        """
        return etree.tostring(self.resource, *args, **kwargs)


class _SimplePassage(_SharedMethods, PrototypeCtsPassage):
    """ CapitainsCtsPassage for simple and quick parsing of texts

    :param resource: Element representing the passage
    :type resource: etree._Element
    :param reference: CapitainsCtsPassage reference
    :type reference: CtsReference
    :param urn: URN of the source text or of the passage
    :type urn: URN
    :param citation: XmlCtsCitation scheme of the text
    :type citation: Citation
    :param text: CtsTextMetadata containing the passage
    :type text: CapitainsCtsText
    """
    def __init__(self, resource, reference, citation, text, urn=None):
        super(_SimplePassage, self).__init__(
            resource=resource,
            citation=citation,
            **_make_passage_kwargs(urn, reference)
        )
        self._text = text
        self._reference = reference
        self._children = None
        self._depth = 0
        if reference is not None:
            self._depth = reference.depth
        self._prev_next = None

    @property
    def reference(self):
        """ URN CapitainsCtsPassage CtsReference

        :return: CtsReference
        :rtype: CtsReference
        """
        return self._reference

    @reference.setter
    def reference(self, value):
        self._reference = value

    @property
    def childIds(self):
        """ Children of the passage

        :rtype: None, CtsReference
        :returns: Dictionary of chidren, where key are subreferences
        """
        if self.depth >= len(self.citation.root):
            return []
        elif self._children is not None:
            return self._children
        else:
            self._children = self.getReffs()
            return self._children

    def getReffs(self, level=1, subreference=None) -> CtsReferenceSet:
        """ Reference available at a given level

        :param level: Depth required. If not set, should retrieve first encountered level (1 based). 0 retrieves inside
            a range
        :param subreference: Subreference (optional)
        :returns: List of levels
        """
        level += self.depth
        if not subreference:
            subreference = self.reference
        return self.textObject.getValidReff(level, reference=subreference)

    def getTextualNode(self, subreference: CtsReference=None):
        """ Special GetPassage implementation for SimplePassage (Simple is True by default)

        :param subreference:
        :return:
        """
        if not isinstance(subreference, CtsReference):
            subreference = CtsReference(subreference)
        return self.textObject.getTextualNode(subreference)

    @property
    def nextId(self):
        """ Next passage

        :returns: Next passage at same level
        :rtype: None, CtsReference
        """
        return self.siblingsId[1]

    @property
    def prevId(self) -> Optional[CtsReference]:
        """ Get the Previous passage reference

        :returns: Previous passage reference at the same level
        :rtype: None, CtsReference
        """
        return self.siblingsId[0]

    @property
    def siblingsId(self) -> Tuple[CtsReference, CtsReference]:
        """ Siblings Identifiers of the passage

        :rtype: (str, str)
        """

        if not self._text:
            raise MissingAttribute("CapitainsCtsPassage was iniated without CtsTextMetadata object")
        if self._prev_next is not None:
            return self._prev_next

        document_references = self._text.getReffs(level=self.depth)

        range_length = 1
        if self.reference.is_range():
            range_length = len(self.getReffs())

        start = document_references.index(self.reference.start)

        if start == 0:
            # If the passage is already at the beginning
            _prev = None
        elif start - range_length < 0:
            _prev = document_references[0]
        else:
            _prev = document_references[start - 1]

        if start + 1 == len(document_references):
            # If the passage is already at the end
            _next = None
        elif start + range_length > len(document_references):
            _next = document_references[-1]
        else:
            _next = document_references[start + 1]

        self._prev_next = (_prev, _next)
        return self._prev_next

    @property
    def textObject(self):
        """ CtsTextMetadata Object. Required for NextPrev

        :rtype: CapitainsCtsText
        """
        return self._text


class CapitainsCtsText(_SharedMethods, PrototypeCtsText):
    """ Implementation of CTS tools for local files

    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference._capitains_cts.URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param citation: Highest XmlCtsCitation level
    :type citation: Citation
    :param autoreffs: Parse references on load (default : True)
    :type autoreffs: bool
    :ivar resource: lxml
    """

    def __init__(self, urn=None, citation=None, resource=None):
        super(CapitainsCtsText, self).__init__(urn=urn, citation=citation, resource=resource)

        if self.resource is not None:
            self._findCRefPattern(self.resource)

    def _findCRefPattern(self, xml):
        """ Find CRefPattern in the text and set object.citation
        :param xml: Xml Resource
        :type xml: lxml.etree._Element
        :return: None
        """
        if not self.citation.is_set():
            citation = xml.xpath("//tei:refsDecl[@n='CTS']", namespaces=XPATH_NAMESPACES)
            if len(citation):
                self.citation = Citation.ingest(resource=citation[0], xpath=".//tei:cRefPattern")
            else:
                raise MissingRefsDecl("No reference declaration (refsDecl) found.")

    def test(self):
        """ Parse the object and generate the children
        """
        try:
            xml = self.xml.xpath(self.citation.scope, namespaces=XPATH_NAMESPACES)
            if len(xml) == 0:
                msg = "Main citation scope does not result in any result ({0})".format(self.citation.scope)
                raise RefsDeclError(msg)
        except Exception as E:
            raise E


class CapitainsCtsPassage(_SharedMethods, PrototypeCtsPassage):
    """ CapitainsCtsPassage class for local texts which rebuilds the tree up to the passage.

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

        :param reference: CapitainsCtsPassage reference
        :type reference: CtsReference
        :param urn: URN of the source text or of the passage
        :type urn: URN
        :param citation: XmlCtsCitation scheme of the text
        :type citation: XmlCtsCitation
        :param resource: Element representing the passage
        :type resource: etree._Element
        :param text: CtsTextMetadata containing the passage
        :type text: CtsTextMetadata

        .. note::
            .prev, .next, .first and .last won't run on passage with a range made of two different level, such as
            1.1-1.2.3 or 1-a.b. Those will raise `InvalidSiblingRequest`

    """
    def __init__(self, reference, urn=None, citation=None, resource=None, text=None):

        super(CapitainsCtsPassage, self).__init__(
            citation=citation,
            resource=resource,
            **_make_passage_kwargs(urn, reference)
        )
        if urn is not None and urn.reference is not None:
            reference = urn.reference
        self._reference = reference
        self._text = text
        self._children = None
        self._depth = self._depth_2 = 1

        if self.reference and self.reference.start:
            self._depth_2 = self._depth = self.reference.start.depth
        if self.reference.is_range() and self.reference.end:
            self._depth_2 = self.reference.end.depth

        self._prev_next = None  # For caching purpose

    @property
    def reference(self):
        """ CtsReference of the object
        """
        return self._reference

    @property
    def childIds(self):
        """ Children of the passage

        :rtype: None, CtsReference
        :returns: Dictionary of chidren, where key are subreferences
        """
        self._raise_depth()
        if self.depth >= len(self.citation.root):
            return []
        elif self._children is not None:
            return self._children
        else:
            self._children = self.getReffs()
            return self._children

    @property
    def nextId(self):
        """ Next passage

        :returns: Next passage at same level
        :rtype: None, CtsReference
        """
        return self.siblingsId[1]

    @property
    def prevId(self):
        """ Get the Previous passage reference

        :returns: Previous passage reference at the same level
        :rtype: None, CtsReference
        """
        return self.siblingsId[0]

    def _raise_depth(self):
        """ Simple check that raises an exception if the passage cannot run first, last, next or prev

        See object notes

        :raise: InvalidSiblingRequest
        """
        if self._depth != self._depth_2:
            raise InvalidSiblingRequest()

    @property
    def siblingsId(self) -> Tuple[CtsReference, CtsReference]:
        """ Siblings Identifiers of the passage

        :rtype: (str, str)
        """
        self._raise_depth()

        if not self._text:
            raise MissingAttribute("CapitainsCtsPassage was initiated without CtsTextMetadata object")
        if self._prev_next:
            return self._prev_next

        document_references = self._text.getReffs(level=self.depth)

        if self.reference.is_range():
            start, end = self.reference.start, self.reference.end
            range_length = len(self.getReffs(level=0))
        else:
            start = end = self.reference.start
            range_length = 1

        start = document_references.index(start)
        end = document_references.index(end)

        if start == 0:
            # If the passage is already at the beginning
            _prev = None
        elif start - range_length < 0:
            if start == end:
                _prev = document_references[0]
            else:
                _prev = "{}-{}".format(document_references[0], document_references[start-1])
        else:
            if start == end:
                _prev = document_references[start-1]
            else:
                _prev = "{}-{}".format(document_references[start-range_length], document_references[start-1])

        if start + 1 == len(document_references) or end + 1 == len(document_references):
            # If the passage is already at the end
            _next = None
        elif end + range_length > len(document_references):
            if start == end:
                _next = document_references[-1]
            else:
                _next = "{}-{}".format(document_references[end+1], document_references[-1])
        else:
            if start == end:
                _next = document_references[end+1]
            else:
                _next = "{}-{}".format(document_references[end+1], document_references[end + range_length])

        self._prev_next = (CtsReference(_prev), CtsReference(_next))
        return self._prev_next

    @property
    def next(self):
        """ Next CapitainsCtsPassage (Interactive CapitainsCtsPassage)
        """
        if self.nextId is not None:
            return super(CapitainsCtsPassage, self).getTextualNode(subreference=self.nextId)

    @property
    def prev(self):
        """ Previous CapitainsCtsPassage (Interactive CapitainsCtsPassage)
        """
        if self.prevId is not None:
            return super(CapitainsCtsPassage, self).getTextualNode(subreference=self.prevId)

    def getTextualNode(self, subreference=None, *args, **kwargs):
        if not isinstance(subreference, CtsReference):
            subreference = CtsReference(subreference)
        X = super(CapitainsCtsPassage, self).getTextualNode(subreference=subreference)
        X._text = self._text
        return X

    @property
    def textObject(self):
        """ CtsTextMetadata Object. Required for NextPrev

        :rtype: CapitainsCtsText
        """
        return self._text
