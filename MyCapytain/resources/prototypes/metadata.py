# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.prototypes.metadata
   :synopsis: Definition of Metadata Type Objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""

from MyCapytain.common.metadata import Metadata
from MyCapytain.common.constants import NAMESPACES, RDFLIB_MAPPING, Mimetypes, Exportable, GRAPH
from rdflib import URIRef, RDF, Literal, Graph, BNode, RDFS
from rdflib.namespace import SKOS, DC


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

    def label(self, lang=None):
        return self.graph.label(self.asNode(), lang)

    def set_label(self, label, lang):
        self.graph.addN([
            (self.asNode(), RDFS.label, Literal(label, lang=lang), self.graph),
            (self.metadata, SKOS.prefLabel, Literal(label, lang=lang), self.graph),
        ])

    def __init__(self, identifier="", *args, **kwargs):
        super(Collection, self).__init__(identifier, *args, **kwargs)
        self.__graph__ = GRAPH

        self.__node__ = URIRef(identifier)
        self.__metadata__ = Metadata.getOr(self.__node__, NAMESPACES.DTS.metadata)
        self.__capabilities__ = Metadata.getOr(self.__node__, NAMESPACES.DTS.capabilities)
        self.__parentsNode__ = Metadata.getOr(self.__node__, NAMESPACES.DTS.parents)

        self.graph.set((self.asNode(), RDF.type, self.TYPE_URI))
        self.graph.set((self.asNode(), NAMESPACES.DTS.model, self.TYPE_URI))

        self.graph.addN(
            [
                (self.asNode(), NAMESPACES.DTS.capabilities, self.capabilities, self.graph),
                (self.asNode(), NAMESPACES.DTS.metadata, self.__metadata__, self.graph),
                (self.asNode(), NAMESPACES.DTS.parents, self.__parentsNode__, self.graph)
            ]
        )

        self.parents = []

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
        return []

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

    def refresh(self):
        """ Updates current Collection with subproperties

        :return:
        """
        # We update parents properties
        self.graph.remove((self.asNode(), NAMESPACES.DTS.parents, None))
        for parent in self.parents:
            self.graph.add((self.asNode(), NAMESPACES.DTS.parents, parent.asNode()))

    def __export__(self, output=None, domain=""):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :param domain: Domain (Necessary sometime to express some IDs)
        :type domain: str
        :return: Object using a different representation
        """

        if output == Mimetypes.JSON.DTS.Std \
                or output == Mimetypes.JSON.LD\
                or output == Mimetypes.XML.RDF:
            self.refresh()
            # We create a temp graph
            graph = Graph()
            graph.namespace_manager = GRAPH.namespace_manager
            for predicate, object in self.graph[self.asNode()]:
                graph.add((self.asNode(), predicate, object))
                for p2, o2 in self.graph[object]:
                    graph.add((object, p2, o2))

            o = graph.serialize(format=RDFLIB_MAPPING[output], auto_compact=True)
            del graph
            return o
