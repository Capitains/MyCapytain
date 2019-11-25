# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.prototypes.cts.inventory
   :synopsis: Prototypes for repository/inventory Collection CTS objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""
from __future__ import unicode_literals
from six import text_type

from MyCapytain.resources.prototypes.metadata import Collection, ResourceCollection
from MyCapytain.common.reference._capitains_cts import URN
from MyCapytain.common.utils.xml import make_xml_node, xmlparser
from MyCapytain.common.constants import RDF_NAMESPACES, Mimetypes
from MyCapytain.errors import InvalidURN
from collections import defaultdict
from copy import deepcopy

from rdflib import RDF, Literal, URIRef
from rdflib.namespace import DC

__all__ = [
    "PrototypeCapitainsCollection",
    "CapitainsTextInventoryCollection",
    "CapitainsCollectionMetadata",
    "CapitainsTextgroupMetadata",
    "CapitainsTextInventoryMetadata",
    "CapitainsReadableMetadata",
]


class PrototypeCapitainsCollection(Collection):
    """ Resource represents any resource from the inventory

    :param identifier: Identifier representing the CtsTextInventoryMetadata
    :type identifier: str,URN
    :cvar CTS_MODEL: String Representation of the type of collection
    """
    DC_TITLE_KEY = None
    CAPITAINS_PROPERTIES = []
    CAPITAINS_LINKS = []

    EXPORT_TO = [Mimetypes.PYTHON.ETREE]
    DEFAULT_EXPORT = Mimetypes.PYTHON.ETREE
    SUBTYPE = ["unknown"]

    def __init__(self, identifier=""):
        super(PrototypeCapitainsCollection, self).__init__(identifier)

        self.__urn__ = ""
        self.__subtype__ = self.SUBTYPE

    @property
    def urn(self):
        return self.__urn__

    @property
    def subtype(self):
        """ Subtype of the object

        :return: string representation of subtype
        """
        return ', '.join(self.__subtype__)

    @subtype.setter
    def subtype(self, val):
        """ Set the subtype of the object

        :param val: the objects subtype
        """
        if type(val) == list:
            self.__subtype__ = val
        else:
            self.__subtype__ = list(val)

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, self.__class__):
            return False
        return hasattr(self, "id") and hasattr(other, "id") and self.id == other.id

    def get_capitains_property(self, prop, lang=None):
        """ Set given property in CAPITAINS Namespace

        .. example::
            collection.get_capitains_property("groupname", "eng")

        :param prop: Property to get (Without namespace)
        :param lang: Language to get for given value
        :return: Value or default if lang is set, else whole set of values
        :rtype: dict or Literal
        """
        x = {
            obj.language: obj for obj in self.metadata.get(RDF_NAMESPACES.CAPITAINS.term(prop))
        }
        if lang is not None:
            if lang in x:
                return x[lang]
            return next(iter(x.values()))
        return x

    def set_capitains_property(self, prop, value, lang=None):
        """ Set given property in CAPITAINS Namespace

        .. example::
            collection.set_capitains_property("groupname", "MyCapytain", "eng")

        :param prop: Property to set (Without namespace)
        :param value: Value to set for given property
        :param lang: Language to set for given value
        """
        if not isinstance(value, Literal):
            value = Literal(value, lang=lang)
        prop = RDF_NAMESPACES.CAPITAINS.term(prop)

        if prop == self.DC_TITLE_KEY:
            self.set_label(value, lang)

        self.metadata.add(prop, value)

    # new for commentary
    def get_link(self, prop):
        """ Get given link in CAPITAINS Namespace

        .. example::
            collection.get_link("about")

        :param prop: Property to get (Without namespace)
        :return: whole set of values
        :rtype: list
        """
        return list(self.metadata.get(prop))

    def set_link(self, prop, value):
        """ Set given link in CAPITAINS Namespace

        .. example::
            collection.set_link(NAMESPACES.CAPITAINS.about, "urn:cts:latinLit:phi1294.phi002")

        :param prop: Property to set (Without namespace)
        :param value: Value to set for given property
        """
        # https://rdflib.readthedocs.io/en/stable/
        # URIRef == identifiers (urn, http, URI in general)
        # Literal == String or Number (can have a language)
        # BNode == Anonymous nodes (So no specific identifier)
        #		eg. BNode : Edition(MartialEpigrams:URIRef) ---has_metadata--> Metadata(BNode)
        if not isinstance(value, URIRef):
            value = URIRef(value)

        self.metadata.add(prop, value)

    def __xml_export_generic__(self, attrs, namespaces=False, lines="\n", members=None, output=None):
        """ Shared method for Mimetypes.XML.CTS Export

        :param attrs: Dictionary of attributes for the node
        :param namespaces: Add namespaces to the node
        :param lines: New Line Character (Can be empty)
        :return: String representation of XML Nodes
        """

        TYPE_URI = self.TYPE_URI

        strings = []
        for pred in self.CAPITAINS_PROPERTIES:
            for obj in self.metadata.get(pred):
                strings.append(
                    make_xml_node(
                        self.graph, pred, attributes={"xml:lang": obj.language}, text=str(obj), complete=True
                    )
                )

        if output == Mimetypes.XML.CapiTainS.CTS:
            strings.append(make_xml_node(self.graph, RDF_NAMESPACES.CAPITAINS.term("structured-metadata")))
            strings.append(
                self.metadata.export(
                    Mimetypes.XML.CapiTainS.CTS,
                    exclude=[RDF_NAMESPACES.CTS, RDF_NAMESPACES.DTS, RDF])
            )
            strings.append(make_xml_node(self.graph, RDF_NAMESPACES.CAPITAINS.term("structured-metadata"), close=True))

        if members is None:
            members = self.members
        for obj in members:
            strings.append(obj.export(output, namespaces=False))

        strings.append(make_xml_node(self.graph, TYPE_URI, close=True))

        if namespaces is True:
            attrs.update(self.__namespaces_header__(cpt=(output == Mimetypes.XML.CapiTainS.CTS)))

        strings = [make_xml_node(self.graph, TYPE_URI, close=False, attributes=attrs)] + strings

        return lines.join(strings)

    def __export__(self, output=None, domain=""):
        if output == Mimetypes.PYTHON.ETREE:
            return xmlparser(self.export(output=Mimetypes.XML.CTS))


