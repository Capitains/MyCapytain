# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.prototypes.cts.inventory
   :synopsis: Prototypes for repository/inventory Collection CTS objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""
from __future__ import unicode_literals
from six import text_type

from MyCapytain.resources.prototypes.metadata import Collection, ResourceCollection
from MyCapytain.common.reference import URN
from MyCapytain.common.utils import make_xml_node, xmlparser
from MyCapytain.common.constants import RDF_NAMESPACES, Mimetypes
from MyCapytain.errors import InvalidURN
from collections import defaultdict
from copy import deepcopy

from rdflib import RDF, Literal, URIRef
from rdflib.namespace import DC


class PrototypeCtsCollection(Collection):
    """ Resource represents any resource from the inventory

    :param identifier: Identifier representing the CtsTextInventoryMetadata
    :type identifier: str,URN
    :cvar CTS_MODEL: String Representation of the type of collection
    """
    CTS_MODEL = "CtsCollection"
    DC_TITLE_KEY = None
    CTS_PROPERTIES = []
    CTS_LINKS = []

    EXPORT_TO = [Mimetypes.PYTHON.ETREE]
    DEFAULT_EXPORT = Mimetypes.PYTHON.ETREE

    def __init__(self, identifier=""):
        super(PrototypeCtsCollection, self).__init__(identifier)

        if hasattr(type(self), "CTS_MODEL"):
            self.graph.set((self.asNode(), RDF.type, RDF_NAMESPACES.CTS.term(self.CTS_MODEL)))
            self.graph.set((self.asNode(), RDF_NAMESPACES.DTS.isA, RDF_NAMESPACES.CTS.term(self.CTS_MODEL)))

        self.__urn__ = ""

    @property
    def urn(self):
        return self.__urn__

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, self.__class__):
            return False
        return hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn

    def get_cts_property(self, prop, lang=None):
        """ Set given property in CTS Namespace

        .. example::
            collection.get_cts_property("groupname", "eng")

        :param prop: Property to get (Without namespace)
        :param lang: Language to get for given value
        :return: Value or default if lang is set, else whole set of values
        :rtype: dict or Literal
        """
        x = {
            obj.language: obj for obj in self.metadata.get(RDF_NAMESPACES.CTS.term(prop))
        }
        if lang is not None:
            if lang in x:
                return x[lang]
            return next(x.values())
        return x

    def set_cts_property(self, prop, value, lang=None):
        """ Set given property in CTS Namespace

        .. example::
            collection.set_cts_property("groupname", "MyCapytain", "eng")

        :param prop: Property to set (Without namespace)
        :param value: Value to set for given property
        :param lang: Language to set for given value
        """
        if not isinstance(value, Literal):
            value = Literal(value, lang=lang)
        prop = RDF_NAMESPACES.CTS.term(prop)

        if prop == self.DC_TITLE_KEY:
            self.set_label(value, lang)

        self.metadata.add(prop, value)

    # new for commentary
    def get_link(self, prop):
        """ Get given link in CTS Namespace

        .. example::
            collection.get_link("about")

        :param prop: Property to get (Without namespace)
        :return: whole set of values
        :rtype: list
        """
        return list(self.metadata.get(prop))

    def set_link(self, prop, value):
        """ Set given link in CTS Namespace

        .. example::
            collection.set_link(NAMESPACES.CTS.about, "urn:cts:latinLit:phi1294.phi002")

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
        if namespaces is True:
            attrs.update(self.__namespaces_header__(cpt=(output == Mimetypes.XML.CapiTainS.CTS)))

        TYPE_URI = self.TYPE_URI
        if TYPE_URI == RDF_NAMESPACES.CTS.term("CtsTextInventoryCollection"):
            TYPE_URI = RDF_NAMESPACES.CTS.term("TextInventory")

        strings = [make_xml_node(self.graph, TYPE_URI, close=False, attributes=attrs)]
        for pred in self.CTS_PROPERTIES:
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

        return lines.join(strings)

    def __export__(self, output=None, domain=""):
        if output == Mimetypes.PYTHON.ETREE:
            return xmlparser(self.export(output=Mimetypes.XML.CTS))


class CtsTextMetadata(ResourceCollection, PrototypeCtsCollection):
    """ Represents a CTS CtsTextMetadata

    :param urn: Identifier of the CtsTextMetadata
    :type urn: str
    :param parent: Item parents of the current collection
    :type parent: [PrototypeCtsCollection]

    :ivar urn: URN Identifier
    :type urn: URN
    """

    DC_TITLE_KEY = RDF_NAMESPACES.CTS.term("label")
    TYPE_URI = RDF_NAMESPACES.CTS.term("text")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.resource)
    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.XML.CapiTainS.CTS]
    CTS_PROPERTIES = [RDF_NAMESPACES.CTS.label, RDF_NAMESPACES.CTS.description]
    CTS_LINKS = [RDF_NAMESPACES.CTS.about]
    SUBTYPE = "unknown"

    def __init__(self, urn="", parent=None, lang=None):
        self.__subtype__ = self.SUBTYPE
        super(CtsTextMetadata, self).__init__(identifier=str(urn))
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
    def subtype(self):
        """ Subtype of the object

        :return: string representation of subtype
        """
        return self.__subtype__

    @property
    def readable(self):
        return True

    @property
    def members(self):
        """ Children of the collection's item

        .. warning:: CapitainsCtsText has no children

        :rtype: list
        """
        return []

    @property
    def descendants(self):
        """ Descendants of the collection's item

        .. warning:: CapitainsCtsText has no Descendants

        :rtype: list
        """
        return []

    def translations(self, key=None):
        """ Get translations in given language

        :param key: Language ISO Code to filter on
        :return:
        """
        return self.parent.get_translation_in(key)

    def editions(self):
        """ Get all editions of the texts

        :return: List of editions
        :rtype: [CtsTextMetadata]
        """
        return [
                item
                for urn, item in self.parent.children.items()
                if isinstance(item, CtsEditionMetadata)
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
            for pred in self.CTS_PROPERTIES:
                for obj in self.metadata.get(pred):
                    strings.append(
                        make_xml_node(
                            self.graph, pred, attributes={"xml:lang": obj.language}, text=str(obj), complete=True
                        )
                    )

            for pred in self.CTS_LINKS:
                # For each predicate in CTS_LINKS
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
                        self.graph, RDF_NAMESPACES.CTS.term("online"), complete=True,
                        # XmlCtsCitation Mapping
                        innerXML=make_xml_node(
                            self.graph, RDF_NAMESPACES.CTS.term("citationMapping"), complete=True,
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

    def get_creator(self, lang=None):
        """ Get the DC Creator literal value

        :param lang: Language to retrieve
        :return: Creator string representation
        :rtype: Literal
        """
        return self.parent.parent.metadata.get_label(lang=lang)

    def get_title(self, lang=None):
        """ Get the DC Title of the object

        :param lang: Lang to retrieve
        :return: Title string representation
        :rtype: Literal
        """
        return self.parent.metadata.get_label(lang=lang)

    def get_description(self, lang=None):
        """ Get the DC description of the object

        :param lang: Lang to retrieve
        :return: Description string representation
        :rtype: Literal
        """
        return self.metadata.get_single(key=RDF_NAMESPACES.CTS.description, lang=lang)

    def get_subject(self, lang=None):
        """ Get the DC subject of the object

        :param lang: Lang to retrieve
        :return: Subject string representation
        :rtype: Literal
        """
        return self.get_label(lang=lang)


class CtsEditionMetadata(CtsTextMetadata):
    """ Represents a CTS XmlCtsEditionMetadata

    :param urn: Identifier of the CtsTextMetadata
    :type urn: str
    :param parent: Parent of current item
    :type parent: CtsWorkMetadata
    """
    TYPE_URI = RDF_NAMESPACES.CTS.term("edition")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.resource)
    SUBTYPE = "edition"


class CtsTranslationMetadata(CtsTextMetadata):
    """ Represents a CTS XmlCtsTranslationMetadata

    :param urn: Identifier of the CtsTextMetadata
    :type urn: str
    :param parent: Parent of current item
    :type parent: CtsWorkMetadata
    :param lang: Language of the translation
    :type lang: Lang
    """
    TYPE_URI = RDF_NAMESPACES.CTS.term("translation")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.resource)
    SUBTYPE = "translation"


class CtsCommentaryMetadata(CtsTextMetadata):
    """ Represents a CTS Commentary

    :param urn: Identifier of the PrototypeText
    :type urn: str
    :param parent: Parent of current item
    :type parent: PrototypeWork
    :param lang: Language of the commentary
    :type lang: Lang
    """
    TYPE_URI = RDF_NAMESPACES.CTS.term("commentary")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.resource)
    SUBTYPE = "commentary"


class CtsWorkMetadata(PrototypeCtsCollection):
    """ Represents a CTS CtsWorkMetadata

    CTS CtsWorkMetadata can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param urn: Identifier of the CtsWorkMetadata
    :type urn: str
    :param parent: Parent of current object
    :type parent: CtsTextgroupMetadata

    :ivar urn: URN Identifier
    :type urn: URN
    """

    DC_TITLE_KEY = RDF_NAMESPACES.CTS.term("title")
    TYPE_URI = RDF_NAMESPACES.CTS.term("work")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.XML.CapiTainS.CTS]
    CTS_PROPERTIES = [RDF_NAMESPACES.CTS.term("title")]

    def __init__(self, urn=None, parent=None):
        super(CtsWorkMetadata, self).__init__(identifier=str(urn))
        self.__urn__ = URN(urn)
        self.__children__ = defaultdict(CtsTextMetadata)

        if parent is not None:
            self.parent = parent

    @property
    def texts(self):
        """ Texts

        :return: Dictionary of texts
        :rtype: defaultdict(:class:`PrototypeTexts`)
        """
        return self.__children__

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
        """ Merge two XmlCtsWorkMetadata Objects.

        - Original (left Object) keeps his parent.
        - Added document overwrite text if it already exists

        :param other: XmlCtsWorkMetadata object
        :type other: CtsWorkMetadata
        :return: XmlCtsWorkMetadata Object
        :rtype XmlCtsWorkMetadata:
        """
        if not isinstance(other, CtsWorkMetadata):
            raise TypeError("Cannot add %s to CtsWorkMetadata" % type(other))
        elif self.urn != other.urn:
            raise InvalidURN("Cannot add CtsWorkMetadata %s to CtsWorkMetadata %s " % (self.urn, other.urn))

        for urn, text in other.texts.items():
            self.texts[urn] = text
            self.texts[urn].parent = self
            self.texts[urn].resource = None

        return self

    def get_translation_in(self, key=None):
        """ Find a translation with given language

        :param key: Language to find
        :type key: text_type
        :rtype: [CtsTextMetadata]
        :returns: List of availables translations
        """
        if key is not None:
            return [
                item
                for item in self.texts.values()
                if isinstance(item, CtsTranslationMetadata) and item.lang == key
                ]
        else:
            return [
                item
                for item in self.texts.values()
                if isinstance(item, CtsTranslationMetadata)
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


class CtsTextgroupMetadata(PrototypeCtsCollection):
    """ Represents a CTS Textgroup

    CTS CtsTextgroupMetadata can be added to each other which would most likely happen if you take your data from multiple API or \
    Textual repository. This works close to dictionary update in Python. See update

    :param urn: Identifier of the CtsTextgroupMetadata
    :type urn: str
    :param parent: Parent of the current object
    :type parent: CtsTextInventoryMetadata

    :ivar urn: URN Identifier
    :type urn: URN
    """
    DC_TITLE_KEY = RDF_NAMESPACES.CTS.term("groupname")
    TYPE_URI = RDF_NAMESPACES.CTS.term("textgroup")
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.XML.CTS, Mimetypes.XML.CapiTainS.CTS]
    CTS_PROPERTIES = [RDF_NAMESPACES.CTS.groupname]

    def __init__(self, urn="", parent=None):
        super(CtsTextgroupMetadata, self).__init__(identifier=str(urn))
        self.__urn__ = URN(urn)
        self.__children__ = defaultdict(CtsWorkMetadata)

        if parent is not None:
            self.parent = parent

    @property
    def works(self):
        """ Works

        :return: Dictionary of works
        :rtype: defaultdict(:class:`PrototypeWorks`)
        """
        return self.__children__

    def update(self, other):
        """ Merge two Textgroup Objects.

        - Original (left Object) keeps his parent.
        - Added document merges with work if it already exists

        :param other: Textgroup object
        :type other: CtsTextgroupMetadata
        :return: Textgroup Object
        :rtype: CtsTextgroupMetadata
        """
        if not isinstance(other, CtsTextgroupMetadata):
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


class CtsTextInventoryMetadata(PrototypeCtsCollection):
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
        super(CtsTextInventoryMetadata, self).__init__(identifier=name)
        self.__children__ = defaultdict(CtsTextgroupMetadata)

        if parent is not None:
            self.parent = parent

    @property
    def textgroups(self):
        """ Textgroups

        :return: Dictionary of textgroups
        :rtype: defaultdict(:class:`CtsTextgroupMetadata`)
        """
        return self.__children__

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


class CtsTextInventoryCollection(PrototypeCtsCollection):
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
        super(CtsTextInventoryCollection, self).__init__(identifier=identifier)
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
                return Collection.__export__(self, output=output, domain=domain)
            else:
                return self.members[0].export(output=output, domain=domain)
