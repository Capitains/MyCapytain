# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.prototypes.metadata
   :synopsis: Definition of Metadata Type Objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""

from MyCapytain.common.metadata import Metadata
from MyCapytain.common.utils import Subgraph, LiteralToDict
from MyCapytain.common.constants import NAMESPACES, RDFLIB_MAPPING, Mimetypes, Exportable, GRAPH
from rdflib import URIRef, RDF, Literal, Graph, RDFS
from rdflib.namespace import SKOS


class Collection(Exportable):
    """ Collection represents any resource's metadata. It has members and parents

    :ivar properties: Properties of the collection
    :type properties: dict
    :ivar parents: Parent of the node from the direct parent to the highest ascendant
    :type parents: [Collection]
    :ivar metadata: Metadata
    :type metadata: Metadata
    """
    TYPE_URI = URIRef(NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.JSON.LD, Mimetypes.JSON.DTS.Std, Mimetypes.XML.RDF]

    def __init__(self, identifier="", *args, **kwargs):
        super(Collection, self).__init__(identifier, *args, **kwargs)
        self.__graph__ = GRAPH

        self.__node__ = URIRef(identifier)
        self.__metadata__ = Metadata.getOr(self.__node__, NAMESPACES.DTS.metadata)
        self.__capabilities__ = Metadata.getOr(self.__node__, NAMESPACES.DTS.capabilities)

        self.graph.set((self.asNode(), RDF.type, self.TYPE_URI))
        self.graph.set((self.asNode(), NAMESPACES.DTS.model, self.TYPE_URI))

        self.graph.addN(
            [
                (self.asNode(), NAMESPACES.DTS.capabilities, self.capabilities, self.graph),
                (self.asNode(), NAMESPACES.DTS.metadata, self.__metadata__, self.graph)
            ]
        )

        self.__parent__ = None
        self.__children__ = {}

    # Graph Related Properties
    @property
    def graph(self):
        """ RDFLib Graph space

        :rtype: Graph
        """
        return self.__graph__

    @property
    def metadata(self):
        return self.__metadata__

    @property
    def capabilities(self):
        return self.__capabilities__

    def asNode(self):
        """ Node representation of the collection in the graph

        :rtype: URIRef
        """
        return self.__node__

    @property
    def id(self):
        return str(self.asNode())

    def get_label(self, lang=None):
        """ Return label for given lang or any default

        :param lang: Language to request
        :return: Label value
        :rtype: Literal
        """
        x = None
        if lang is None:
            for obj in self.graph.objects(self.asNode(), RDFS.label):
                return obj
        for obj in self.graph.objects(self.asNode(), RDFS.label):
            x = obj
            if x.language == lang:
                return x
        return x

    def set_label(self, label, lang):
        """ Add the label of the collection in given lang

        :param label: Label Value
        :param lang:  Language code
        """
        self.graph.addN([
            (self.asNode(), RDFS.label, Literal(label, lang=lang), self.graph),
            (self.metadata, SKOS.prefLabel, Literal(label, lang=lang), self.graph),
        ])

    @property
    def children(self):
        """ Dictionary of childrens {Identifier: Collection}

        :rtype: dict
        """
        return self.__children__

    @property
    def parents(self):
        """ Iterator to find parents of current collection, from closest to furthest

        :rtype: Generator[:class:`Collection`]
        """
        p = self.parent
        parents = []
        while p is not None:
            parents.append(p)
            p = p.parent
        return parents

    @property
    def parent(self):
        """ Parent of current object

        :rtype: Collection
        """
        return self.__parent__

    @parent.setter
    def parent(self, parent):
        """ Parents

        :param parent: Parent to set for the object
        :type parent: Collection
        :return:
        """
        self.__parent__ = parent
        self.graph.set(
            (self.asNode(), NAMESPACES.DTS.parent, parent.asNode())
        )
        parent.__add_member__(self)

    def __add_member__(self, member):
        """ Does not add member if it already knows it.

        .. warning:: It should not be called !

        :param member: Collection to add to members
        """
        if member.id in self.children:
            return None
        else:
            self.children[member.id] = member
            #self.graph.add((self.asNode(), NAMESPACES.DTS.child, member.asNode()))

    def __getitem__(self, item):
        """ Retrieve an item by its ID in the tree of a collection

        :param item:
        :return: Collection identified by the item
        """
        for obj in self.descendants + [self]:
            if obj.id == item:
                return obj
        raise KeyError("%s is not part of this object" % item)

    @property
    def readable(self):
        """ Readable property should return elements where the element can be queried for getPassage / getReffs
        """
        return False

    @property
    def members(self):
        """ Children of the collection's item

        :rtype: [Collection]
        """
        return list(self.children.values())

    @property
    def descendants(self):
        """ Any descendant (no max level) of the collection's item

        :rtype: [Collection]
        """
        return self.members + \
            [submember for member in self.members for submember in member.descendants]

    @property
    def readableDescendants(self):
        """ List of element available which are readable

        :rtype: [Collection]
        """
        return [member for member in self.descendants if member.readable]

    def __namespaces_header__(self):
        """ Generates Namespaces Header given the graph

        :return: Dictionary with XMLNS prefix and uri as key and values
        """
        nm = self.graph.namespace_manager
        bindings = {}
        for predicate in set(self.graph.predicates()):
            prefix, namespace, name = nm.compute_qname(predicate)
            if prefix != "":
                bindings["xmlns:" + prefix] = str(URIRef(namespace))[:-1]
            else:
                bindings["xmlns"] = str(URIRef(namespace))[:-1]

        return bindings

    def __export__(self, output=None, domain=""):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :param domain: Domain (Necessary sometime to express some IDs)
        :type domain: str
        :return: Object using a different representation
        """

        if output == Mimetypes.JSON.DTS.Std:
            nm = self.graph.namespace_manager
            bindings = {}
            for predicate in set(self.graph.predicates()):
                prefix, namespace, name = nm.compute_qname(predicate)
                bindings[prefix] = str(URIRef(namespace))

            RDFSLabel = self.graph.qname(RDFS.label)
            store = Subgraph(GRAPH.namespace_manager)
            store.graphiter(self.graph, self.metadata, ascendants=0, descendants=1)
            metadata = {}
            for _, predicate, obj in store.graph:
                k = self.graph.qname(predicate)
                if k in metadata:
                    if isinstance(metadata[k], list):
                        metadata[k].append(LiteralToDict(obj))
                    else:
                        metadata[k] = [metadata[k], LiteralToDict(obj)]
                else:
                    metadata[k] = LiteralToDict(obj)
            o = {
                "@context": bindings,
                "@graph": {
                    "@id": self.id,
                    RDFSLabel: LiteralToDict(self.get_label()) or self.id,
                    self.graph.qname(NAMESPACES.DTS.size): len(self.members),
                    self.graph.qname(NAMESPACES.DTS.metadata): metadata
                }
            }
            if len(self.members):
                o["@graph"][self.graph.qname(NAMESPACES.DTS.members)] = [
                    {
                        "@id": member.id,
                        RDFSLabel: LiteralToDict(member.get_label()) or member.id,
                        self.graph.qname(NAMESPACES.DTS.url): domain+member.id
                    }
                    for member in self.members
                ]
            if self.parent:
                o["@graph"][self.graph.qname(NAMESPACES.DTS.parents)] = [
                    {
                        "@id": member.id,
                        RDFSLabel: LiteralToDict(member.get_label()) or member.id,
                        self.graph.qname(NAMESPACES.DTS.url): domain+member.id
                    }
                    for member in self.parents
                ]
            del store
            return o
        elif output == Mimetypes.JSON.LD\
                or output == Mimetypes.XML.RDF:

            # We create a temp graph
            store = Subgraph(GRAPH.namespace_manager)
            store.graphiter(self.graph, self.asNode(), ascendants=1, descendants=-1)

            o = store.serialize(format=RDFLIB_MAPPING[output], auto_compact=True, indent="")
            del store
            return o
