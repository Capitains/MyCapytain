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
from MyCapytain.errors import InvalidURN, UnknownCollection
from MyCapytain.resolvers.prototypes import Resolver
from collections import defaultdict

from rdflib import RDF, Literal, URIRef
from rdflib.namespace import DC
from typing import List, Dict, Set

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
    TYPE_URI = RDF_NAMESPACES.CAPITAINS.term("collection")
    COLLECTION_ATTRIBUTES = ['path', 'readable']

    def __init__(self, identifier: str='', resolver: Resolver=None):
        super(PrototypeCapitainsCollection, self).__init__(identifier, resolver)

        self._id = str(identifier)
        self._subtype = set()
        self._parent = list()

    @property
    def urn(self):
        return self._id

    @property
    def id(self):
        return self._id

    @property
    def subtype(self) -> Set[str]:
        """ Subtypes of the object

        :return: string representation of subtype
        """
        return self._subtype

    @subtype.setter
    def subtype(self, val: str):
        """ Set the subtype of the object

        :param val: the object's subtype
        """
        if isinstance(val, str):
            self._subtype.add(val)
        else:
            self._subtype.add(str(val))

    @property
    def children(self) -> Dict[str, 'PrototypeCapitainsCollection']:
        """ Dictionary of childrens {Identifier: Collection}

        """
        return {x: self._resolver.id_to_coll[x] for x in self._resolver.children[self.id]}

    @property
    def parent(self):
        """ Parent of current object

        :rtype: [Collection]
        """
        return self._resolver.parents[self.id]

    @parent.setter
    def parent(self, parent):
        """ Parents

        :param parent: Parent to set for the object
        :type parent: Collection
        :return:
        """
        self.metadata.add(RDF_NAMESPACES.CAPITAINS.parent, URIRef(parent.id))
        self._resolver.add_parent(self.id, parent.id)

    @property
    def ancestors(self) -> Dict[str, 'Collection']:
        """ Iterator to find parents of current collection, from closest to furthest

        :rtype: Generator[:class:`Collection`]
        """
        ancestors = set()
        parents = self.parent
        ancestors.update(parents)
        while parents:
            new_p = set()
            for parent in parents:
                parent_coll = self._resolver.id_to_coll[parent]
                ancestors.update(parent_coll.parent)
                new_p.update(parent_coll.parent)
            parents = new_p
        return {x: self._resolver.id_to_coll[x] for x in ancestors}

    @property
    def descendants(self) -> Dict[str, 'Collection']:
        """ Any descendant (no max level) of the collection's item

        :rtype: [Collection]
        """
        descendants = set()
        children = self.children
        descendants.update(children)
        while children:
            new_c = set()
            for child in children:
                child_coll = self._resolver.id_to_coll[child]
                descendants.update(child_coll.children)
                new_c.update(child_coll.children)
            children = new_c
        return {x: self._resolver.id_to_coll[x] for x in descendants}

    @property
    def readableDescendants(self) -> Dict[str, 'CapitainsReadableMetadata']:
        """ List of element available which are readable

        :rtype: [Collection]
        """
        return {k: v for k, v in self.descendants.items() if v.readable}

    @property
    def texts(self) -> Dict[str, 'CapitainsReadableMetadata']:
        """ Texts

        :return: Readable descendants
        :rtype: {str: CapitainsReadableMetadata}
        """
        return self.readableDescendants

    def get_label(self, lang=None):
        """ Return label for given lang or any default

        :param lang: Language to request
        :return: Label value
        :rtype: Literal
        """
        x = None
        for obj in self.graph.objects(self.asNode(), DC.title):
            if obj.language == lang:
                return obj
        for obj in self.graph.objects(self.asNode(), DC.title):
            return obj
        return x

    def set_label(self, label, lang):
        return NotImplementedError('Use obj.metadata.add(DC.title, {}, {}) to add a title to collection'.format(label,
                                                                                                                lang))

    def __getitem__(self, key):
        """ Retrieve an item by its ID in the tree of a collection

        :param key: Key of the object to delete
        :return: Collection identified by the item
        """
        if key == self.id:
            return self
        if key in self.members or key in self.descendants:
            return self._resolver.id_to_coll[key]
        raise UnknownCollection("%s is not part of this object" % key)

    def __contains__(self, item):
        """ Retrieve an item by its ID in the tree of a collection

        :param item:
        :return: Collection identified by the item
        """
        if item == self.id or item in self.descendants:
            return True
        return False

    def __eq__(self, other):
        if self is other:
            return True
        elif not isinstance(other, self.__class__):
            return False
        return hasattr(self, "id") and hasattr(other, "id") and self.id == other.id

    def get_property(self, namespace, name, lang=None):
        """ Get given property in CAPITAINS Namespace

        .. example::
            collection.get_capitains_property("groupname", "eng")

        :param name: Property to get (Without namespace)
        :param lang: Language to get for given value
        :return: Value or default if lang is set, else whole set of values
        :rtype: dict([Literal]) or [Literal]
        """
        x = defaultdict(list)
        for obj in self.metadata.get(namespace.term(name)):
            x[getattr(obj, 'language', "")].append(obj)
        if lang is not None:
            if lang in x:
                return x[lang]
            return next(iter(x.values()))
        return x

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

    def __init__(self, urn: str="", parent: 'CapitainsCollectionMetadata'=None, lang: str=None, resolver: Resolver=None):
        super(CapitainsReadableMetadata, self).__init__(identifier=str(urn), resolver=resolver)
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
        return dict()

    @property
    def descendants(self):
        """ Descendants of the collection's item

        .. warning:: CapitainsCtsText has no Descendants

        :rtype: list
        """
        return dict()

    @property
    def readable_siblings(self):
        """ Get all readable siblings of the text

        :return: List of readable siblings
        :rtype: [CapitainsTextMetadata]
        """
        sibs = dict()
        for parent in self.parent:
            sibs.update({k: v for k, v in self._resolver.id_to_coll[parent].readableDescendants.items()})
        sibs.pop(self.id, None)
        return list(sibs.values())

    def get_title(self, lang=None):
        """ Get the DC Title of the object

        :param lang: Lang to retrieve
        :return: Title string representation
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
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.XML.GUIDELINES3]
    CAPITAINS_PROPERTIES = [RDF_NAMESPACES.CAPITAINS.title]

    def __init__(self, urn: str=None, parent: 'CapitainsCollectionMetadata'=None, resolver: Resolver=None):
        super(CapitainsCollectionMetadata, self).__init__(identifier=str(urn), resolver=resolver)

        if parent is not None:
            self.parent = parent

    @property
    def collections(self):
        """ The sub-collections in this collection

        :return: List of sub-collections
        :rtype: {str: CapitainsCollectionMetadata}
        """
        return {k: v for k, v in self.children.items() if v.readable is False}

    @property
    def lang(self):
        """ Languages this text is in

        :return: List of available languages
        """
        return None

    def update(self, other: 'CapitainsCollectionMetadata') -> 'CapitainsCollectionMetadata':
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
        self_descendants = {k: v for k, v in self.descendants.items()}
        # The sorting here is to make sure that the new descendants that are added to self will be processed first.
        # This is so that a descendant in other that is also in self but has a different parent in other will have its parent attribute correctly expanded.
        for desc_id, other_descendant in sorted(other.descendants.items(), key=lambda x: x[0] in self_descendants.keys()):
            if desc_id in self_descendants.keys():
                if other_descendant.readable is False:
                    self._resolver.id_to_coll[desc_id].update(other_descendant)
                for parent in other_descendant.parent.union(self_descendants[desc_id].parent):
                    self._resolver.id_to_coll[desc_id].parent = self._resolver.id_to_coll[parent]
            else:
                new_parents = []
                for parent in other_descendant.parent:
                    if parent in self._resolver.id_to_coll:
                        parent_coll = self._resolver.id_to_coll[parent]
                        # parent_coll.update(other._resolver.id_to_coll[parent])
                    else:
                        parent_coll = other._resolver.id_to_coll[parent]
                    new_parents.append(parent_coll)
                other_descendant._parent = []
                for parent in new_parents:
                    other_descendant.parent = parent

        return self

    def __len__(self):
        """ Get the number of text in the CtsWorkMetadata

        :return: Number of texts available in the inventory
        """
        return len(self.texts)