class CapitainsReadableMetadata(ResourceCollection, PrototypeCapitainsCollection):
    """ Represents a CAPITAINS CapitainsTextMetadata

    :param urn: Identifier of the CapitainsTextMetadata
    :type urn: str
    :param parent: Item parents of the current collection
    :type parent: [PrototypeCapitainsCollection]

    :ivar urn: URN Identifier
    :type urn: URN
    """

    DC_TITLE_KEY = RDF_NAMESPACES.CAPITAINS.term("title")
    TYPE_URI = RDF_NAMESPACES.CAPITAINS.term("readable")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.resource)
    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.XML.CapiTainS.CTS]
    CAPITAINS_PROPERTIES = [RDF_NAMESPACES.CAPITAINS.label, RDF_NAMESPACES.CAPITAINS.description]
    CAPITAINS_LINKS = [RDF_NAMESPACES.CAPITAINS.about]

    def __init__(self, urn="", parent=None, lang=None):
        super(CapitainsReadableMetadata, self).__init__(identifier=str(urn))
        self.resource = None
        self.citation = None
        self.__urn__ = URN(urn)
        self.docname = None
        self.validate = None
        if lang is not None:
            self.lang = lang

        if parent is not None:
            self.parent = parent
            if lang is None:
                self.lang = self.parent.lang

    @property
    def readable(self):
        return True

    @property
    def members(self):
        """ Children of the collection's item

        .. warning:: CapitainsCtsText has no children

        :rtype: list
        """
        return list()

    @property
    def descendants(self):
        """ Descendants of the collection's item

        .. warning:: CapitainsCtsText has no Descendants

        :rtype: list
        """
        return list()

    def translations(self, key=None):
        """ Get translations in given language

        :param key: Language ISO Code to filter on
        :return:
        """
        return self.parent.get_translation_in(key)

    @property
    def readable_siblings(self):
        """ Get all readable siblings of the text

        :return: List of readable siblings
        :rtype: [CapitainsTextMetadata]
        """
        return [
                item
                for item in self.parent.readableDescendants
        ]

    def __export__(self, output=None, domain="", namespaces=True, lines="\n"):
        """ Create a {output} version of the CapitainsCtsText

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :returns: Desired output formatted resource
        """
        if output == Mimetypes.XML.CTS or output == Mimetypes.XML.CapiTainS.CTS:
            attrs = {"urn": self.id, "xml:lang": self.lang}
            if self.parent is not None and self.parent.id:
                attrs["workUrn"] = self.parent.id
            if namespaces is True:
                attrs.update(self.__namespaces_header__(cpt=(output==Mimetypes.XML.CapiTainS.CTS)))

            strings = [make_xml_node(self.graph, self.TYPE_URI, close=False, attributes=attrs)]

            # additional = [make_xml_node(self.graph, RDF_NAMESPACES.CTS.extra)]
            for pred in self.CAPITAINS_PROPERTIES:
                for obj in self.metadata.get(pred):
                    strings.append(
                        make_xml_node(
                            self.graph, pred, attributes={"xml:lang": obj.language}, text=str(obj), complete=True
                        )
                    )

            for pred in self.CAPITAINS_LINKS:
                # For each predicate in CAPITAINS_LINKS
                for obj in self.metadata.get(pred):
                    # For each item in the graph connected to the current item metadata as object through the predicate "pred"
                    strings.append(
                        make_xml_node(
                            self.graph, pred, attributes={"urn": str(obj)}, complete=True
                        )
                        # <pref urn="obj.language"/>
                    )

            # Citation !
            if self.citation is not None:
                strings.append(
                    # Online
                    make_xml_node(
                        self.graph, RDF_NAMESPACES.CAPITAINS.term("online"), complete=True,
                        # XmlCtsCitation Mapping
                        innerXML=make_xml_node(
                            self.graph, RDF_NAMESPACES.CAPITAINS.term("citationMapping"), complete=True,
                            innerXML=self.citation.export(Mimetypes.XML.CTS)
                        )
                    )
                )

            if output == Mimetypes.XML.CapiTainS.CTS:
                strings.append(make_xml_node(self.graph, RDF_NAMESPACES.CAPITAINS.term("structured-metadata")))
                strings.append(
                    self.metadata.export(
                        Mimetypes.XML.CapiTainS.CTS,
                        exclude=[RDF_NAMESPACES.CTS, RDF_NAMESPACES.DTS, RDF])
                )
                strings.append(
                    make_xml_node(self.graph, RDF_NAMESPACES.CAPITAINS.term("structured-metadata"), close=True)
                )

            strings.append(make_xml_node(self.graph, self.TYPE_URI, close=True))

            return lines.join(strings)

    def get_root_collection(self, lang=None):
        """ Get the label of the root collection as a literal value

        :param lang: Language to retrieve
        :return: Creator string representation
        :rtype: Literal
        """
        ancestor = self.parent
        while ancestor.parent:
            ancestor = ancestor.parent
        return ancestor.get_label(lang=lang)

    def get_title(self, lang=None):
        """ Get the DC Title of the object

        :param lang: Lang to retrieve
        :return: Title string representation
        :rtype: Literal
        """
        return self.parent.get_label(lang=lang)

    def get_description(self, lang=None):
        """ Get the DC description of the object

        :param lang: Lang to retrieve
        :return: Description string representation
        :rtype: Literal
        """
        return self.metadata.get_single(key=RDF_NAMESPACES.CAPITAINS.description, lang=lang)

    def get_subject(self, lang=None):
        """ Get the DC subject of the object

        :param lang: Lang to retrieve
        :return: Subject string representation
        :rtype: Literal
        """
        return self.get_label(lang=lang)


