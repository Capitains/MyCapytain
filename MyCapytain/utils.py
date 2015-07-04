from __future__ import unicode_literals
from collections import defaultdict, OrderedDict
from past.builtins import basestring
from builtins import range
import re


"""
    The ```utils``` modules
"""

class Reference(object):

    """ A reference object giving informations """

    def __init__(self, reference):
        self.reference = reference
        self.parsed = self.__parse(reference)

    def __eq__(self, other):
        """ Equality checker for Reference object
        :param other: An object to be checked against
        :rtype: boolean
        :returns: Equality between other and self
        """
        return (isinstance(other, self.__class__)
                and self.reference == str(other))

    def __str__(self):
        """ Return full initial reference
        :rtype: basestring
        :returns: String representation of Reference Object
        """
        return self.reference

    def __getitem__(self, key):
        """ Return part of or full passage reference 
        :param key: Identifier of the part to return
        :type key: basestring or int
        :rtype: basestring or List.<int> or None or Tuple.<string>
        :returns: Desired part of the passage reference
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
        return [None, [], None]

    def __regexp(self, subreference):
        """ Split components of subreference 
        :param subreference: A subreference
        :type subreference: basestring
        :rtype: List.<Tuple>
        :returns: List where first element is a tuple representing different components
        """
        r = re.compile("(\w*)\[{0,1}([0-9]*)\]{0,1}", re.UNICODE)
        return r.findall(subreference)[0]

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
                r = subreference[0]
            element[i][1] = r.split(".")
            element[i] = tuple(element[i])
        return tuple(element)


class URN(object):

    """ A URN object giving all useful sections """

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
        """ Warning : Does not take into account the passage ! """
        items = [key for key in self.parsed if key not in ["passage", "reference", "full"] ]
        return len(items)

    def __gt__(self, other):
        return len(self) > len(other)

    def __lt__(self, other):
        return len(self) < len(other)

    def __eq__(self, other):
        """ Equality checker for URN object
        :param other: An object to be checked against
        :rtype: boolean
        :returns: Equality between other and self
        """
        return (isinstance(other, self.__class__)
                and self.parsed["full"] == other["full"])

    def __str__(self):
        """ Return full initial urn
        :rtype: basestring
        :returns: String representation of URN Object
        """
        return self.urn

    def __getitem__(self, key):
        """ Returns the urn (int) level or up to (str) level. 
            Urn is not counted as an element !

        :param key: Identifier of the wished resource
        :type key: int or basestring
        :rtype: basestring or Reference
        :returns: Part or complete URN
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

class Metadatum(object):

    """ Metadatum object represent a single field of metadata """

    def __init__(self, name, children=None):
        """ Initiate a Metadatum object
        :param name: Name of the field
        :type name: basestring
        :param children: List.tuple
        :type children: dict
        """
        self.name = name
        self.children = OrderedDict()
        self.default = None

        if children is not None and isinstance(children, list):
            for tup in children:
                self[tup[0]] = tup[1]

    def __getitem__(self, key):
        """ Add an iterable access method
        :param key:
        :type key:
        :returns: An element of children whose index is key
        """
        if isinstance(key, int):
            items = list(self.children.keys())
            if key + 1 > len(items):
                raise KeyError()
            else:
                key = items[key]
        elif isinstance(key, tuple):
            return tuple([self[k] for k in key])

        if key not in self.children:
            if self.default is None:
                raise KeyError()
            else:
                return self.children[self.default]
        else:
            return self.children[key]

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            if not isinstance(value, (tuple, list)):
                value = [value]*len(key)
                print(value)
            if len(value) < len(key):
                raise ValueError("Less values than keys detected")
            for i in range(0, len(key)):
                self[key[i]] = value[i]
        elif not isinstance(key, basestring):
            raise TypeError("Only basestring or tuple instances are accepted as key")
        else:
            self.children[key] = value
            if self.default is None:
                self.default = key

    def setDefault(self, key):
        if key not in self.children:
            raise ValueError("Can not set a default to an unknown key")
        else:
            self.default = key
        return self.default