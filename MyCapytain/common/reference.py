# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.reference
   :synopsis: URN related objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

>>> from MyCapytain.common.reference import (URN, Reference, Citation)

"""
from __future__ import unicode_literals

from collections import defaultdict
from past.builtins import basestring
from builtins import range, object
import re


REFSDECL_SPLITTER = re.compile("/+[a-zA-Z0-9:\[\]@=\\\{\$'\"\.]+")
REFSDECL_REPLACER = re.compile("\$[0-9]+")
SUBREFERENCE = re.compile("(\w*)\[{0,1}([0-9]*)\]{0,1}", re.UNICODE)
REFERENCE_REPLACER = re.compile("(@[a-zA-Z0-9:]+){1}(=){1}([\\\$'\"?0-9]{3,6})")


class Reference(object):

    """ A reference object giving informations

    :param reference: Passage Reference part of a Urn
    :type reference: basestring

    :Example:
        >>>    a = Reference(reference="1.1@Achiles[1]-1.2@Zeus[1]")
        >>>    b = Reference(reference="1.1")

    .. automethod:: __str__
    .. automethod:: __eq__
    .. automethod:: __getitem__
    .. automethod:: __setitem__
    """

    def __init__(self, reference):
        self.reference = reference
        self.parsed = self.__parse(reference)

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
        return (isinstance(other, self.__class__)
                and self.reference == str(other))

    @property
    def parent(self):
        """

        :return:
        """
        if len(self.parsed[0][1]) == 1 and len(self.parsed[1][1]) <= 1:
            return None
        else:
            if len(self.parsed[0][1]) > 1 and len(self.parsed[1][1]) == 0:
                return "{0}{1}".format(
                    ".".join(list(self.parsed[0][1])[0:-1]),
                    self.parsed[0][3] or ""
                )
            elif len(self.parsed[0][1]) > 1 and len(self.parsed[1][1]) > 1:
                first = list(self.parsed[0][1])[0:-1]
                last = list(self.parsed[1][1])[0:-1]
                if first == last and self.parsed[1][3] is None \
                    and self.parsed[0][3] is None:
                    return ".".join(first)
                else:
                    return "{0}{1}-{2}{3}".format(
                        ".".join(first),
                        self.parsed[0][3] or "",
                        ".".join(list(self.parsed[1][1])[0:-1]),
                        self.parsed[1][3] or ""
                    )

    def __str__(self):
        """ Return full reference in string format
        
        :rtype: basestring
        :returns: String representation of Reference Object

        :Example:
            >>>    a = Reference(reference="1.1@Achiles[1]-1.2@Zeus[1]")
            >>>    b = Reference(reference="1.1")
            >>>    str(a) == "1.1@Achiles[1]-1.2@Zeus[1]"
            >>>    str(b) == "1.1"
        """
        return self.reference

    def __getitem__(self, key):
        """ Return part of or full passage reference 
        
        Available keys :
            - *1 | start* : First part of the reference
            - *2 | start_list* : Reference start parsed into a list
            - *3 | start_sub* : Subreference start parsed into a tuple
            - *4 | end* : Last part of the reference
            - *5 | end_list* : Reference start parsed into a list
            - *6 | end_sub* : Subreference end parsed into a tuple
            - *default* : full string reference 

        :param key: Identifier of the part to return
        :type key: basestring or int
        :rtype: basestring or List.<int> or None or Tuple.<string>
        :returns: Desired part of the passage reference

        :Example:
            >>>    a = Reference(reference="1.1@Achiles[1]-1.2@Zeus[1]")
            >>>    print(a[1]) # "1.1@Achiles[1]"
            >>>    print(a["start_list"]) # ("1", "1")
            >>>    print(a[6]) # ("Zeus", "1")
            >>>    print(a[7]) # "1.1@Achiles[1]-1.2@Zeus[1]"
        """
        if key == 1 or key == "start":
            return self.parsed[0][0]
        elif key == 4 or key == "end":
            return self.parsed[1][0]
        elif key == 2 or key == "start_list":
            return self.parsed[0][1]
        elif key == 5 or key == "end_list":
            return self.parsed[1][1]
        elif key == 3 or key == "start_sub":
            return self.parsed[0][2]
        elif key == 6 or key == "end_sub":
            return self.parsed[1][2]
        else:
            return self.reference

    def __model(self):
        """ 3-Tuple model for references
        
            First element is full text reference,
            Second is list of passage identifiers
            Third is subreference

        :rtype: Tuple
        :returns: An empty tuple to model data
        """
        return [None, [], None, None]

    def __regexp(self, subreference):
        """ Split components of subreference 
        
        :param subreference: A subreference
        :type subreference: basestring
        :rtype: List.<Tuple>
        :returns: List where first element is a tuple representing different components
        """
        return SUBREFERENCE.findall(subreference)[0]

    def __parse(self, reference):
        """ Parse references informations
        
        """

        ref = reference.split("-")
        element = [self.__model(), self.__model()]
        for i in range(0, len(ref)):
            r = ref[i]
            element[i][0] = r
            subreference = r.split("@")
            if len(subreference) == 2:
                element[i][2] = self.__regexp(subreference[1])
                element[i][3] = "@" + subreference[1]
                r = subreference[0]
            element[i][1] = r.split(".")
            element[i] = tuple(element[i])
        return tuple(element)


class URN(object):

    """ A URN object giving all useful sections 

    :param urn: A CTS URN
    :type urn: basestring

    :Example:
        >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")

    .. automethod:: __len__
    .. automethod:: __gt__
    .. automethod:: __lt__
    .. automethod:: __eq__
    .. automethod:: __str__
    .. automethod:: __getitem__
    """
        

    __order = [
        "full",
        "urn_namespace",
        "cts_namespace",
        "textgroup",
        "work",
        "text",
        "passage",
        "reference"  # Reference is a more complex object
    ]

    def __init__(self, urn):
        self.urn = urn
        self.parsed = self.__parse(self.urn)

    def __len__(self):
        """ Returns the len of the URN

        :rtype: int
        :returns: Length of the URN

        .. warning:: Does not take into account the passage !

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1") 
            >>>    print(len(a)) # 


        """
        
        items = [key for key in self.parsed if key not in ["passage", "reference", "full"] ]
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
            >>>    (a > b) == True # 
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
            >>>    (b < a) == True # 
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
            >>>    (b == a) == False # 
        """
        return (isinstance(other, self.__class__)
                and self.parsed["full"] == other["full"])

    def __str__(self):
        """ Return full initial urn
        
        :rtype: basestring
        :returns: String representation of URN Object

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1") 
            >>>    str(a) == "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        """
        return self.urn

    def __getitem__(self, key):
        """ Returns the urn (int) level or up to (str) level. 
        

        Available keys :
            - *0* :  URN
            - *full* : URN
            - *1* :  Namespace of the urn (cts)
            - *urn_namespace* : URN until the Namespace of the urn 
            - *2* :  CTS Namespace of the URN (e.g. latinLit)
            - *cts_namespace* : URN until the CTS Namespace
            - *3* :  Textgroup of the URN
            - *textgroup* : URN until the Textgroup
            - *4* :  Work of the URN
            - *work* : URN until the Work
            - *5* :  Text of the URN
            - *text* : URN until the Text
            - *6* or *passage*:  Passage of URN

        :param key: Identifier of the wished resource
        :type key: int or basestring
        :rtype: basestring or Reference
        :returns: Part or complete URN
        :warning: *urn:* is not counted as an element !

        :Example:
            >>>    a = URN(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1") 
            >>>    a["textgroup"] == "urn:cts:latinLit:phi1294"
            >>>    a[3] == "phi1294
        """
        if isinstance(key, int) and key < len(URN.__order):
            return self.parsed[URN.__order[key]]
        elif key == "urn_namespace":
            return ":".join(["urn", self.parsed["urn_namespace"]])
        elif key == "cts_namespace":
            return ":".join([
                "urn",
                self.parsed["urn_namespace"],
                self.parsed["cts_namespace"]])
        elif key == "textgroup" and "textgroup" in self.parsed:
            return ":".join([
                "urn",
                self.parsed["urn_namespace"],
                self.parsed["cts_namespace"],
                self.parsed["textgroup"]
            ])
        elif key == "work" and "work" in self.parsed:
            return ":".join([
                "urn",
                self.parsed["urn_namespace"],
                self.parsed["cts_namespace"],
                ".".join(
                    [
                        self.parsed["textgroup"],
                        self.parsed["work"]
                    ])
            ])
        elif key == "text" and "text" in self.parsed:
            return ":".join([
                "urn",
                self.parsed["urn_namespace"],
                self.parsed["cts_namespace"],
                ".".join(
                    [
                        self.parsed["textgroup"],
                        self.parsed["work"],
                        self.parsed["text"]
                    ])
            ])
        elif key == "passage" and "passage" in self.parsed:
            if "text" in self.parsed:
                return ":".join([
                    "urn",
                    self.parsed["urn_namespace"],
                    self.parsed["cts_namespace"],
                    ".".join(
                        [
                            self.parsed["textgroup"],
                            self.parsed["work"],
                            self.parsed["text"]
                        ]),
                    self.parsed["passage"]
                ])
            else:
                return ":".join([
                    "urn",
                    self.parsed["urn_namespace"],
                    self.parsed["cts_namespace"],
                    ".".join(
                        [
                            self.parsed["textgroup"],
                            self.parsed["work"]
                        ]),
                    self.parsed["passage"]
                ])
        elif key == "start" and "passage" in self.parsed:
            if "text" in self.parsed:
                return ":".join([
                    "urn",
                    self.parsed["urn_namespace"],
                    self.parsed["cts_namespace"],
                    ".".join(
                        [
                            self.parsed["textgroup"],
                            self.parsed["work"],
                            self.parsed["text"]
                        ]),
                    self.parsed["reference"]["start"]
                ])
            else:
                return ":".join([
                    "urn",
                    self.parsed["urn_namespace"],
                    self.parsed["cts_namespace"],
                    ".".join(
                        [
                            self.parsed["textgroup"],
                            self.parsed["work"]
                        ]),
                    self.parsed["reference"]["start"]
                ])
        elif key == "end" and "passage" in self.parsed and self.parsed["reference"]["end"] is not None:
            if "text" in self.parsed:
                return ":".join([
                    "urn",
                    self.parsed["urn_namespace"],
                    self.parsed["cts_namespace"],
                    ".".join([
                        self.parsed["textgroup"],
                        self.parsed["work"],
                        self.parsed["text"]
                    ]),
                    self.parsed["reference"]["end"]
                ])
            else:
                return ":".join([
                    "urn",
                    self.parsed["urn_namespace"],
                    self.parsed["cts_namespace"],
                    ".".join([
                        self.parsed["textgroup"],
                        self.parsed["work"]
                    ]),
                    self.parsed["reference"]["end"]
                ])
        elif key == "full":
            return self.parsed["full"]
        elif key == "reference" and "reference" in self.parsed:
            return self.parsed["reference"]
        else:
            return None

    def __parse(self, urn):
        """ Parse a URN
        

        :param urn: A URN:CTS
        :type urn: basestring
        :rtype: defaultdict.basestring
        :returns: Dictionary representation
        """
        parsed = defaultdict(str)
        parsed["full"] = urn.split("#")[0]
        urn = parsed["full"].split(":")
        if isinstance(urn, list) and len(urn) > 2:
            parsed["urn_namespace"] = urn[1]
            parsed["cts_namespace"] = urn[2]

            if len(urn) == 5:
                parsed["passage"] = urn[4]
                parsed["reference"] = Reference(urn[4])

            if len(urn) >= 4:
                urn = urn[3].split(".")
                if len(urn) >= 1:
                    parsed["textgroup"] = urn[0]
                if len(urn) >= 2:
                    parsed["work"] = urn[1]
                if len(urn) >= 3:
                    parsed["text"] = urn[2]
        else:
            raise ValueError("URN is empty")
        return parsed


