# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.proto.inventory
   :synopsis: Prototypes for repository/inventory

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from MyCapytain.common.reference import URN, Reference
from MyCapytain.common.metadata import Metadata
from past.builtins import basestring
from collections import defaultdict


class Resource(object):
    """ Resource represents any resource from the inventory """
    def __init__(self, resource=None):
        """ Initiate a TextInventory resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        """
        self.metadata = Metadata()
        self.resource = None
        if resource is not None:
            self.setResource(resource)

    def __getitem__(self, key):
        """ Direct key access function for Text objects """
        if key == 0:
            return self
        elif isinstance(key, int) and 1 <= key <= len(self.parents):
            r = self.parents[key - 1]
            if isinstance(r, (list, tuple)):
                return r[0]
            else:
                return r
        elif isinstance(key, basestring):
            return self.__urnitem__(key)
        else:
            None

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, self.__class__):
            return False
        elif self.resource is None:
            # Not totally true
            return (hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn)
        return (hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn) and self.resource == other.resource

    def __str__(self):
        raise NotImplementedError()

    def export(self, format=None):
        raise NotImplementedError()

    def __urnitem__(self, key):
        urn = URN(key)

        if len(urn) <= 2:
            raise ValueError("Not valid urn")
        elif hasattr(self, "urn") and self.urn == urn:
            return self
        else:
            if hasattr(self, "urn"):
                i = len(self.urn)
            else:
                i = 2

            if isinstance(self, TextInventory):
                children = self.textgroups
            elif isinstance(self, TextGroup):
                children = self.works
            elif isinstance(self, Work):
                children = self.texts

            order = ["", "", "textgroup", "work", "text"]

            while i <= len(urn) - 1:
                children = children[urn[order[i]]]
                if not hasattr(children, "urn") or str(children.urn) != urn[order[i]]:
                    raise ValueError("Unrecognized urn at level " + order[i])
                i += 1
            return children

    def setResource(self, resource):
        """ Set the object property resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :rtype: Any
        :returns: Input resource
        """
        self.resource = resource
        self.parse(resource)
        return self.resource

    def parse(self, resource):
        """ Parse the object resource 

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :rtype: List
        """
        raise NotImplementedError()

class Text(Resource):
    """ Represents a CTS Text
    """
    def __init__(self, resource=None, urn=None, parents=None, subtype="Edition"):
        """ Initiate a Work resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :param urn: Identifier of the Text
        :type urn: str
        """
        self.citation = None
        self.lang = None
        self.urn = None
        self.docname = None
        self.parents = ()
        self.subtype = subtype
        self.validate = None
        self.metadata = Metadata(keys=["label", "description", "namespaceMapping"])
        # self.citations = ()

        if urn is not None:
            self.urn = URN(urn)

        if parents is not None:
            self.parents = parents
            self.lang = self.parents[0].lang

        if resource is not None:
            self.setResource(resource)

        if self.subtype == "Edition":
            self.translations = lambda key=None: self.parents[0].getLang(key)
        elif self.subtype == "Translation":
            self.editions = lambda: [
                self.parents[0].texts[urn] 
                for urn in self.parents[0].texts 
                if self.parents[0].texts[urn].subtype == "Edition"
            ]


def Edition(resource=None, urn=None, parents=None):
    return Text(resource=resource, urn=urn, parents=parents, subtype="Edition")

def Translation(resource=None, urn=None, parents=None):
    return Text(resource=resource, urn=urn, parents=parents, subtype="Translation")
    
class Work(Resource):
    """ Represents a CTS Work
    """
    def __init__(self, resource=None, urn=None, parents=None):
        """ Initiate a Work resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :param urn: Identifier of the Work
        :type urn: str
        :param parents: List of parents for current object
        :type parents: Tuple.<TextInventory> 
        """
        self.lang = None
        self.urn = None
        self.texts = defaultdict(Text)
        self.parents = ()
        self.metadata = Metadata(keys=["title"])

        if urn is not None:
            self.urn = URN(urn)

        if parents is not None:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    def getLang(self, key=None):
        """ Find a translation with given language

        :param key: Language to find
        :type key: basestring
        :rtype: [Text]
        :returns: List of availables translations
        """
        if key is not None:
            return [self.texts[urn] for urn in self.texts if self.texts[urn].subtype == "Translation" and self.texts[urn].lang == key]
        else:
            return [self.texts[urn] for urn in self.texts if self.texts[urn].subtype == "Translation"]

class TextGroup(Resource):
    """ Represents a CTS Textgroup
    """
    def __init__(self, resource=None, urn=None, parents=None):
        """ Initiate a TextGroup resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :param urn: Identifier of the TextGroup
        :type urn: str
        :param parents: List of parents for current object
        :type parents: Tuple.<TextInventory> 
        """
        self.urn = None
        self.works = defaultdict(Work)
        self.parents = ()
        self.metadata = Metadata(keys=["groupname"])

        if urn is not None:
            self.urn = URN(urn)

        if parents:
            self.parents = [parents]

        if resource is not None:
            self.setResource(resource)


class TextInventory(Resource):
    """ Represents a CTS Inventory file
    """
    def __init__(self, resource=None, id=None):
        """ Initiate a TextInventory resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :param id: Identifier of the TextInventory
        :type id: str
        """
        self.textgroups = defaultdict(TextGroup)
        self.id = id
        self.parents = ()
        if resource is not None:
            self.setResource(resource)