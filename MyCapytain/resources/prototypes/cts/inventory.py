# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.prototypes.cts.inventory
   :synopsis: Prototypes for repository/inventory Collection CTS objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""
from __future__ import unicode_literals
from six import text_type

from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.common.reference import URN
from MyCapytain.common.metadata import Metadata, Metadatum
from MyCapytain.common.constants import NAMESPACES, RDF_PREFIX
from MyCapytain.errors import InvalidURN
from collections import defaultdict
from copy import copy, deepcopy
from lxml import etree


class CTSCollection(Collection):
    """ Resource represents any resource from the inventory

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :cvar CTSMODEL: String Representation of the type of collection
    """
    CTSMODEL = "CTSCollection"

    def __init__(self, resource=None):
        super(CTSCollection, self).__init__()

        if hasattr(type(self), "CTSMODEL"):
            self.properties[RDF_PREFIX["ti"]+"model"] = RDF_PREFIX["ti"] + type(self).CTSMODEL

        self.resource = None
        if resource is not None:
            self.setResource(resource)

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


class Text(CTSCollection):
    """ Represents a CTS Text

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param urn: Identifier of the Text
    :type urn: str
    :param parents: Item parents of the current collection
    :type parents: [CTSCollection]
    :param subtype: Subtype of the object (Edition, Translation)
    :type subtype: str

    :ivar urn: URN Identifier
    :type urn: URN
    :ivar parents: List of ancestors, from parent to furthest
    """

    DC_TITLE_KEY = "label"

    @property
    def TEXT_URI(self):
        """ Ontology URI of the text

        :return: CTS Ontology Edition or Translation object
        :rtype: str
        """
        return RDF_PREFIX["ti"] + self.subtype

    def __init__(self, resource=None, urn=None, parents=None, subtype="Edition"):
        super(Text, self).__init__()
        self.resource = None
        self.citation = None
        self.lang = None
        self.urn = None
        self.docname = None
        self.parents = list()
        self.subtype = subtype
        self.validate = None
        self.metadata = Metadata()
        self.metadata["label"] = Metadatum(name="label", namespace=NAMESPACES.CTS)
        self.metadata["description"] = Metadatum(name="description", namespace=NAMESPACES.CTS)
        self.metadata["namespaceMapping"] = Metadatum(name="namespaceMapping", namespace=NAMESPACES.CTS)

        if urn is not None:
            self.urn = URN(urn)

        if parents is not None:
            self.parents = parents
            self.lang = self.parents[0].lang

        if resource is not None:
            self.setResource(resource)

    @property
    def readable(self):
        return True

    @property
    def members(self):
        return []

    @property
    def descendants(self):
        return []

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

    @property
    def id(self):
        return str(self.urn)

    @id.setter
    def id(self, value):
        self.urn = URN(value)


def Edition(resource=None, urn=None, parents=None):
    """ Represents a CTS Edition

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param urn: Identifier of the Text
    :type urn: str
    :param parents: Item parents of the current collection
    :type parents: [CTSCollection]
    """
    return Text(resource=resource, urn=urn, parents=parents, subtype="Edition")


def Translation(resource=None, urn=None, parents=None):
    """ Represents a CTS Translation

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param urn: Identifier of the Text
    :type urn: str
    :param parents: Item parents of the current collection
    :type parents: [CTSCollection]
    """
    return Text(resource=resource, urn=urn, parents=parents, subtype="Translation")


class Work(CTSCollection):
    """ Represents a CTS Work

    CTS Work can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param urn: Identifier of the Work
    :type urn: str
    :param parents: List of parents for current object
    :type parents: Tuple.<TextInventory>

    :ivar urn: URN Identifier
    :type urn: URN
    :ivar parents: List of ancestors, from parent to furthest
    """

    DC_TITLE_KEY = "title"
    TYPE_URI = RDF_PREFIX["ti"] + "Work"

    def __init__(self, resource=None, urn=None, parents=None):
        super(Work, self).__init__()
        self.resource = None
        self.lang = None
        self.urn = None
        self.texts = defaultdict(Text)
        self.parents = list()
        self.metadata = Metadata()
        self.metadata["title"] = Metadatum(name="title", namespace=NAMESPACES.CTS)

        if urn is not None:
            self.urn = URN(urn)
            self.id = str(self.urn)

        if parents is not None:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    @property
    def readable(self):
        return True

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
        :type key: text_type
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

    @property
    def members(self):
        return list(self.texts.values())

    @property
    def id(self):
        return str(self.urn)

    @id.setter
    def id(self, value):
        self.urn = URN(value)


class TextGroup(CTSCollection):
    """ Represents a CTS Textgroup

    CTS TextGroup can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param urn: Identifier of the TextGroup
    :type urn: str
    :param parents: List of parents for current object
    :type parents: Tuple.<TextInventory>

    :ivar urn: URN Identifier
    :type urn: URN
    :ivar parents: List of ancestors, from parent to furthest
    """
    DC_TITLE_KEY = "groupname"
    TYPE_URI = RDF_PREFIX["ti"] + "TextGroup"

    @property
    def members(self):
        return list(self.works.values())

    def __init__(self, resource=None, urn=None, parents=None):
        super(TextGroup, self).__init__()
        self.resource = None
        self.urn = None
        self.works = defaultdict(Work)
        self.parents = list()
        self.metadata = Metadata()
        self.metadata["groupname"] = Metadatum(name="groupname", namespace=NAMESPACES.CTS)

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

    @property
    def id(self):
        return str(self.urn)

    @id.setter
    def id(self, value):
        self.urn = URN(value)


class TextInventory(CTSCollection):
    """ Initiate a TextInventory resource

    :param resource: Resource representing the TextInventory
    :type resource: Any
    :param id: Identifier of the TextInventory
    :type id: str
    """
    TYPE_URI = RDF_PREFIX["ti"] + "TextInventory"

    @property
    def members(self):
        return list(self.textgroups.values())

    def __init__(self, resource=None, name=None):
        super(TextInventory, self).__init__()
        self.resource = None
        self.textgroups = defaultdict(TextGroup)
        self.__id__ = name
        self.parents = list()
        if resource is not None:
            self.setResource(resource)

    @property
    def id(self):
        return self.__id__

    @id.setter
    def id(self, value):
        self.__id__ = value

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