class Citation(object):
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
    :type child: Citation

    .. automethod:: __iter__
    .. automethod:: __len__
    """

    def __init__(self, name=None, xpath=None, scope=None, refsDecl=None, child=None):
        """ Initialize a Citation object
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
        
        :type: basestring
        :Example: Book, Chapter, Textpart, Section, Poem...
        """
        return self.__name

    @name.setter
    def name(self, val):
        self.__name = val

    @property
    def xpath(self):
        """ TextInventory xpath property of a citation (ie. identifier of the last element of the citation)
        
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
        """ TextInventory scope property of a citation (ie. identifier of all element but the last of the citation)
        
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

        :type: basestring
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

        :type: Citation or None
        :Example: Citation.name==poem would have a child Citation.name==line
        """
        return self.__child
        
    @child.setter
    def child(self, val):
        if isinstance(val, self.__class__):
            self.__child = val

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
            >>>    c = Citation(name="line")
            >>>    b = Citation(name="poem", child=c)
            >>>    a = Citation(name="book", child=b)
            >>>    [e for e in a] == [a, b, c]
            
        """
        e = self
        while e is not None:
            yield e
            if hasattr(e, "child") and e.child is not None:
                e = e.child
            else:
                break

    def __len__(self):
       """ Length method

       :rtype: int
       :returns: Number of nested citations
       """
       return len([item for item in self])

    def fill(self, passage=None, xpath=None):
        """ Fill the xpath with given informations

        :param passage: Passage reference
        :type passage: Reference or lsit
        :param xpath: If set to True, will return the replaced self.xpath value and not the whole self.refsDecl
        :type xpath: Boolean
        :rtype: basestring
        :returns: Xpath to find the passage
        """
        if xpath is True: # Then passage is a string or None
            xpath = self.xpath

            if passage is None:
                replacement = r"\1"
            elif isinstance(passage, basestring):
                replacement = r"\1\2'" + passage + "'"

            return REFERENCE_REPLACER.sub(replacement, xpath)
        else:        
            if isinstance(passage, Reference):
                passage = passage[2]
            passage = iter(passage)    
            return REFERENCE_REPLACER.sub(
                lambda m: REF_REPLACER(m, passage),
                self.refsDecl
            )

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