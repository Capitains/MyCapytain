# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.reference
   :synopsis: URN related objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""
from __future__ import unicode_literals
from six import text_type
from copy import copy
import re
from lxml.etree import _Element
from MyCapytain.common.constants import XPATH_NAMESPACES, Mimetypes, get_graph, RDF_NAMESPACES
from MyCapytain.common.base import Exportable
from MyCapytain.common.utils import make_xml_node

REFSDECL_SPLITTER = re.compile(r"/+[*()|\sa-zA-Z0-9:\[\]@=\\{$'\".\s]+")
REFSDECL_REPLACER = re.compile(r"\$[0-9]+")
SUBREFERENCE = re.compile(r"(\w*)\[?([0-9]*)\]?", re.UNICODE)
REFERENCE_REPLACER = re.compile(r"(@[a-zA-Z0-9:]+)(=)([\\$'\"?0-9]{3,6})")

def __childOrNone__(liste):
    """ Used to parse resources in XmlCtsCitation

    :param liste: List of item
    :return: If there is > 1 element in the list, return the last one
    """
    if len(liste) > 0:
        return liste[-1]
    else:
        return None


class Reference(object):
    """ A reference object giving information

    :param reference: CapitainsCtsPassage Reference part of a Urn
    :type reference: basestring

    :Example:
        >>>    a = Reference(reference="1.1@Achiles[1]-1.2@Zeus[1]")
        >>>    b = Reference(reference="1.1")
        >>>    Reference("1.1-2.2.2").highest == ["1", "1"]

    Reference object supports the following magic methods : len(), str() and eq().

    :Example:
        >>>    len(a) == 2 && len(b) == 1
        >>>    str(a) == "1.1@Achiles[1]-1.2@Zeus[1]"
        >>>    b == Reference("1.1") && b != a

    .. note::
        While Reference(...).subreference and .list are not available for range, Reference(..).start.subreference \
        and Reference(..).end.subreference as well as .list are available
    """

    def __init__(self, reference=""):
        self.reference = reference
        if reference == "":
            self.parsed = (self.__model__(), self.__model__())
        else:
            self.parsed = self.__parse__(reference)

    @property
    def parent(self):
        """ Parent of the actual URN, for example, 1.1 for 1.1.1

        :rtype: Reference
        """
        if len(self.parsed[0][1]) == 1 and len(self.parsed[1][1]) <= 1:
            return None
        else:
            if len(self.parsed[0][1]) > 1 and len(self.parsed[1][1]) == 0:
                return Reference("{0}{1}".format(
                    ".".join(list(self.parsed[0][1])[0:-1]),
                    self.parsed[0][3] or ""
                ))
            elif len(self.parsed[0][1]) > 1 and len(self.parsed[1][1]) > 1:
                first = list(self.parsed[0][1])[0:-1]
                last = list(self.parsed[1][1])[0:-1]
                if first == last and self.parsed[1][3] is None \
                    and self.parsed[0][3] is None:
                    return Reference(".".join(first))
                else:
                    return Reference("{0}{1}-{2}{3}".format(
                        ".".join(first),
                        self.parsed[0][3] or "",
                        ".".join(list(self.parsed[1][1])[0:-1]),
                        self.parsed[1][3] or ""
                    ))

    @property
    def highest(self):
        """ Return highest reference level

        For references such as 1.1-1.2.8, with different level, it can be useful to access to the highest node in the
        hierarchy. In this case, the highest level would be 1.1. The function would return ["1", "1"]

        .. note:: By default, this property returns the start level

        :rtype: Reference
        """
        if not self.end:
            return self
        elif len(self.start) < len(self.end) and len(self.start):
            return self.start
        elif len(self.start) > len(self.end) and len(self.end):
            return self.end
        elif len(self.start):
            return self.start

    @property
    def start(self):
        """ Quick access property for start list

        :rtype: Reference
        """
        if self.parsed[0][0] and len(self.parsed[0][0]):
            return Reference(self.parsed[0][0])

    @property
    def end(self):
        """ Quick access property for reference end list

        :rtype: Reference
        """
        if self.parsed[1][0] and len(self.parsed[1][0]):
            return Reference(self.parsed[1][0])

    @property
    def list(self):
        """ Return a list version of the object if it is a single passage

        .. note:: Access to start list and end list should be done through obj.start.list and obj.end.list

        :rtype: [str]
        """
        if not self.end:
            return self.parsed[0][1]

    @property
    def subreference(self):
        """ Return the subreference of a single node reference

        .. note:: Access to start and end subreference should be done through obj.start.subreference \
        and obj.end.subreference

        :rtype: (str, int)
        """
        if not self.end:
            return Reference.convert_subreference(*self.parsed[0][2])

    def __len__(self):
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
            >>>    a = Reference(reference="1.1@Achiles[1]-1.2@Zeus[1]")
            >>>    b = Reference(reference="1.1")
            >>>    str(a) == "1.1@Achiles[1]-1.2@Zeus[1]"
            >>>    str(b) == "1.1"
        """
        return self.reference

    def __eq__(self, other):
        """ Equality checker for Reference object

        :param other: An object to be checked against
        :rtype: boolean
        :returns: Equality between other and self

        :Example:
            >>>    a = Reference(reference="1.1@Achiles[1]-1.2@Zeus[1]")
            >>>    b = Reference(reference="1.1")
            >>>    c = Reference(reference="1.1")
            >>>    (a == b) == False
            >>>    (c == b) == True
        """
        return (isinstance(other, type(self))
                and self.reference == str(other))

    def __ne__(self, other):
        """ Inequality checker for Reference object

        :param other: An object to be checked against
        :rtype: boolean
        :returns: Equality between other and self
        """
        return not self.__eq__(other)

    @staticmethod
    def __model__():
        """ 3-Tuple model for references

        First element is full text reference,
        Second is list of passage identifiers
        Third is subreference

        :returns: An empty list to model data
        :rtype: list
        """
        return [None, [], None, None]

    def __regexp__(self, subreference):
        """ Split components of subreference

        :param subreference: A subreference
        :type subreference: str
        :rtype: List.<Tuple>
        :returns: List where first element is a tuple representing different components
        """
        return SUBREFERENCE.findall(subreference)[0]

    def __parse__(self, reference):
        """ Parse references information

        :param reference: String representation of a reference
        :type reference: str
        :returns: Tuple representing each part of the reference
        :rtype: tuple(str)
        """

        ref = reference.split("-")
        element = [self.__model__(), self.__model__()]
        for i in range(0, len(ref)):
            r = ref[i]
            element[i][0] = r
            subreference = r.split("@")
            if len(subreference) == 2:
                element[i][2] = self.__regexp__(subreference[1])
                element[i][3] = "@" + subreference[1]
                r = subreference[0]
            element[i][1] = r.split(".")
            element[i] = tuple(element[i])
        return tuple(element)

    @staticmethod
    def convert_subreference(word, counter):
        """ Convert a word and a counter into a standard tuple representation

        :param word: Word Element of the subreference
        :param counter: Index of the Word
        :return: Tuple representing the element
        :rtype: (str, int)
        """
        if len(counter) and word:
            return str(word), int(counter)
        elif len(counter) == 0 and word:
            return str(word), 0
        else:
            return "", 0


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
        >>>     len(a) == 5 # Reference is not counted to not induce count equivalencies with the optional version
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

        :rtype: Reference
        :return: Reference part of the URN
        """
        return self.__parsed["reference"]

    @reference.setter
    def reference(self, value):
        self.__urn = None
        if isinstance(value, Reference):
            self.__parsed["reference"] = value
        else:
            self.__parsed["reference"] = Reference(value)

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
        """ Inequality checker for Reference object

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
                parsed["reference"] = Reference(urn[4])

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


class Citation(Exportable):
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
        self.__name = None
        self.__xpath = None
        self.__scope = None
        self.__refsDecl = None
        self.__child = None

        self.name = name
        self.scope = scope
        self.xpath = xpath
        self.refsDecl = refsDecl

        if child is not None:
            self.child = child

    @property
    def name(self):
        """ Type of the citation represented
        
        :type: text_type
        :example: Book, Chapter, Textpart, Section, Poem...
        """
        return self.__name

    @name.setter
    def name(self, val):
        self.__name = val

    @property
    def xpath(self):
        """ CtsTextInventoryMetadata xpath property of a citation (ie. identifier of the last element of the citation)
        
        :type: basestring
        :Example: //tei:l[@n="?"]
        """
        return self.__xpath

    @xpath.setter
    def xpath(self, val):
        if val is not None:
            self.__xpath = val
            self.__upRefsDecl()

    @property
    def scope(self):
        """ CtsTextInventoryMetadata scope property of a citation (ie. identifier of all element but the last of the citation)
        
        :type: basestring
        :Example: /tei:TEI/tei:text/tei:body/tei:div
        """
        return self.__scope
        
    @scope.setter
    def scope(self, val):
        if val is not None:
            self.__scope = val
            self.__upRefsDecl()

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
            self.__upXpathScope()

    @property
    def child(self):
        """ Child of a citation

        :type: XmlCtsCitation or None
        :Example: XmlCtsCitation.name==poem would have a child XmlCtsCitation.name==line
        """
        return self.__child
        
    @child.setter
    def child(self, val):
        if isinstance(val, self.__class__):
            self.__child = val

    @property
    def attribute(self):
        """ Attribute that serves as a reference getter
        """
        refs = re.findall(
            "\@([a-zA-Z:]+)=\\\?[\'\"]\$"+str(self.refsDecl.count("$"))+"\\\?[\'\"]",
            self.refsDecl
        )
        return refs[-1]

    def __upXpathScope(self):
        """ Update xpath and scope property when refsDecl is updated
        
        """
        rd = self.__refsDecl
        matches = REFSDECL_SPLITTER.findall(rd)
        self.__scope = REFSDECL_REPLACER.sub("?", "".join(matches[0:-1]))
        self.__xpath = REFSDECL_REPLACER.sub("?", matches[-1])

    def __upRefsDecl(self):
        """ Update xpath and scope property when refsDecl is updated
        
        """
        if self.__scope is not None and self.__xpath is not None:
            xpath = self.__scope + self.__xpath
            i = xpath.find("?")
            ii = 1
            while i >= 0:
                xpath = xpath[:i] + "$" + str(ii) + xpath[i+1:]
                i = xpath.find("?")
                ii += 1
            self.__refsDecl = xpath

    def __iter__(self):
        """ Iteration method
        
        Loop over the citation childs

        :Example:
            >>>    c = XmlCtsCitation(name="line")
            >>>    b = XmlCtsCitation(name="poem", child=c)
            >>>    a = XmlCtsCitation(name="book", child=b)
            >>>    [e for e in a] == [a, b, c]
            
        """
        e = self
        while e is not None:
            yield e
            if hasattr(e, "child") and e.child is not None:
                e = e.child
            else:
                break

    def __getitem__(self, item):
        if not isinstance(item, int) or item > len(self)-1:
            raise KeyError("XmlCtsCitation index is too big")
        return [x for x in self][item]

    def __len__(self):
        """ Length method

        :rtype: int
        :returns: Number of nested citations
        """
        return len([item for item in self])

    def fill(self, passage=None, xpath=None):
        """ Fill the xpath with given informations

        :param passage: CapitainsCtsPassage reference
        :type passage: Reference or list or None. Can be list of None and not None
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
            print(citation.fill(Reference("1.1"))
            # /TEI/text/body/div/div[@n='1']//l[@n='1']
            print(citation.fill("1", xpath=True)
            # //l[@n='1']


        """
        if xpath is True:  # Then passage is a string or None
            xpath = self.xpath

            replacement = r"\1"
            if isinstance(passage, text_type):
                replacement = r"\1\2'" + passage + "'"

            return REFERENCE_REPLACER.sub(replacement, xpath)
        else:
            if isinstance(passage, Reference):
                passage = passage.list or passage.start.list
            elif passage is None:
                return REFERENCE_REPLACER.sub(
                    r"\1",
                    self.refsDecl
                )
            passage = iter(passage)
            return REFERENCE_REPLACER.sub(
                lambda m: REF_REPLACER(m, passage),
                self.refsDecl
            )

    def __getstate__(self):
        """ Pickling method

        :return: dict
        """
        return copy(self.__dict__)

    def __setstate__(self, dic):
        self.__dict__ = dic
        return self

    def isEmpty(self):
        """ Check if the citation has not been set

        :return: True if nothing was setup
        :rtype: bool
        """
        return self.refsDecl is None and self.scope is None and self.xpath is None

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
        resources = []

        for x in range(0, len(resource)):
            resources.append(
                Citation(
                    name=resource[x].get("n"),
                    refsDecl=resource[x].get("replacementPattern")[7:-1],
                    child=__childOrNone__(resources)
                )
            )

        return resources[-1]


def REF_REPLACER(match, passage):
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


class NodeId(object):
    """ Collection of directional references for a Tree

    :param identifier: Current object identifier
    :type identifier: str
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    """
    def __init__(self, identifier=None, children=None, parent=None, siblings=(None, None), depth=None):
        self.__children__ = children or []
        self.__parent__ = parent
        self.__prev__, self.__nextId__ = siblings
        self.__identifier__ = identifier
        self.__depth__ = depth

    @property
    def depth(self):
        """ Depth of the node in the global hierarchy of the text tree

        :rtype: int
        """
        return self.__depth__

    @property
    def childIds(self):
        """ Children Node

        :rtype: [str]
        """
        return self.__children__

    @property
    def firstId(self):
        """ First child Node

        :rtype: str
        """
        if len(self.__children__) == 0:
            return None
        return self.__children__[0]

    @property
    def lastId(self):
        """ Last child Node

        :rtype: str
        """
        if len(self.__children__) == 0:
            return None
        return self.__children__[-1]

    @property
    def parentId(self):
        """ Parent Node

        :rtype: str
        """
        return self.__parent__

    @property
    def siblingsId(self):
        """ Siblings Node

        :rtype: (str, str)
        """
        return self.__prev__, self.__nextId__

    @property
    def prevId(self):
        """ Previous Node (Sibling)

        :rtype: str
        """
        return self.__prev__

    @property
    def nextId(self):
        """ Next Node (Sibling)

        :rtype: str
        """
        return self.__nextId__

    @property
    def id(self):
        """Current object identifier

        :rtype: str
        """
        return self.__identifier__
