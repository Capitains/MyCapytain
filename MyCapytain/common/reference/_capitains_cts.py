import re
from typing import Optional, List, Union, Tuple
from lxml.etree import _Element

from MyCapytain.common.constants import Mimetypes, get_graph, RDF_NAMESPACES, XPATH_NAMESPACES
from MyCapytain.common.utils.xml import make_xml_node

from ._base import BaseCitation, BaseReference, BaseReferenceSet

REFSDECL_SPLITTER = re.compile(r"/+[*()|\sa-zA-Z0-9:\[\]@=\\{$'\".\s]+")
REFSDECL_REPLACER = re.compile(r"\$[0-9]+")
SUBREFERENCE = re.compile(r"(\w*)\[?([0-9]*)\]?", re.UNICODE)
REFERENCE_REPLACER = re.compile(r"(@[a-zA-Z0-9:]+)(=)([\\$'\"?0-9]{3,6})")


def _child_or_none(liste):
    """ Used to parse resources in XmlCtsCitation

    :param liste: List of item
    :return: If there is > 1 element in the list, return the last one
    """
    if len(liste) > 0:
        return liste[-1]
    else:
        return None


class CtsWordReference(str):
    """ A CTSWordReference is the specific part of a CTS identifier that
    identifies a word in a given passage. It contains the text in its
    .word property and the index of this word in its .counter identifier

    It can be returned as a tuple using .tuple()

    """
    def __new__(cls, word_reference: str):
        word, counter = tuple(SUBREFERENCE.findall(word_reference)[0])

        if counter:
            counter = int(counter)
        else:
            counter = 0

        obj = str.__new__(cls, "@"+word_reference)
        obj.counter = counter
        obj.word = word

        return obj

    def tuple(self) -> Tuple[str, int]:
        return self.word, self.counter

    def __iter__(self):
        return iter([self.word, self.counter])


class CtsSinglePassageId(str):
    """ A CtsSinglePassageId identifies part of a range, or a non-range passage
    such as 1.1.1 or 1.2.2 in 1.2.2-1.2.3.

    It provides a list version of itself through the .list property and
    links to its subreference using the .subreference property (Word and Index identifier)

    If you iter over it, it returns each passage of the hierarchy, so

    >>> iter((CtsSinglePassageId("1.2.3"))) == iter(["1", "2", "3"])

    len() and .depth returns the depth of the passage

    >>> (CtsSinglePassageId("1.2.4")).depth == 3
    >>> len(CtsSinglePassageId("1.2.4")) == 3
    """
    def __new__(cls, str_repr: str):
        # Saving the original ID
        obj = str.__new__(cls, str_repr)

        # Setting up the properties that can be None
        obj._sub_reference = None

        # Parsing the reference
        temp_str_repr = str_repr
        subreference = temp_str_repr.split("@")

        if len(subreference) == 2:
            obj._sub_reference = CtsWordReference(subreference[1])
            temp_str_repr = subreference[0]

        obj._list = temp_str_repr
        return obj

    @property
    def list(self) -> List[str]:
        return list(iter(self))

    @property
    def subreference(self) -> Optional[CtsWordReference]:
        subref = self.split("@")
        if len(subref) == 2:
            return CtsWordReference(subref[1])

    def __iter__(self) -> List[str]:
        subref = self.split("@")[0]
        yield from subref.split(".")

    def __len__(self) -> int:
        return self.count(".") + 1

    @property
    def depth(self) -> int:
        return self.count(".") + 1


