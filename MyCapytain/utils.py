from __future__ import unicode_literals
from collections import defaultdict
from future import basestring
import re

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


class Reference(object):

    """ A reference object giving informations """

    def __init__(self, reference):
        self.reference = reference
        self.parsed = self.__parse(reference)

    def __str__(self):
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
        return (None, [], None)

    def __regexp(self, subreference):
        r = re.compile("(\w*)\[([0-9]*)\]", re.UNICODE)
        return r.findall(subreference)[0]

    def __parse(self, reference):
        """ Parse references informations
        """
        ref = reference.split("-")
        element = (self.__model(), self.__model())
        for i in xrange(0,len(ref)):
            r = ref[i]
            subreference = r.split("@")
            if len(ref) == 2:
                element[i][2] = __regexp(r[1])
                r = r[0]
            element[i][1] = r.split(".")
        return element



class URN(object):

    """ A URN object giving all useful sections """

    def __init__(self, urn):
        self.urn = urn
        self.parsed = self.__parse(self.urn)
        self.reference = None

        if "reference" in self.parsed:
            self.reference = Reference(self.parsed["reference"])

    def __str__(self):
        return self.urn

    def __getitem__(self, key):
        """ Returns the urn (int) level or up to (str) level. 
            Urn is not counted as an element !

        :param key: Identifier of the wished resource
        :type key: int or basestring
        :rtype: basestring or Reference
        :returns: Part or complete URN
        """
        if isinstance(key, int) and key < len(__order):
            return self.parsed[__order[key]]
        elif level == "urn_namespace":
            return ":".join(["urn", urn["urn_namespace"]])
        elif level == "cts_namespace":
            return ":".join(["urn", urn["urn_namespace"], urn["cts_namespace"]])
        elif level == "textgroup":
            return ":".join(["urn", urn["urn_namespace"], urn["cts_namespace"], urn["textgroup"]])
        elif level == "work":
            return ":".join(["urn", urn["urn_namespace"], urn["cts_namespace"], ".".join([urn["textgroup"], urn["work"]])])
        elif level == "text":
            return ":".join(["urn", urn["urn_namespace"], urn["cts_namespace"], ".".join([urn["textgroup"], urn["work"], urn["text"]])])
        elif level == "passage":
            return ":".join(["urn", urn["urn_namespace"], urn["cts_namespace"], ".".join([urn["textgroup"], urn["work"], urn["text"], urn["passage"]])])
        elif level == "start":
            return ":".join(["urn", urn["urn_namespace"], urn["cts_namespace"], ".".join([urn["textgroup"], urn["work"], urn["text"], urn["reference"]["start"]])])
        elif level == "end":
            return ":".join(["urn", urn["urn_namespace"], urn["cts_namespace"], ".".join([urn["textgroup"], urn["work"], urn["text"], urn["reference"]["end"]])])
        else:
            return ""

    def __parse(self, urn):
        """ Parse a URN
        """
        parsed = defaultdict(basestring)
        parsed["full"] = urn.split("#")[0]
        urn = parsed["full"].split(":")
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

        return parsed
