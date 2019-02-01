# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.prototypes.metadata
   :synopsis: Definition of Metadata Type Objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>

"""

from MyCapytain.common.metadata import Metadata
from MyCapytain.errors import UnknownCollection
from MyCapytain.common.utils import literal_to_dict, Subgraph
from MyCapytain.common.constants import RDF_NAMESPACES, RDFLIB_MAPPING, Mimetypes, get_graph
from MyCapytain.common.base import Exportable
from MyCapytain.common.reference import BaseCitationSet
from rdflib import URIRef, RDF, Literal, Graph, RDFS
from rdflib.namespace import SKOS, DC, DCTERMS
from typing import List


__all__ = [
    "Collection",
    "ResourceCollection"
]


_ns_hydra_str = str(RDF_NAMESPACES.HYDRA)
_ns_cts_str = str(RDF_NAMESPACES.CTS)
_ns_dts_str = str(RDF_NAMESPACES.DTS)
_ns_dct_str = str(DCTERMS)
_ns_cap_str = str(RDF_NAMESPACES.CAPITAINS)
_ns_rdf_str = str(RDF)
_ns_rdfs_str = str(RDFS)


class Collection(Exportable):
    """ Collection represents any resource's metadata. It has members and parents

    :ivar properties: Properties of the collection
    :type properties: dict
    :ivar parents: Parent of the node from the direct parent to the highest ascendant
    :type parents: [Collection]
    :ivar metadata: Metadata
    :type metadata: Metadata
    """
    TYPE_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    MODEL_URI = URIRef(RDF_NAMESPACES.DTS.collection)
    EXPORT_TO = [Mimetypes.JSON.LD, Mimetypes.JSON.DTS.Std, Mimetypes.XML.RDF]

    def __init__(self, identifier="", *args, **kwargs):
        super(Collection, self).__init__(identifier, *args, **kwargs)
        self._graph = get_graph()

        self._node = URIRef(identifier)
        self._metadata = Metadata(node=self.asNode())

        self.graph.set((self.asNode(), RDF.type, self.TYPE_URI))
        self.graph.set((self.asNode(), RDF_NAMESPACES.DTS.model, self.MODEL_URI))

        self._parent = None
        self._children = {}

    def __repr__(self):
        return "%s(%s)#%s" % (self.__class__.__name__, self.id, id(self))

    @property
    def version(self):
        for x in self.graph.objects(self.asNode(), RDF_NAMESPACES.DTS.version):
            return x

    @version.setter
    def version(self, value):
        if not isinstance(value, Literal):
            value = Literal(value)
        self.graph.set((self.asNode(), RDF_NAMESPACES.DTS.version, value))

    @property
    def type(self):
        return list(self.graph.objects(self.asNode(), RDF.type))[0]

    @type.setter
    def type(self, value):
        if not isinstance(value, URIRef):
            value = URIRef(value)
        self.graph.set((self.asNode(), RDF.type, value))

    @property
    def model(self):
        return list(self.graph.objects(self.asNode(), RDF_NAMESPACES.DTS.model))[0]

    @model.setter
    def model(self, value):
        if not isinstance(value, URIRef):
            value = URIRef(value)
        self.graph.set((self.asNode(), RDF_NAMESPACES.DTS.model, value))

    @property
    def size(self):
        return len(self.members)

    # Graph Related Properties
    @property
    def graph(self):
        """ RDFLib Graph space

        :rtype: Graph
        """
        return self._graph

    @property
    def metadata(self):
        return self._metadata

    def asNode(self):
        """ Node representation of the collection in the graph

        :rtype: URIRef
        """
        return self._node

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
        self.metadata.add(SKOS.prefLabel, Literal(label, lang=lang))
        self.graph.addN([
            (self.asNode(), RDFS.label, Literal(label, lang=lang), self.graph),
        ])

    @property
    def children(self) -> dict:
        """ Dictionary of childrens {Identifier: Collection}

        :rtype: dict
        """
        return self._children

    @property
    def parents(self) -> List["Collection"]:
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
        return self._parent

    @parent.setter
    def parent(self, parent):
        """ Parents

        :param parent: Parent to set for the object
        :type parent: Collection
        :return:
        """
        self._parent = parent
        self.graph.add(
            (self.asNode(), RDF_NAMESPACES.CAPITAINS.parent, parent.asNode())
        )
        parent._add_member(self)

    def _add_member(self, member):
        """ Does not add member if it already knows it.

        .. warning:: It should not be called !

        :param member: Collection to add to members
        """
        if member.id in self.children:
            return None
        else:
            self.children[member.id] = member
            #self.graph.add((self.asNode(), RDF_NAMESPACES.DTS.child, member.asNode()))

    def __getitem__(self, key):
        """ Retrieve an item by its ID in the tree of a collection

        :param key: Key of the object to delete
        :return: Collection identified by the item
        """
        if key == self.id:
            return self
        for obj in self.members:
            if key == obj.id:
                return obj
        for obj in self.descendants:
            if obj.id == key:
                return obj
        raise UnknownCollection("%s is not part of this object" % key)

    def __delitem__(self, key):
        """ Delete a children of the collection

        :param key: Key of the object to delete
        """
        item = self[key]
        # Delete the graph Item
        self.graph.remove((item.asNode(), None, None))
        self.graph.remove((None, None, item.asNode()))
        self.metadata.remove()
        self.metadata.unlink()
        # Delete the Python item
        if len(item.parents) > 0:
            del item.parents[0].children[item.id]

    def __contains__(self, item):
        """ Retrieve an item by its ID in the tree of a collection

        :param item:
        :return: Collection identified by the item
        """
        for obj in self.descendants + [self]:
            if obj.id == item:
                return True
        return False

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

    def __namespaces_header__(self, cpt=None):
        """ Generates Namespaces Header given the graph

        :return: Dictionary with XMLNS prefix and uri as key and values
        """
        nm = self.graph.namespace_manager
        bindings = {}
        for predicate in set(self.graph.predicates()):
            prefix, namespace, name = nm.compute_qname(predicate)
            if prefix != "":
                bindings["xmlns:" + prefix] = str(URIRef(namespace))#[:-1]
            else:
                bindings["xmlns"] = str(URIRef(namespace))#[:-1]
        if cpt is True:
            bindings["xmlns:cpt"] = str(RDF_NAMESPACES.CAPITAINS)

        # Small hard coded fix for namespace that were not thought for RDF
        for k, v in bindings.items():
            if v in ["http://chs.harvard.edu/xmlns/cts/"]:
                bindings[k] = v[:-1]

        return bindings

    @classmethod
    def export_base_dts(cls, graph, obj, nsm):
        """ Export the base DTS information in a simple reusable way

        :param graph: Current graph where the information lie
        :param obj: Object for which we build info
        :param nsm: Namespace manager
        :return: Dict
        """

        o = {
            "@id": str(obj.asNode()),
            "@type": nsm.qname(obj.type),
            nsm.qname(RDF_NAMESPACES.HYDRA.title): str(obj.get_label()),
            nsm.qname(RDF_NAMESPACES.HYDRA.totalItems): obj.size
        }

        for desc in graph.objects(obj.asNode(), RDF_NAMESPACES.HYDRA.description):
            o[nsm.qname(RDF_NAMESPACES.HYDRA.description)] = str(desc)

        return o

    def __export__(self, output=None, namespace_manager=None):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """

        if output == Mimetypes.JSON.DTS.Std:

            # Set-up a derived Namespace Manager
            if not namespace_manager:
                nsm = {
                    prefix: ns
                    for prefix, ns in self.graph.namespace_manager.namespaces()
                    if str(ns) not in [_ns_cap_str, _ns_cts_str, _ns_dts_str, _ns_dct_str, _ns_hydra_str]
                }
                nsm[""] = RDF_NAMESPACES.HYDRA
                nsm["cts"] = RDF_NAMESPACES.CTS
                nsm["dts"] = RDF_NAMESPACES.DTS
                nsm["dct"] = DCTERMS

            else:
                nsm = namespace_manager.namespaces()

            # Set-up a derived graph
            store = Subgraph(nsm)
            store.graphiter(self.graph, self.asNode(), ascendants=0, descendants=1)
            graph = store.graph
            nsm = store.graph.namespace_manager

            # Build the JSON-LD @context

            ignore_ns_for_bindings = [_ns_cap_str, _ns_hydra_str, _ns_rdf_str, _ns_rdfs_str]
            bindings = {}
            for predicate in set(graph.predicates()):
                prefix, namespace, name = nsm.compute_qname(predicate)
                if prefix not in bindings and str(namespace) not in ignore_ns_for_bindings:
                    bindings[prefix] = str(URIRef(namespace))

            # Builds the specific Store data
            extensions = {}
            dublincore = {}
            ignore_ns = [_ns_cap_str, _ns_hydra_str, _ns_rdf_str, _ns_rdfs_str, _ns_dts_str]

            # Builds the .dublincore and .extensions graphs
            for _, predicate, obj in store.graph:
                k = graph.qname(predicate)
                prefix, namespace, name = nsm.compute_qname(predicate)
                namespace = str(namespace)

                # Ignore namespaces that are part of the root DTS object
                if namespace in ignore_ns:
                    continue

                # Switch to the correct container depending on namespaces
                if namespace == str(DCTERMS):
                    metadata = dublincore
                else:
                    metadata = extensions

                if k in metadata:
                    if isinstance(metadata[k], list):
                        metadata[k].append(literal_to_dict(obj))
                    else:
                        metadata[k] = [metadata[k], literal_to_dict(obj)]
                else:
                    metadata[k] = literal_to_dict(obj)
                    if isinstance(metadata[k], dict):
                        metadata[k] = [metadata[k]]

            o = {"@context": bindings}
            o.update(self.export_base_dts(graph, self, nsm))
            o["@context"]["@vocab"] = _ns_hydra_str

            if extensions:
                o[graph.qname(RDF_NAMESPACES.DTS.extensions)] = extensions

            if dublincore:
                o[graph.qname(RDF_NAMESPACES.DTS.dublincore)] = dublincore

            if self.size:
                o[graph.qname(RDF_NAMESPACES.HYDRA.member)] = [
                    self.export_base_dts(self.graph, member, nsm)
                    for member in self.members
                ]

            # If the system handles citation structure
            if hasattr(self, "citation") and \
                    isinstance(self.citation, BaseCitationSet):
                if self.citation.depth:
                    o[graph.qname(RDF_NAMESPACES.DTS.term("citeDepth"))] = self.citation.depth

                if not self.citation.is_empty():
                    o[graph.qname(RDF_NAMESPACES.DTS.term("citeStructure"))] = self.citation.export(
                        Mimetypes.JSON.DTS.Std,
                        context=False,
                        namespace_manager=nsm
                    )

            del store
            return o
        elif output == Mimetypes.JSON.LD\
                or output == Mimetypes.XML.RDF:

            # We create a temp graph
            store = Subgraph(get_graph().namespace_manager)
            store.graphiter(self.graph, self.asNode(), ascendants=1, descendants=-1)

            o = store.serialize(format=RDFLIB_MAPPING[output], auto_compact=True, indent="")
            del store
            return o


class ResourceCollection(Collection):
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

    def get_creator(self, lang=None):
        """ Get the DC Creator literal value

        :param lang: Language to retrieve
        :return: Creator string representation
        :rtype: Literal
        """
        return self.metadata.get_single(key=DC.creator, lang=lang)

    def get_title(self, lang=None):
        """ Get the title of the object

        :param lang: Lang to retrieve
        :return: Title string representation
        :rtype: Literal
        """
        return self.metadata.get_single(key=DC.title, lang=lang)

    def get_description(self, lang=None):
        """ Get the description of the object

        :param lang: Lang to retrieve
        :return: Description string representation
        :rtype: Literal
        """
        return self.metadata.get_single(key=DC.description, lang=lang)

    def get_subject(self, lang=None):
        """ Get the subject of the object

        :param lang: Lang to retrieve
        :return: Subject string representation
        :rtype: Literal
        """
        return self.metadata.get_single(key=DC.subject, lang=lang)