class CtsReference(BaseReference):
    """ A reference object giving information

    :Example:
        >>>    a = CtsReference("1.1@Achiles[1]-1.2@Zeus[1]")
        >>>    b = CtsReference("1.1")
        >>>    CtsReference("1.1-2.2.2").highest == CtsSinglePassageId("1.1")

    Reference object supports the following magic methods : len(), str() and eq().

    :Example:
        >>>    len(a) == 2 && len(b) == 1
        >>>    str(a) == "1.1@Achiles[1]-1.2@Zeus[1]"
        >>>    b == CtsReference("1.1") && b != a

    .. note::
        Reference(...).subreference and .list are not available for range. You will need to convert .start or .end to
        a Reference

        >>>    ref = CtsReference('1.2.3')
    """

    def __new__(cls, *references):
        # pickle.load will try to feed the tuple back !
        if len(references) == 2:
            start, end = references
            o = BaseReference.__new__(
                CtsReference,
                CtsSinglePassageId(start),
                CtsSinglePassageId(end)
            )
            o._str_repr = start + "-" + end
            return o

        references, *_ = references
        if not references:
            return None
        elif isinstance(references, tuple):
            if references[1]:
                o = BaseReference.__new__(
                    CtsReference,
                    CtsSinglePassageId(references[0]),
                    CtsSinglePassageId(references[1])
                )
            else:
                o = BaseReference.__new__(
                    CtsReference,
                    CtsSinglePassageId(references[0])
                )
            o._str_repr = "-".join([r for r in references if r])

        elif isinstance(references, str):
            if "-" not in references:
                o = BaseReference.__new__(CtsReference, CtsSinglePassageId(references))
            else:
                _start, _end = tuple(references.split("-"))
                o = BaseReference.__new__(CtsReference, CtsSinglePassageId(_start), CtsSinglePassageId(_end))
            o._str_repr = references

        return o

    @property
    def parent(self) -> Optional['CtsReference']:
        """ Parent of the actual URN, for example, 1.1 for 1.1.1

        :rtype: CtsReference
        """
        if self.start.depth == 1 and (self.end is None or self.end.depth <= 1):
            return None
        else:
            if self.start.depth > 1 and (self.end is None or self.end.depth == 0):
                return CtsReference("{0}{1}".format(
                    ".".join(self.start.list[:-1]),
                    self.start.subreference or ""
                ))
            elif self.start.depth > 1 and self.end is not None and self.end.depth > 1:
                _start = self.start.list[0:-1]
                _end = self.end.list[0:-1]
                if _start == _end and \
                        self.start.subreference is None and \
                        self.end.subreference is None:
                    return CtsReference(
                        ".".join(_start)
                    )
                else:
                    return CtsReference("{0}{1}-{2}{3}".format(
                        ".".join(_start),
                        self.start.subreference or "",
                        ".".join(_end),
                        self.end.subreference or ""
                    ))

    @property
    def highest(self) -> CtsSinglePassageId:
        """ Return highest reference level

        For references such as 1.1-1.2.8, with different level, it can be useful to access to the highest node in the
        hierarchy. In this case, the highest level would be 1.1. The function would return ["1", "1"]

        .. note:: By default, this property returns the start level

        :rtype: CtsReference
        """
        if not self.end:
            return self.start
        elif len(self.start) < len(self.end) and len(self.start):
            return self.start
        elif len(self.start) > len(self.end) and len(self.end):
            return self.end
        elif len(self.start):
            return self.start

    @property
    def start(self) -> CtsSinglePassageId:
        """ Quick access property for start list

        :rtype: str
        """
        return super(CtsReference, self).start

    @property
    def end(self) -> CtsSinglePassageId:
        """ Quick access property for reference end list

        :rtype: str
        """
        return super(CtsReference, self).end

    @property
    def subreference(self):
        """ Return the subreference of a single node reference

        .. note:: Access to start and end subreference should be done through obj.start.subreference \
        and obj.end.subreference

        :rtype: (str, int)
        """
        if not self.end:
            return self.start.subreference

    @property
    def depth(self):
        """ Return depth of highest reference level

        For references such as 1.1-1.2.8, or simple references such as 1.a, with different level, it can be useful to
        know the depth of the reference to access the right XPath for example. This property returns the depth of the
        highest node

        :example:
            - len(1.1) == 2
            - len(1.2.8-1.3) == 2
            - len(1-1.2) == 1

        :rtype: int
        """
        return len(self.highest.list)

    def __str__(self):
        """ Return full reference in string format

        :rtype: str
        :returns: String representation of Reference Object

        :Example:
            >>>    a = CtsReference("1.1@Achiles[1]-1.2@Zeus[1]")
            >>>    b = CtsReference("1.1")
            >>>    str(a) == "1.1@Achiles[1]-1.2@Zeus[1]"
            >>>    str(b) == "1.1"
        """
        return self._str_repr