class CapitainsCollectionMetadata(PrototypeCapitainsCollection):
    """ Represents a CAPITAINS CapitainsCollectionMetadata

    CAPITAINS CapitainsCollectionMetadata can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param urn: Identifier of the CAPITAINS
    :type urn: str
    :param parent: Parent of current object
    :type parent: CapitainsCollectionMetadata

    :ivar urn: URN Identifier
    :type urn: URN
    """

    DC_TITLE_KEY = RDF_NAMESPACES.CAPITAINS.term("title")
    TYPE_URI = RDF_NAMESPACES.CAPITAINS.term("collection")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.XML.CapiTainS.CTS]
    CAPITAINS_PROPERTIES = [RDF_NAMESPACES.CAPITAINS.term("title")]

    def __init__(self, urn=None, parent=None):
        super(CapitainsCollectionMetadata, self).__init__(identifier=str(urn))
        self.__urn__ = str(urn)
        self.__children__ = defaultdict(CapitainsReadableMetadata)

        if parent is not None:
            self.parent = parent

    @property
    def texts(self):
        """ Texts

        :return: List of readable descendants
        :rtype: {str: CapitainsReadableMetadata}
        """
        return {item.id: item for item in self.readableDescendants}

    @property
    def collections(self):
        """ The sub-collections in this collection

        :return: List of sub-collections
        :rtype: {str: CapitainsCollectionMetadata}
        """
        return {collection.id: collection for collection in self.members if collection.readable is False}

    @property
    def lang(self):
        """ Languages this text is in

        :return: List of available languages
        """
        return str(self.graph.value(self.asNode(), DC.language))

    @lang.setter
    def lang(self, lang):
        """ Language this text is available in

        :param lang: Language to add
        :type lang: str
        """
        self.graph.set((self.asNode(), DC.language, Literal(lang)))

    def update(self, other):
        """ Merge two CapitainsCollectionMetadata Objects.

        - Original (left Object) keeps his parent.
        - Added document overwrite text if it already exists

        :param other: CapitainsCollectionMetadata object
        :type other: CapitainsCollectionMetadata
        :return: CapitainsCollectionMetadata Object
        :rtype : CapitainsCollectionMetadata
        """
        if not isinstance(other, CapitainsCollectionMetadata):
            raise TypeError("Cannot add %s to CapitainsCollectionMetadata" % type(other))
        elif self.urn != other.urn:
            raise InvalidURN("Cannot add CapitainsCollectionMetadata %s to CapitainsCollectionMetadata %s " % (self.urn, other.urn))

        # This is necessary because self.texts cannot just call self.children since not all children will be readable
        if self.texts:
            texts = self.texts
        else:
            texts = dict()

        for id, text in other.texts.items():
            texts[id] = text
            texts[id].parent = self
            texts[id].resource = None

        self.texts.update(texts)

        return self

    def get_translation_in(self, key=None):
        """ Find a translation with given language

        :param key: Language to find
        :type key: text_type
        :rtype: [CapitainsReadableMetadata]
        :returns: List of available translations
        """
        if key is not None:
            return [
                item
                for item in self.texts
                if item.lang == key
                ]
        else:
            return [
                item
                for item in self.texts
                if item.subtype == 'cts:translation'
            ]

    def __len__(self):
        """ Get the number of text in the CtsWorkMetadata

        :return: Number of texts available in the inventory
        """
        return len(self.texts)

    def __export__(self, output=None, domain="", namespaces=True):
        """ Create a {output} version of the XmlCtsWorkMetadata

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :returns: Desired output formated resource
        """
        if output == Mimetypes.XML.CTS or output == Mimetypes.XML.CapiTainS.CTS:
            attrs = {"urn": self.id, "xml:lang": self.lang}
            if self.parent is not None and self.parent.id:
                attrs["groupUrn"] = self.parent.id
            return self.__xml_export_generic__(attrs, namespaces=namespaces, output=output)


