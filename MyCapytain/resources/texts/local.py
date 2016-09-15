# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml


Local files handler for CTS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from collections import OrderedDict, defaultdict
from past.builtins import basestring
import warnings

from MyCapytain.errors import DuplicateReference, RefsDeclError
from MyCapytain.common.utils import xmlparser, NS, copyNode, passageLoop, normalizeXpath, normalize, \
    nested_set, nested_ordered_dictionary
from MyCapytain.common.reference import URN, Citation, Reference
from MyCapytain.resources.proto import text
from MyCapytain.errors import InvalidSiblingRequest
import MyCapytain.resources.texts.tei
from lxml import etree


class Text(text.Text):
    """ Implementation of CTS tools for local files

    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param citation: Highest Citation level
    :type citation: MyCapytain.common.reference.Citation
    :param autoreffs: Parse references on load (default : True)
    :type autoreffs: bool
    :ivar resource: lxml
    """

    def __init__(self, urn=None, citation=None, resource=None, autoreffs=False):
        super(Text, self).__init__(urn=urn, citation=citation)
        self._passages = Passage()
        self._orphan = defaultdict(Reference)  # Represents passage we got without asking for all. Storing convenience ?

        self._cRefPattern = MyCapytain.resources.texts.tei.Citation()
        self.xml = None

        if citation is not None:
            self.citation = citation

        if resource is not None:
            self.resource = resource
            self.xml = xmlparser(resource)
            self.__findCRefPattern(self.xml)

            if autoreffs is True:
                self.parse()

    def __findCRefPattern(self, xml):
        """ Find CRefPattern in the text and set object.citation
        :param xml: Xml Resource
        :return: None
        """
        self.citation = MyCapytain.resources.texts.tei.Citation.ingest(
            resource=xml.xpath("//tei:refsDecl[@n='CTS']", namespaces=MyCapytain.common.utils.NS),
            xpath=".//tei:cRefPattern"
        )

    def parse(self):
        """ Parse the object and generate the children
        """
        try:
            xml = self.xml.xpath(self.citation.scope, namespaces=NS)[0]
        except IndexError:
            msg = "Main citation scope does not result in any result ({0})".format(self.citation.scope)
            raise RefsDeclError(msg)
        except Exception as E:
            raise E

        self._passages = Passage(resource=xml, citation=self.citation, urn=self.urn, reference=None)

    @property
    def citation(self):
        """ Get the lowest cRefPattern in the hierarchy

        :rtype: Citation
        """
        return self._cRefPattern

    @citation.setter
    def citation(self, value):
        """ Set the cRefPattern

        :param value: Citation to be saved
        :type value: Citation
        :raises: TypeError when value is not a TEI Citation or a Citation
        """
        if isinstance(value, MyCapytain.resources.texts.tei.Citation):
            self._cRefPattern = value
        elif isinstance(value, Citation):
            # .. todo:: Should support conversion between Citation...
            self._cRefPattern = MyCapytain.resources.texts.tei.Citation(
                name=value.name,
                refsDecl=value.refsDecl,
                child=value.child
            )

    def nested_dict(self, exclude=None):
        """ Nested Dict Representation of the text passages

        :param exclude: Remove some nodes from text according to `MyCapytain.resources.texts.tei.Passage.text`
        :type exclude: List
        :rtype: dict
        :returns: Dictionary
        """
        reffs = self.getValidReff(level=len(self.citation))
        text = nested_ordered_dictionary()
        for reff in reffs:
            _r = reff.split(".")
            nested_set(text, _r, self.getPassage(_r, hypercontext=False).text(exclude=exclude))
        return text

    def getPassage(self, reference, hypercontext=True):
        """ Finds a passage in the current text

        :param reference: Identifier of the subreference / passages
        :type reference: list, Reference
        :param hypercontext: If set to true, retrieves nodes up to the given one, cleaning non required siblings.
        :type hypercontext: bool
        :rtype: Passage, ContextPassage
        :returns: Asked passage

        .. note :: As of MyCapytain 0.1.0, Text().getPassage() returns by default a ContextPassage, thus being able
            to handle range. This design change also means that the returned tree is way different that a classic
             Passage. To retrieve MyCapytain<=0.0.9 behaviour, use `hypercontext=False`.
        """
        if hypercontext is True:
            return self._getPassageContext(reference)

        if isinstance(reference, Reference):
            reference = reference.list or reference.start.list

        if self._passages.resource is None:
            self.parse()

        reference = [".".join(reference[:i]) for i in range(1, len(reference) + 1)]
        passages = [self._passages]
        while len(reference) > 0:
            passages = [passage for sublist in [p.get(reference[0]) for p in passages] for passage in sublist]
            reference.pop(0)

        return passages[0]

    def _getPassageContext(self, reference):
        """ Retrieves nodes up to the given one, cleaning non required siblings.

        :param reference: Identifier of the subreference / passages
        :type reference: list, reference
        :returns: Asked passage
        :rtype: ContextPassage
        """
        if isinstance(reference, list):
            start, end = reference, reference
            reference = Reference(".".join(reference))
        elif not reference.end:
            start, end = reference.start.list, reference.start.list
        else:
            start, end = reference.start.list, reference.end.list

        if len(start) > len(self.citation):
            raise ReferenceError("URN is deeper than citation scheme")

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
        return ContextPassage(
            urn=urn,
            resource=root, parent=self, citation=self.citation
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

    def text(self, exclude=None):
        """ Returns the text of the XML resource without the excluded nodes

        :param exclude: List of nodes
        :type exclude: list(str)
        :return: Text of the text without the text inside removed nodes
        :rtype: str

        .. example::
            `epigrammata.exclude(["tei:note"])` would remove all note nodes of the XML and print the text

        """
        return self._passages.text(exclude=exclude)


class Passage(MyCapytain.resources.texts.tei.Passage):
    """ Passage class for local texts which is fast but contains the minimum DOM.

        For design purposes, some people would prefer passage to be found quickly (Text indexing for example).
        Passage keeps only the node found through the xpath

        **Example** :  for a text with a citation scheme with following refsDecl :
        `/TEI/text/body/div[@type='edition']/div[@n='$1']/div[@n='$2']/l[@n='$3']` and a passage 1.1.1, this
        class will build an XML tree looking like the following

         .. code-block:: xml

            <l n='1'>Lorem ipsum</l>

    :param urn: A URN identifier
    :type urn: URN
    :param resource: A resource
    :type resource: etree._Element
    :param parent: Parent of the current passage
    :type parent: Passage
    :param citation: Citation for children level
    :type citation: Citation
    :param reference: Identifier of the subreference without URN information
    :type reference: Reference, List

    .. warning:: This passage system does not accept range
    """

    def __init__(self, urn=None, resource=None, parent=None, citation=None, reference=None):
        super(Passage, self).__init__(resource=resource, parent=parent)

        self.__next = False
        self.__prev = False

        self.citation = None
        if isinstance(citation, Citation):
            self.citation = citation

        self.__reference = Reference("")
        if urn:
            self.urn = urn
        if reference:
            self.reference = reference

        self.__children = OrderedDict()
        self.__parsed = False

    @property
    def reference(self):
        """ Id represents the passage subreference as a list of basestring

        :returns: Representation of the passage subreference as a list
        :rtype: Reference
        """
        return self.__reference

    @reference.setter
    def reference(self, value):
        """ Set up ID property

        :param value: Representation of the passage subreference as a list
        :type value: list, tuple, Reference

        .. note:: `Passage.id = [..]` will update automatically the URN property as well if correct
        """
        _value = None
        if isinstance(value, (list, tuple)):
            _value = Reference(".".join(value))
        elif isinstance(value, basestring):
            _value = Reference(value)
        elif isinstance(value, Reference):
            _value = value

        if _value and self.__reference != _value:
            self.__reference = _value
            if self._URN and len(self._URN):
                if len(value):
                    self._URN = URN("{}:{}".format(self._URN.upTo(URN.NO_PASSAGE), str(_value)))
                else:
                    self._URN = URN(self._URN["text"])

    @property
    def urn(self):
        """ URN Identifier of the object

        :rtype: URN
        """
        return self._URN

    @urn.setter
    def urn(self, value):
        """ Set the urn

        :param value: URN to be saved
        :type value: URN, basestring, str
        :raises: *TypeError* when the value is not URN compatible

        .. note:: `Passage.URN = ...` will update automatically the id property if Passage is set

        """
        a = self._URN

        if isinstance(value, basestring):
            value = URN(value)
        elif not isinstance(value, URN):
            raise TypeError()

        if str(a) != str(value):
            self._URN = value

            if value.reference and self.__reference != value.reference:
                self.__reference = value.reference
            elif not value.reference and self.__reference and len(self.__reference):
                self._URN = URN("{}:{}".format(str(value), str(self.__reference)))

    def get(self, key=None):
        """ Get a child or multiple children

        :param key: String identifying a passage
        :type key: basestring or int 
        :raises KeyError: When key identifies a child unknown to this passage
        :rtype: List.Passage
        :returns: List of passage identified by key. If key is None, returns all children
        
        .. note:: Call time depends on parsing status. If the passage was never parsed, then on first call citation is used to find children
        """
        if len(self.__children) == 0 and self.__parsed is False:
            self.__parse()

        if key is None:
            return [self.__children[key] for key in self.__children]
        elif isinstance(key, int):
            keys = list(self.__children.copy().keys())
            return [self.__children[keys[key]]]
        elif key not in self.__children:
            raise KeyError()
        else:
            return [self.__children[key]]

    def __parse(self):
        """ Private method for parsing children
        """
        if self.citation is None:
            self.__parsed = True
            return []

        elements = self.resource.xpath("."+self.citation.fill(passage=None, xpath=True), namespaces=NS)
        ids = [self.reference.list+[element.get("n")] for element in elements]
        ns = [".".join(_id) for _id in ids]

        # Checking for duplicates
        duplicates = set([n for n in ns if ns.count(n) > 1])
        if len(duplicates) > 0:
            message = ", ".join(duplicates)
            warnings.warn(message, DuplicateReference)

        for element, _id, n in zip(elements, ids, ns):
            self.__children[n] = Passage(
                resource=element,
                citation=self.citation.child,
                reference=_id,
                urn=self.urn,
                parent=self
            )
        self.__parsed = True

    @property
    def first(self):
        """ First child of current Passage 

        :returns: None if current Passage has no children,  first child passage if available
        :rtype: None, Passage
        """
        try:
            return self.get(0)[0]
        except:
            return None

    @property
    def last(self):
        """ Last child of current Passage 

        :returns: None if current Passage has no children, last child passage if available
        :rtype: None, Passage
        """
        try:
            return self.get(-1)[0]
        except :
            return None

    @property
    def children(self):
        """ Children of the passage

        :returns: Dictionary of chidren, where key are subreferences
        :rtype: OrderedDict
        """
        if len(self.__children) == 0 and self.__parsed is False:
            self.__parse()

        return self.__children
    
    @property
    def next(self):
        """ Next passage 

        :returns: Next passage at same level
        :rtype: Passage
        """ 
        if self.__next is False:

            if self.parent is None:  # When top of hierarchy is access, should return None
                self.__next = None
                return None

            keys = list(self.parent.children.copy().keys())
            current = keys.index(str(self.reference))
            if len(keys) - 1 > current:
                self.__next = self.parent.get(keys[current + 1])[0]
            else:
                n = self.parent.next
                if n is None:
                    self.__next = None
                else:
                    self.__next = n.first

        return self.__next

    @property
    def prev(self):
        """ Previous passage 

        :returns: Previous passage at same level
        :rtype: Passage
        """ 
        if self.__prev is False:

            if self.parent is None:  # When top of hierarchy is access, should return None
                self.__prev = None
                return None

            keys = list(self.parent.children.copy().keys())
            current = keys.index(str(self.reference))
            if current > 0:
                self.__prev = self.parent.get(keys[current - 1])[0]
            else:
                n = self.parent.prev
                if n is None:
                    self.__prev = None
                else:
                    self.__prev = n.last

        return self.__prev


class ContextPassage(Passage):
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
        :param parent: Text containing the passage
        :type parent: Text
        :param citation: Citation scheme of the text
        :type citation: Citation
        :param reference: Passage reference
        :type reference: Reference

        .. note::
            .prev, .next, .first and .last won't run on passage with a range made of two different level, such as
            1.1-1.2.3 or 1-a.b. Those will raise `InvalidSiblingRequest`

    """
    def __init__(self, urn=None, resource=None, parent=None, citation=None, reference=None):
        super(ContextPassage, self).__init__(urn=urn, reference=reference)

        if isinstance(resource, etree._Element):
            if urn:
                self.resource = Text(resource=resource, urn=urn.upTo(URN.NO_PASSAGE), citation=parent.citation)
            else:
                self.resource = Text(resource=resource, citation=parent.citation)
        else:
            self.resource = resource
        self.parent = parent
        self.citation = parent.citation
        self.__children = None

        self.depth = self.depth_2 = 1

        if self.reference.start:
            self.depth_2 = self.depth = len(self.reference.start)
        if self.reference and self.reference.end:
            self.depth_2 = len(self.reference.end)

        self.__prevnext = None  # For caching purpose

    def xpath(self, *args, **kwargs):
        """ Perform XPath on the passage XML

        :param args: Ordered arguments for etree._Element().xpath()
        :param kwargs: Named arguments
        :return: Result list
        :rtype: list(etree._Element)
        """
        if "smart_strings" not in kwargs:
            kwargs["smart_strings"] = False
        return self.resource.resource.xpath(*args, **kwargs)

    def tostring(self, *args, **kwargs):
        """ Transform the Passage in XML string

        :param args: Ordered arguments for etree.tostring() (except the first one)
        :param kwargs: Named arguments
        :return:
        """
        return etree.tostring(self.resource.resource, *args, **kwargs)

    def __str__(self):
        """ Text based representation of the passage

        :returns: XML of the passage in string form
        :rtype: basestring
        """
        return self.tostring(encoding=str)

    @property
    def first(self):
        """ First child of current Passage

        :returns: None if current Passage has no children,  first child passage if available
        :rtype: None, Reference
        """
        if self.depth >= len(self.citation):
            return None
        else:
            return self.children[0]

    @property
    def last(self):
        """ Last child of current Pass

        :returns: None if current Passage has no children, last child passage if available
        :rtype: None, Reference
        """
        if self.depth >= len(self.citation):
            return None
        else:
            return self.children[-1]

    @property
    def children(self):
        """ Children of the passage

        :rtype: None, Reference
        :returns: Dictionary of chidren, where key are subreferences
        """
        self.__raiseDepth()
        if self.depth >= len(self.citation):
            return []
        elif self.__children and len(self.__children):
            return self.__children
        else:
            self.__children = self.resource.getValidReff(level=self.depth+1)
            return self.__children

    @property
    def next(self):
        """ Next passage

        :returns: Next passage at same level
        :rtype: None, Reference
        """
        return self.__getSiblings(direction=1)

    @property
    def prev(self):
        """ Get the Previous passage reference

        :returns: Previous passage reference at the same level
        :rtype: None, Reference
        """
        return self.__getSiblings(direction=0)

    def text(self, exclude=None):
        """ Text content of the passage

        :param exclude: Remove some nodes from text
        :type exclude: List
        :rtype: basestring
        :returns: Text of the xml node
        :Example:
            >>>    P = Passage(resource='<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>')
            >>>    P.text == "Ibis hello b ab excusso missus in astra sago. "
            >>>    P.text(exclude=["note"]) == "Ibis ab excusso missus in astra sago. "


        """

        if exclude is None:
            exclude = ""
        else:
            exclude = "[{0}]".format(
                " and ".join(
                    "not(./ancestor-or-self::{0})".format(excluded)
                    for excluded in exclude
                )
            )

        return normalize(
            " ".join(
                [
                    element
                    for element
                    in self.xpath(
                        ".//descendant-or-self::text()" + exclude,
                        namespaces=NS
                    )
                ]
            )
        )

    def __raiseDepth(self):
        """ Simple check that raises an exception if the passage cannot run first, last, next or prev

        See object notes

        :raise: InvalidSiblingRequest
        """
        if self.depth != self.depth_2:
            raise InvalidSiblingRequest()

    def __getSiblings(self, direction=1):
        """

        :return: Reference
        """
        self.__raiseDepth()

        if self.__prevnext:
            return self.__prevnext[direction]

        document_references = list(map(lambda x: str(x), self.parent.getValidReff(level=self.depth)))
        range_length = len(self.resource.getValidReff(level=self.depth))

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

        self.__prevnext = (_prev, _next)
        return self.__prevnext[direction]