class CtsReferenceSet(BaseReferenceSet):
    """ A CTS version of the BaseReferenceSet

    """
    def __contains__(self, item: str) -> bool:
        return BaseReferenceSet.__contains__(self, item) or \
               BaseReferenceSet.__contains__(self, CtsReference(item))

    def index(self, obj: Union[str, CtsReference], *args, **kwargs) -> int:
        _o = obj
        if not isinstance(obj, CtsReference):
            _o = CtsReference(obj)
        return super(CtsReferenceSet, self).index(_o)


class URN(object):
    """ A URN object giving all useful sections

    :param urn: A CTS URN
    :type urn: str
    :cvar NAMESPACE: Constant representing the URN until its namespace
    :cvar TEXTGROUP: Constant representing the URN until its textgroup
    :cvar WORK: Constant representing the URN until its work
    :cvar VERSION: Constant representing the URN until its version
    :cvar PASSAGE: Constant representing the URN until its full passage
    :cvar PASSAGE_START: Constant representing the URN until its passage (end excluded)
    :cvar PASSAGE_END: Constant representing the URN until its passage (start excluded)
    :cvar NO_PASSAGE: Constant representing the URN until its passage excluding its passage
    :cvar COMPLETE: Constant representing the complete URN

    :Example:
        >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")

    URN object supports the following magic methods : len(), str() and eq(), gt() and lt().

    :Example:
        >>>     b = URN("urn:cts:latinLit:phi1294.phi002")
        >>>     a != b
        >>>     a > b # It has more member. Only member count is compared
        >>>     b < a
        >>>     len(a) == 5 # CtsReference is not counted to not induce count equivalencies with the optional version
        >>>     len(b) == 4

    """

    NAMESPACE = 0
    TEXTGROUP = 1
    WORK = 2
    VERSION = 3
    PASSAGE = 4
    PASSAGE_START = 5
    PASSAGE_END = 6
    NO_PASSAGE = 10
    COMPLETE = 100

    def __init__(self, urn):
        self.__urn = None
        self.__parsed = self.__parse__(urn)

    @property
    def urn_namespace(self):
        """ General Namespace element of the URN

        :rtype: str
        :return: Namespace part of the URN
        """
        return self.__parsed["urn_namespace"]

    @urn_namespace.setter
    def urn_namespace(self, value):
        self.__urn = None
        self.__parsed["urn_namespace"] = value

    @property
    def namespace(self):
        """ CTS Namespace element of the URN

        :rtype: str
        :return: Namespace part of the URN
        """
        return self.__parsed["cts_namespace"]

    @namespace.setter
    def namespace(self, value):
        self.__urn = None
        self.__parsed["cts_namespace"] = value

    @property
    def textgroup(self):
        """ Textgroup element of the URN

        :rtype: str
        :return: Textgroup part of the URN
        """
        return self.__parsed["textgroup"]

    @textgroup.setter
    def textgroup(self, value):
        self.__urn = None
        self.__parsed["textgroup"] = value

    @property
    def work(self):
        """ CtsWorkMetadata element of the URN

        :rtype: str
        :return: CtsWorkMetadata part of the URN
        """
        return self.__parsed["work"]

    @work.setter
    def work(self, value):
        self.__urn = None
        self.__parsed["work"] = value

    @property
    def version(self):
        """ Version element of the URN

        :rtype: str
        :return: Version part of the URN
        """
        return self.__parsed["version"]

    @version.setter
    def version(self, value):
        self.__urn = None
        self.__parsed["version"] = value

    @property
    def reference(self):
        """ Reference element of the URN

        :rtype: CtsReference
        :return: Reference part of the URN
        """
        return self.__parsed["reference"]

    @reference.setter
    def reference(self, value):
        self.__urn = None
        if isinstance(value, CtsReference):
            self.__parsed["reference"] = value
        else:
            self.__parsed["reference"] = CtsReference(value)

    def __len__(self):
        """ Returns the len of the URN

        :rtype: int
        :returns: Length of the URN

        .. warning:: Does not take into account the passage !

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
            >>>    print(len(a))
        """

        items = [
            key
            for key, value in self.__parsed.items()
            if key not in ["reference"] and value is not None
        ]
        return len(items)

    def __gt__(self, other):
        """ Allows for greater comparison

        :param other: Comparison object
        :type other: URN
        :rtype: boolean
        :returns: Indicator of bigger size

        .. warning:: Does not take into account the passage !

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
            >>>    b = URN(urn="urn:cts:latinLit:phi1294.phi002:1.1")
            >>>    (a > b) == True
        """
        return len(self) > len(other)

    def __lt__(self, other):
        """ Allows for lower comparison

        :param other: Comparison object
        :type other: URN
        :rtype: boolean
        :returns: Indicator of lower size

        .. warning:: Does not take into account the passage !

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
            >>>    b = URN(urn="urn:cts:latinLit:phi1294.phi002:1.1")
            >>>    (b < a) == True
        """
        return len(self) < len(other)

    def __eq__(self, other):
        """ Equality checker for URN object

        :param other: An object to be checked against
        :type other: URN
        :rtype: boolean
        :returns: Equality between other and self

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
            >>>    b = URN(urn="urn:cts:latinLit:phi1294.phi002:1.1")
            >>>    (b == a) == False
        """
        return isinstance(other, type(self)) and str(self) == str(other)

    def __ne__(self, other):
        """ Inequality checker for CtsReference object

        :param other: An object to be checked against
        :rtype: boolean
        :returns: Equality between other and self
        """
        return not self.__eq__(other)

    def __str__(self):
        """ Return full initial urn

        :rtype: basestring
        :returns: String representation of URN Object

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
            >>>    str(a) == "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        """
        if self.__urn is None:
            urn = "urn:" + self.__parsed["urn_namespace"]
            if self.namespace:
                urn += ":" + self.namespace
                if self.textgroup:
                    urn += ":" + self.textgroup
                    if self.work:
                        urn += "." + self.work
                        if self.version:
                            urn += "." + self.version
                        if self.reference:
                            urn += ":" + str(self.reference)
            self.__urn = urn
        return self.__urn

    def upTo(self, key):
        """ Returns the urn up to given level using URN Constants

        :param key: Identifier of the wished resource using URN constants
        :type key: int
        :returns: String representation of the partial URN requested
        :rtype: str

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
            >>>    a.upTo(URN.TEXTGROUP) == "urn:cts:latinLit:phi1294"
        """
        middle = [
            component
            for component in [self.__parsed["textgroup"], self.__parsed["work"], self.__parsed["version"]]
            if component is not None
        ]

        if key == URN.COMPLETE:
            return self.__str__()
        elif key == URN.NAMESPACE:
            return ":".join([
                "urn",
                self.__parsed["urn_namespace"],
                self.__parsed["cts_namespace"]])
        elif key == URN.TEXTGROUP and self.__parsed["textgroup"]:
            return ":".join([
                "urn",
                self.__parsed["urn_namespace"],
                self.__parsed["cts_namespace"],
                self.__parsed["textgroup"]
            ])
        elif key == URN.WORK and self.__parsed["work"]:
            return ":".join([
                "urn",
                self.__parsed["urn_namespace"],
                self.__parsed["cts_namespace"],
                ".".join([self.__parsed["textgroup"], self.__parsed["work"]])
            ])
        elif key == URN.VERSION and self.__parsed["version"]:
            return ":".join([
                "urn",
                self.__parsed["urn_namespace"],
                self.__parsed["cts_namespace"],
                ".".join(middle)
            ])
        elif key == URN.NO_PASSAGE and self.__parsed["work"]:
            return ":".join([
                "urn",
                self.__parsed["urn_namespace"],
                self.__parsed["cts_namespace"],
                ".".join(middle)
            ])
        elif key == URN.PASSAGE and self.__parsed["reference"]:
            return ":".join([
                "urn",
                self.__parsed["urn_namespace"],
                self.__parsed["cts_namespace"],
                ".".join(middle),
                str(self.reference)
            ])
        elif key == URN.PASSAGE_START and self.__parsed["reference"]:
            return ":".join([
                "urn",
                self.__parsed["urn_namespace"],
                self.__parsed["cts_namespace"],
                ".".join(middle),
                str(self.reference.start)
            ])
        elif key == URN.PASSAGE_END and self.__parsed["reference"] and self.reference.end is not None:
            return ":".join([
                "urn",
                self.__parsed["urn_namespace"],
                self.__parsed["cts_namespace"],
                ".".join(middle),
                str(self.reference.end)
            ])
        else:
            raise KeyError("Provided key is not recognized.")

    @staticmethod
    def model():
        """ Generate a standard dictionary model for URN inside function

        :return: Dictionary of CTS elements
        """
        return {
            "urn_namespace": None,
            "cts_namespace": None,
            "textgroup": None,
            "work": None,
            "version": None,
            "reference": None
        }

    def __parse__(self, urn):
        """ Parse a URN

        :param urn: A URN:CTS
        :type urn: basestring
        :rtype: defaultdict.basestring
        :returns: Dictionary representation
        """
        parsed = URN.model()
        self.__urn = urn.split("#")[0]
        urn = self.__urn.split(":")
        if isinstance(urn, list) and len(urn) > 2:
            parsed["urn_namespace"] = urn[1]
            parsed["cts_namespace"] = urn[2]

            if len(urn) == 5:
                parsed["reference"] = CtsReference(urn[4])

            if len(urn) >= 4:
                urn = urn[3].split(".")
                if len(urn) >= 1:
                    parsed["textgroup"] = urn[0]
                if len(urn) >= 2:
                    parsed["work"] = urn[1]
                if len(urn) >= 3:
                    parsed["version"] = urn[2]
        else:
            raise ValueError("URN is empty")
        return parsed