class CapitainsTextgroupMetadata(PrototypeCapitainsCollection):
    """ Represents a CTS Textgroup

    CTS CtsTextgroupMetadata can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param urn: Identifier of the CtsTextgroupMetadata
    :type urn: str
    :param parent: Parent of the current object
    :type parent: CapitainsTextInventoryMetadata

    :ivar urn: URN Identifier
    :type urn: URN
    """
    DC_TITLE_KEY = RDF_NAMESPACES.CTS.term("groupname")
    TYPE_URI = RDF_NAMESPACES.CTS.term("textgroup")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.XML.CapiTainS.CTS]
    CTS_PROPERTIES = [RDF_NAMESPACES.CTS.groupname]

    def __init__(self, urn="", parent=None):
        super(CapitainsTextgroupMetadata, self).__init__(identifier=str(urn))
        self.__urn__ = URN(urn)
        self.__children__ = defaultdict(CapitainsCollectionMetadata)

        if parent is not None:
            self.parent = parent

    @property
    def works(self):
        """ Works

        :return: Dictionary of works
        :rtype: defaultdict(:class:`PrototypeWorks`)
        """
        return self.children

    def update(self, other):
        """ Merge two Textgroup Objects.

        - Original (left Object) keeps his parent.
        - Added document merges with work if it already exists

        :param other: Textgroup object
        :type other: CapitainsTextgroupMetadata
        :return: Textgroup Object
        :rtype: CapitainsTextgroupMetadata
        """
        if not isinstance(other, CapitainsTextgroupMetadata):
            raise TypeError("Cannot add %s to CtsTextgroupMetadata" % type(other))
        elif str(self.urn) != str(other.urn):
            raise InvalidURN("Cannot add CtsTextgroupMetadata %s to CtsTextgroupMetadata %s " % (self.urn, other.urn))

        for urn, work in other.works.items():
            if urn in self.works:
                self.works[urn].update(deepcopy(work))
            else:
                self.works[urn] = deepcopy(work)
            self.works[urn].parent = self
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

    def __export__(self, output=None, domain="", namespaces=True):
        """ Create a {output} version of the XmlCtsTextgroupMetadata

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :returns: Desired output formated resource
        """
        if output == Mimetypes.XML.CTS or output == Mimetypes.XML.CapiTainS.CTS:
            attrs = {"urn": self.id}
            return self.__xml_export_generic__(attrs, namespaces=namespaces, output=output)


