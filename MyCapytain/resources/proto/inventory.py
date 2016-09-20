# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.proto.inventory
   :synopsis: Prototypes for repository/inventory

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from MyCapytain.common.reference import URN, Reference, Citation
from MyCapytain.common.metadata import Metadata
from MyCapytain.errors import InvalidURN
from past.builtins import basestring
from collections import defaultdict
from copy import copy, deepcopy
from lxml import etree
from builtins import object
from six import text_type as str


class Resource(object):
    """ Resource represents any resource from the inventory

    :param resource: Resource representing the TextInventory
    :type resource: Any
    """
    def __init__(self, resource=None):
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
            return None

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, self.__class__):
            return False
        elif self.resource is None:
            # Not totally true
            return hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn
        return hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn and self.resource == other.resource

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

            order = ["", "", URN.TEXTGROUP, URN.WORK, URN.VERSION]
            while i <= len(urn) - 1:
                children = children[urn.upTo(order[i])]
                if not hasattr(children, "urn") or str(children.urn) != urn.upTo(order[i]):
                    error = "Unrecognized urn at " + [
                        "URN namespace", "CTS Namespace", "URN Textgroup", "URN Work", "URN Version"
                    ][i]
                    raise ValueError(error)
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

    def __getstate__(self, children=True):
        """ Pickling method to be called upon dumping object

        :return:
        """

        dic = copy(self.__dict__)
        if "xml" in dic:
            dic["xml"] = etree.tostring(dic["xml"], encoding=str)
        if "resource" in dic:
            del dic["resource"]
        """ The resource is unecessary in later than parsing state
        if "resource" in dic:
            dic["resource"] = str(dic["resource"])
        """
        return dic

    def __setstate__(self, dic):
        """

        :param dic:
        :return:
        """
        self.__dict__ = dic
        if "xml" in dic:
            self.xml = etree.fromstring(dic["xml"])
        return self


class Text(Resource):
    """ Represents a CTS Text

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param urn: Identifier of the Text
    :type urn: str
    """
    def __init__(self, resource=None, urn=None, parents=None, subtype="Edition"):
        self.resource = None
        self.citation = None
        self.lang = None
        self.urn = None
        self.docname = None
        self.parents = list()
        self.subtype = subtype
        self.validate = None
        self.metadata = Metadata(keys=["label", "description", "namespaceMapping"])

        if urn is not None:
            self.urn = URN(urn)

        if parents is not None:
            self.parents = parents
            self.lang = self.parents[0].lang

        if resource is not None:
            self.setResource(resource)

    def translations(self, key=None):
        """ Get translations in given language

        :param key: Language ISO Code to filter on
        :return:
        """
        return self.parents[0].getLang(key)

    def editions(self):
        """ Get all editions of the texts

        :return: List of editions
        :rtype: [Text]
        """
        return [
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

    CTS Work can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param urn: Identifier of the Work
    :type urn: str
    :param parents: List of parents for current object
    :type parents: Tuple.<TextInventory>
    """
    def __init__(self, resource=None, urn=None, parents=None):
        self.resource = None
        self.lang = None
        self.urn = None
        self.texts = defaultdict(Text)
        self.parents = list()
        self.metadata = Metadata(keys=["title"])

        if urn is not None:
            self.urn = URN(urn)

        if parents is not None:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    def update(self, other):
        """ Merge two Work Objects.

        - Original (left Object) keeps his parent.
        - Added document overwrite text if it already exists

        :param other: Work object
        :type other: Work
        :return: Work Object
        :rtype Work:
        """
        if not isinstance(other, Work):
            raise TypeError("Cannot add %s to Work" % type(other))
        elif self.urn != other.urn:
            raise InvalidURN("Cannot add Work %s to Work %s " % (self.urn, other.urn))

        self.metadata += other.metadata
        parents = [self] + self.parents
        for urn, text in other.texts.items():
            if urn in self.texts:
                self.texts[urn] = deepcopy(text)
            else:
                self.texts[urn] = deepcopy(text)
            self.texts[urn].parents = parents
            self.texts[urn].resource = None

        return self

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

    def __len__(self):
        """ Get the number of text in the Work

        :return: Number of texts available in the inventory
        """
        return len(self.texts)


class TextGroup(Resource):
    """ Represents a CTS Textgroup

    CTS TextGroup can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param urn: Identifier of the TextGroup
    :type urn: str
    :param parents: List of parents for current object
    :type parents: Tuple.<TextInventory>
    """
    def __init__(self, resource=None, urn=None, parents=None):
        self.resource = None
        self.urn = None
        self.works = defaultdict(Work)
        self.parents = list()
        self.metadata = Metadata(keys=["groupname"])

        if urn is not None:
            self.urn = URN(urn)

        if parents:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    def update(self, other):
        """ Merge two Textgroup Objects.

        - Original (left Object) keeps his parent.
        - Added document merges with work if it already exists

        :param other: Textgroup object
        :type other: TextGroup
        :return: Textgroup Object
        :rtype: TextGroup
        """
        if not isinstance(other, TextGroup):
            raise TypeError("Cannot add %s to TextGroup" % type(other))
        elif str(self.urn) != str(other.urn):
            raise InvalidURN("Cannot add TextGroup %s to TextGroup %s " % (self.urn, other.urn))

        self.metadata += other.metadata
        parents = [self] + self.parents
        for urn, work in other.works.items():
            if urn in self.works:
                self.works[urn].update(deepcopy(work))
            else:
                self.works[urn] = deepcopy(work)
            self.works[urn].parents = parents
            self.works[urn].resource = None

        return self

    def __len__(self):
        """ Get the number of text in the Textgroup

        :return: Number of texts available in the inventory
        """
        return len([
            text
            for work in self.works.values()
            for text in work.texts.values()
        ])


class TextInventory(Resource):
    """ Initiate a TextInventory resource

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param id: Identifier of the TextInventory
    :type id: str
    """
    def __init__(self, resource=None, id=None):
        self.resource = None
        self.textgroups = defaultdict(TextGroup)
        self.id = id
        self.parents = list()
        if resource is not None:
            self.setResource(resource)

    def __len__(self):
        """ Get the number of text in the Inventory

        :return: Number of texts available in the inventory
        """
        return len([
            text
            for tg in self.textgroups.values()
            for work in tg.works.values()
            for text in work.texts.values()
        ])