class Citation(BaseCitation):
    """ A citation object gives informations about the scheme

    :param name: Name of the citation (e.g. "book")
    :type name: basestring
    :param xpath: Xpath of the citation (As described by CTS norm)
    :type xpath: basestring
    :param scope: Scope of the citation (As described by CTS norm)
    :type xpath: basestring
    :param refsDecl: refsDecl version
    :type refsDecl: basestring
    :param child: A citation
    :type child: XmlCtsCitation
    :ivar name: Name of the citation (e.g. "book")
    :type name: basestring
    :ivar xpath: Xpath of the citation (As described by CTS norm)
    :type xpath: basestring
    :ivar scope: Scope of the citation (As described by CTS norm)
    :type xpath: basestring
    :ivar refsDecl: refsDecl version
    :type refsDecl: basestring
    :ivar child: A citation
    :type child: Citation

    """

    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.XML.TEI]
    DEFAULT_EXPORT = Mimetypes.XML.CTS

    escape = re.compile('(")')

    def __init__(self, name=None, xpath=None, scope=None, refsDecl=None, child=None):
        """ Initialize a XmlCtsCitation object
        """
        super(Citation, self).__init__(name=name, children=[child])

        self.__refsDecl = None

        self.name = name
        if scope and xpath:
            self._fromScopeXpathToRefsDecl(scope, xpath)
        else:
            self.refsDecl = refsDecl

    @property
    def xpath(self):
        """ CtsTextInventoryMetadata xpath property of a citation (ie. identifier of the last element of the citation)

        :type: basestring
        :Example: //tei:l[@n="?"]
        """
        return self._parseXpathScope()[1]

    @xpath.setter
    def xpath(self, new_xpath):
        if new_xpath is not None and self.refsDecl:
            current_scope, current_xpath = self._parseXpathScope()
            self._fromScopeXpathToRefsDecl(current_scope, new_xpath)

    @property
    def scope(self):
        """ CtsTextInventoryMetadata scope property of a citation (ie. identifier of all element but the last of the citation)

        :type: basestring
        :Example: /tei:TEI/tei:text/tei:body/tei:div
        """
        return self._parseXpathScope()[0]

    @scope.setter
    def scope(self, new_scope):
        if new_scope is not None and self.refsDecl:
            current_scope, current_xpath = self._parseXpathScope()
            self._fromScopeXpathToRefsDecl(new_scope, current_xpath)

    @property
    def refsDecl(self):
        """ ResfDecl expression of the citation scheme

        :rtype: str
        :Example: /tei:TEI/tei:text/tei:body/tei:div//tei:l[@n='$1']
        """
        return self.__refsDecl

    @refsDecl.setter
    def refsDecl(self, val):
        if val is not None:
            self.__refsDecl = val

    @property
    def child(self):
        """ Child of a citation

        :type: XmlCtsCitation or None
        :Example: XmlCtsCitation.name==poem would have a child XmlCtsCitation.name==line
        """
        if len(self.children):
            return self.children[0]

    @child.setter
    def child(self, val):
        if val:
            self.children = [val]
            if self.is_root():
                val.root = self
            else:
                val.root = self.root
        else:
            self.children = []

    @property
    def attribute(self):
        """ Attribute that serves as a reference getter
        """
        refs = re.findall(
            "\@([a-zA-Z:]+)=\\\?[\'\"]\$"+str(self.refsDecl.count("$"))+"\\\?[\'\"]",
            self.refsDecl
        )
        return refs[-1]

    def _parseXpathScope(self):
        """ Update xpath and scope property when refsDecl is updated

        :returns: Scope, Xpath
        """
        rd = self.refsDecl
        matches = REFSDECL_SPLITTER.findall(rd)
        return REFSDECL_REPLACER.sub("?", "".join(matches[0:-1])), REFSDECL_REPLACER.sub("?", matches[-1])

    def _fromScopeXpathToRefsDecl(self, scope, xpath):
        """ Update the refsDecl value if xpath and scope property are to be updated

        """
        if scope is not None and xpath is not None:
            _xpath = scope + xpath
            i = _xpath.find("?")
            ii = 1
            while i >= 0:
                _xpath = _xpath[:i] + "$" + str(ii) + _xpath[i+1:]
                i = _xpath.find("?")
                ii += 1
            self.refsDecl = _xpath

    def __getitem__(self, item):
        if not isinstance(item, int) or item > len(self)-1:
            raise KeyError("XmlCtsCitation index is too big")
        return [x for x in self][item]

    def __len__(self):
        """ Length method

        :rtype: int
        :returns: Number of nested citations
        """
        return len([x for x in self])

    def match(self, passageId):
        """ Given a passageId matches a citation level

        :param passageId: A passage to match
        :return:
        """
        if not isinstance(passageId, CtsReference):
            passageId = CtsReference(passageId)

        if self.is_root():
            return self[passageId.depth-1]
        return self.root.match(passageId)

    def fill(self, passage=None, xpath=None):
        """ Fill the xpath with given informations

        :param passage: CapitainsCtsPassage reference
        :type passage: CtsReference or list or None. Can be list of None and not None
        :param xpath: If set to True, will return the replaced self.xpath value and not the whole self.refsDecl
        :type xpath: Boolean
        :rtype: basestring
        :returns: Xpath to find the passage

        .. code-block:: python

            citation = XmlCtsCitation(name="line", scope="/TEI/text/body/div/div[@n=\"?\"]",xpath="//l[@n=\"?\"]")
            print(citation.fill(["1", None]))
            # /TEI/text/body/div/div[@n='1']//l[@n]
            print(citation.fill(None))
            # /TEI/text/body/div/div[@n]//l[@n]
            print(citation.fill(CtsReference("1.1"))
            # /TEI/text/body/div/div[@n='1']//l[@n='1']
            print(citation.fill("1", xpath=True)
            # //l[@n='1']


        """
        if xpath is True:  # Then passage is a string or None
            xpath = self.xpath

            replacement = r"\1"
            if isinstance(passage, str):
                replacement = r"\1\2'" + passage + "'"

            return REFERENCE_REPLACER.sub(replacement, xpath)
        else:
            if isinstance(passage, CtsReference):
                passage = passage.start.list
            elif passage is None:
                return REFERENCE_REPLACER.sub(
                    r"\1",
                    self.refsDecl
                )
            passage = iter(passage)
            return REFERENCE_REPLACER.sub(
                lambda m: _ref_replacer(m, passage),
                self.refsDecl
            )

    def is_set(self) -> bool:
        """ Check if the citation has been set

        :return: True if set up, False if not
        :rtype: bool
        """
        return self.refsDecl is not None

    def __export__(self, output=None, **kwargs):
        if output == Mimetypes.XML.CTS:
            if self.xpath is None and self.scope is None and self.refsDecl is None:
                return ""

            child = ""
            if isinstance(self.child, Citation):
                child = self.child.export(output=output)

            label = ""
            if self.name is not None:
                label = self.name

            return make_xml_node(
                get_graph(), RDF_NAMESPACES.CTS.citation, attributes={
                    "xpath": re.sub(Citation.escape, "'", self.xpath),
                    "scope": re.sub(Citation.escape, "'", self.scope),
                    "label": label
                }, innerXML=child, complete=True
            )
        elif output == Mimetypes.XML.TEI:
            if self.refsDecl is None:
                return ""

            label = ""
            if self.name is not None:
                label = self.name

            return \
                "<tei:cRefPattern n=\"{label}\" matchPattern=\"{regexp}\" replacementPattern=\"#xpath({refsDecl})\">" \
                "<tei:p>This pointer pattern extracts {label}</tei:p></tei:cRefPattern>".format(
                    refsDecl=self.refsDecl,
                    label=label,
                    regexp="\.".join(["(\w+)"]*self.refsDecl.count("$"))
                )

    def export(self, output=None, **kwargs):
        if self.refsDecl:
            return super(Citation, self).export(output=output, **kwargs)
        return ""

    @staticmethod
    def ingest(resource, xpath=".//tei:cRefPattern"):
        """ Ingest a resource and store data in its instance

        :param resource: XML node cRefPattern or list of them in ASC hierarchy order (deepest to highest, eg. lines to poem to book)
        :type resource: [lxml.etree._Element]
        :param xpath: XPath to use to retrieve citation
        :type xpath: str

        :returns: A citation object
        :rtype: Citation
        """
        if len(resource) == 0 and isinstance(resource, list):
            return None
        elif isinstance(resource, list):
            resource = resource[0]
        elif not isinstance(resource, _Element):
            return None

        resource = resource.xpath(xpath, namespaces=XPATH_NAMESPACES)
        citations = []

        for x in range(0, len(resource)):
            citations.append(
                Citation(
                    name=resource[x].get("n"),
                    refsDecl=resource[x].get("replacementPattern")[7:-1],
                    child=_child_or_none(citations)
                )
            )
        if len(citations) > 1:
            for citation in citations[:-1]:
                citation.root = citations[-1]
        return citations[-1]


def _ref_replacer(match, passage):
    """ Helper to replace xpath/scope/refsDecl on iteration with passage value

    :param match: A RegExp match
    :type match: re.SRE_MATCH
    :param passage: A list with subreference informations
    :type passage: iter

    :rtype: basestring
    :return: Replaced string
    """
    groups = match.groups()
    ref = next(passage)
    if ref is None:
        return groups[0]
    else:
        return "{1}='{0}'".format(ref, groups[0])