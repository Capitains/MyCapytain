# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.prototypes.cts.inventory
   :synopsis: Prototypes for repository/inventory Collection CTS objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""
from __future__ import unicode_literals

from MyCapytain.resources.prototypes.metadata import Collection, ResourceCollection
from MyCapytain.common.reference._capitains_cts import URN
from MyCapytain.common.utils.xml import make_xml_node, xmlparser
from MyCapytain.common.constants import RDF_NAMESPACES, Mimetypes, GRAPH_BINDINGS
from MyCapytain.errors import InvalidURN
from collections import defaultdict

from rdflib import RDF, Literal, URIRef
from rdflib.namespace import DC
from typing import List

__all__ = [
    "PrototypeCapitainsCollection",
    "CapitainsCollectionMetadata",
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

    EXPORT_TO = [Mimetypes.PYTHON.ETREE, Mimetypes.XML.GUIDELINES3]
    DEFAULT_EXPORT = Mimetypes.PYTHON.ETREE
    SUBTYPE = "unknown"
    TYPE_URI = RDF_NAMESPACES.CAPITAINS.term("collection")
    COLLECTION_ATTRIBUTES = ['path', 'readable']

    def __init__(self, identifier=""):
        super(PrototypeCapitainsCollection, self).__init__(identifier)

        self.__urn__ = ""
        self.__subtype__ = self.SUBTYPE
        self._parent = list()

    @property
    def urn(self):
        return self.__urn__

    @property
    def subtype(self):
        """ Subtype of the object

        :return: string representation of subtype
        """
        return self.__subtype__

    @subtype.setter
    def subtype(self, val):
        """ Set the subtype of the object

        :param val: the object's subtype
        """
        if isinstance(val, str):
            self.__subtype__ = val
        else:
            self.__subtype__ = str(val)

    @property
    def parents(self) -> List["Collection"]:
        """ Iterator to find parents of current collection, from closest to furthest

        :rtype: Generator[:class:`Collection`]
        """
        p = self.parent
        parents = []
        while p != []:
            parents.extend(p)
            new_p = []
            for parent in p:
                if isinstance(parent, list):
                    new_p.extend([par.parent for par in parent])
                else:
                    new_p.extend(parent.parent)
            p = new_p
        return parents

    @property
    def parent(self):
        """ Parent of current object

        :rtype: [Collection]
        """
        return self._parent

    @parent.setter
    def parent(self, parent):
        """ Parents

        :param parent: Parent to set for the object
        :type parent: Collection
        :return:
        """
        if parent not in self._parent:
            self._parent.append(parent)
            self.graph.add(
                (self.asNode(), RDF_NAMESPACES.CAPITAINS.parent, parent.asNode())
            )
            parent._add_member(self)

    def get_label(self, lang=None):
        """ Return label for given lang or any default

        :param lang: Language to request
        :return: Label value
        :rtype: Literal
        """
        x = None
        if lang is None:
            for obj in self.graph.objects(self.asNode(), DC.title):
                return obj
        for obj in self.graph.objects(self.asNode(), DC.title):
            if obj.language == lang:
                return obj
        return x

    def set_label(self, label, lang):
        return NotImplementedError('Use obj.metadata.add(DC.title, {}, {}) to add a title to collection'.format(label,
                                                                                                                lang))

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, self.__class__):
            return False
        return hasattr(self, "id") and hasattr(other, "id") and self.id == other.id

    def get_capitains_property(self, prop, lang=None):
        """ Get given property in CAPITAINS Namespace

        .. example::
            collection.get_capitains_property("groupname", "eng")

        :param prop: Property to get (Without namespace)
        :param lang: Language to get for given value
        :return: Value or default if lang is set, else whole set of values
        :rtype: dict([Literal]) or [Literal]
        """
        x = defaultdict(list)
        for obj in self.metadata.get(RDF_NAMESPACES.CAPITAINS.term(prop)):
            x[getattr(obj, 'language', "")].append(obj)
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

    def __export__(self, output=None, domain="", namespaces=True, lines="\n", recursion_depth=0):
        """

        :param output: output format
        :type output: MyCapytain.common.constants.Mimetypes
        :param domain: Domain to prefix IDs when necessary
        :type domain: str
        :param namespaces: Whether to include namespaces on the root node for XML output
        :type namespaces: bool
        :param lines: The character to use to separate the lines for the XML output
        :type lines: str
        :param recursion_depth: The depth to recurse from the base collection: 0: no children, 1: children, 2: children + grandchildren, etc.
        :return:
        """
        if output == Mimetypes.XML.GUIDELINES3:
            element_dict = self.export(output=Mimetypes.JSON.LD)
            element_dict.pop('@context')
            metadata_strings = []
            structured_strings = []
            child_strings = []
            used_namespaces = {'dc', 'cpt'}
            for k, v in element_dict.items():
                ns_plus_tag = k.split(':')
                if ns_plus_tag[0] in ['dc', 'cpt']:
                    for member in v:
                        attrs = None
                        if member['@lang']:
                            attrs = {'xml:lang': member['@lang']}
                        if ns_plus_tag[1] == 'children':
                            if recursion_depth > 0:
                                child_strings.append(member['@object'].export(output=Mimetypes.XML.GUIDELINES3,
                                                                              namespaces=False,
                                                                              recursion_depth=recursion_depth - 1))
                        else:
                            metadata_strings.append(make_xml_node(self.graph,
                                                                  GRAPH_BINDINGS[ns_plus_tag[0]].term(ns_plus_tag[-1]),
                                                                  text=member['@value'],
                                                                  complete=True,
                                                                  attributes=attrs))
                elif ns_plus_tag[0] not in ['dts']:
                    for member in v:
                        attrs = None
                        if member['@lang']:
                            attrs = {'xml:lang': member['@lang']}
                        structured_strings.append(make_xml_node(self.graph,
                                                                GRAPH_BINDINGS[ns_plus_tag[0]].term(ns_plus_tag[-1]),
                                                                text=member['@value'],
                                                                complete=True,
                                                                attributes=attrs))
                    used_namespaces.add(ns_plus_tag[0])

            attrs = {x: getattr(self, x, None) for x in self.COLLECTION_ATTRIBUTES}
            if attrs.get('readable', None):
                attrs['readable'] = 'true'
            else:
                attrs.pop('readable', None)
            if namespaces is True:
                attrs.update(self.__namespaces_header__(cpt=False))

            strings = [make_xml_node(self.graph, self.TYPE_URI, close=False, attributes=attrs)]
            strings += metadata_strings
            if child_strings:
                strings.append(make_xml_node(self.graph, RDF_NAMESPACES.CAPITAINS.term("members")))
                strings += child_strings
                strings.append(make_xml_node(self.graph, RDF_NAMESPACES.CAPITAINS.term("members"), close=True))
            strings.append(make_xml_node(self.graph, RDF_NAMESPACES.CAPITAINS.term("structured-metadata")))
            strings += structured_strings
            strings.append(
                    make_xml_node(self.graph, RDF_NAMESPACES.CAPITAINS.term("structured-metadata"), close=True)
                )
            strings.append(make_xml_node(self.graph, self.TYPE_URI, close=True))

            return lines.join(strings)
        elif output == Mimetypes.PYTHON.ETREE:
            return xmlparser(self.export(output=Mimetypes.XML.GUIDELINES3, recursion_depth=recursion_depth))


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
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.resource)
    EXPORT_TO = [Mimetypes.XML.GUIDELINES3]
    CAPITAINS_PROPERTIES = [RDF_NAMESPACES.CAPITAINS.identifier, RDF_NAMESPACES.CAPITAINS.parent]
    CAPITAINS_LINKS = [RDF_NAMESPACES.CAPITAINS.about]

    def __init__(self, urn="", parent=None, lang=None):
        super(CapitainsReadableMetadata, self).__init__(identifier=str(urn))
        self.resource = None
        self.citation = None
        self.__urn__ = str(urn)
        self.docname = None
        self.validate = None
        self.lang = lang

        if parent is not None:
            self.parent = parent

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
        sibs = dict()
        for parent in self.parent:
            sibs.update({x.id: x for x in parent.readableDescendants})
        sibs.pop(self.id, None)
        return list(sibs.values())

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
        return self.get_label(lang=lang)

    def get_description(self, lang=None):
        """ Get the DC description of the object

        :param lang: Lang to retrieve
        :return: Description string representation
        :rtype: Literal
        """
        return self.metadata.get_single(key=DC.description, lang=lang)

    def get_subject(self, lang=None):
        """ Get the DC subject of the object

        :param lang: Lang to retrieve
        :return: Subject string representation
        :rtype: Literal
        """
        return self.metadata.get_single(key=DC.subject, lang=lang)


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
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.XML.GUIDELINES3]
    CAPITAINS_PROPERTIES = [RDF_NAMESPACES.CAPITAINS.title]

    def __init__(self, urn=None, parent=None):
        super(CapitainsCollectionMetadata, self).__init__(identifier=str(urn))
        self.__urn__ = str(urn)
        self.__children__ = defaultdict(CapitainsReadableMetadata)

        if parent is not None:
            self.parent = parent

    @property
    def texts(self):
        """ Texts

        :return: Readable descendants
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
        self_descendants = {x.id: x for x in self.descendants}
        # The sorting here is to make sure that the new descendants that are added to self will be processed first.
        # This is so that a descendant in other that is also in self but has a different parent in other will have its parent attribute correctly expanded.
        for other_descendant in sorted(other.descendants, key=lambda x: x.id in self_descendants.keys()):
            if other_descendant.id in self_descendants.keys():
                if other_descendant.readable is False:
                    self[other_descendant.id].update(other_descendant)
                for parent in other_descendant.parent + self_descendants[other_descendant.id].parent:
                    self[other_descendant.id].parent = parent
            else:
                new_parents = []
                for parent in other_descendant.parent:
                    if parent.id in self_descendants.keys() or parent.id == self.id:
                        new_parents.append(self[parent.id])
                    else:
                        new_parents.append(parent)
                other_descendant._parent = []
                for parent in new_parents:
                    other_descendant.parent = parent

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
                for item in self.readableDescendants
                if item.lang == key
                ]
        else:
            return [
                item
                for item in self.readableDescendants
                if item.subtype == 'cts:translation'
            ]

    def __len__(self):
        """ Get the number of text in the CtsWorkMetadata

        :return: Number of texts available in the inventory
        """
        return len(self.texts)