class CapitainsTextInventoryMetadata(PrototypeCapitainsCollection):
    """ Initiate a CtsTextInventoryMetadata resource

    :param resource: Resource representing the CtsTextInventoryMetadata
    :type resource: Any
    :param name: Identifier of the CtsTextInventoryMetadata
    :type name: str
    """
    DC_TITLE_KEY = RDF_NAMESPACES.CTS.term("name")
    TYPE_URI = RDF_NAMESPACES.CTS.term("TextInventory")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.XML.CapiTainS.CTS]

    def __init__(self, name="defaultInventory", parent=None):
        super(CapitainsTextInventoryMetadata, self).__init__(identifier=name)
        self.__children__ = defaultdict(CapitainsTextgroupMetadata)

        if parent is not None:
            self.parent = parent

    @property
    def textgroups(self):
        """ Textgroups

        :return: Dictionary of textgroups
        :rtype: defaultdict(:class:`CtsTextgroupMetadata`)
        """
        return self.children

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

    def __export__(self, output=None, domain="", namespaces=True):
        """ Create a {output} version of the CtsTextInventoryMetadata

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :param namespaces: List namespaces in main node
        :returns: Desired output formated resource
        """
        if output == Mimetypes.XML.CTS or output == Mimetypes.XML.CapiTainS.CTS:
            attrs = {}
            if self.id:
                attrs["tiid"] = self.id

            return self.__xml_export_generic__(attrs, namespaces=namespaces, output=output)


class CapitainsTextInventoryCollection(PrototypeCapitainsCollection):
    """ Initiate a CtsTextInventoryMetadata resource

    :param resource: Resource representing the CtsTextInventoryMetadata
    :type resource: Any
    :param name: Identifier of the CtsTextInventoryMetadata
    :type name: str
    """
    DC_TITLE_KEY = RDF_NAMESPACES.CTS.term("name")
    TYPE_URI = RDF_NAMESPACES.CTS.term("CtsTextInventoryCollection")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.JSON.DTS.Std, Mimetypes.XML.CapiTainS.CTS]

    def __init__(self, identifier="default"):
        super(CapitainsTextInventoryCollection, self).__init__(identifier=identifier)
        self.__children__ = dict()

    def __len__(self):
        """ Get the number of text in the Inventory

        :return: Number of texts available in the inventory
        """
        return len([
            text
            for inv in self.members
            for tg in inv.textgroups.values()
            for work in tg.works.values()
            for text in work.texts.values()
        ])

    def __export__(self, output=None, domain="", namespaces=True):
        """ Create a {output} version of the CtsTextInventoryMetadata

        :param output: Format to be chosen
        :type output: basestring
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :param namespaces: List namespaces in main node
        :returns: Desired output formated resource
        """
        if output == Mimetypes.XML.CTS:
            attrs = {}
            if self.id:
                attrs["tiid"] = self.id

            return self.__xml_export_generic__(
                attrs,
                namespaces=namespaces,
                members=[
                    m for inv in self.members for m in inv.members
                ],
                output=Mimetypes.XML.CTS
            )
        elif output == Mimetypes.JSON.DTS.Std:
            if len(self.members) > 1:
                return Collection.__export__(self, output=output)
            else:
                return self.members[0].export(output=output)
