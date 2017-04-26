# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.metadata
   :synopsis: Metadata related objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals
from MyCapytain.common.utils import make_xml_node
from MyCapytain.common.constants import Mimetypes, get_graph
from MyCapytain.common.base import Exportable
from rdflib import BNode, Literal, Graph, URIRef, term


class Metadata(Exportable):
    """ A metadatum aggregation object provided to centralize metadata

    :param keys: A metadata field names list
    :type keys: [text_type]

    :cvar EXPORT_TO: List of exportable supported formats
    :cvar DEFAULT_EXPORT: Default export (CTS XML Inventory)
    :cvar STORE: RDF Store
    """
    EXPORT_TO = [Mimetypes.JSON.Std, Mimetypes.XML.RDF, Mimetypes.XML.RDFa, Mimetypes.JSON.LD, Mimetypes.XML.CapiTainS.CTS]
    DEFAULT_EXPORT = Mimetypes.JSON.Std
    
    def __init__(self, node=None, *args, **kwargs):
        super(Metadata, self).__init__(*args, **kwargs)
        self.__graph__ = get_graph()
        if node is not None:
            self.__node__ = node
        else:
            self.__node__ = BNode()

    def asNode(self):
        return self.__node__

    @property
    def graph(self):
        """ Quick access to the graph this node is connected to

        :rtype: Graph
        """
        return self.__graph__

    def add(self, key, value, lang=None):
        """ Add a triple to the graph related to this node

        :param key: Predicate of the triple
        :param value: Object of the triple
        :param lang: Language of the triple if applicable
        """
        if not isinstance(value, Literal) and lang is not None:
            value = Literal(value, lang=lang)
        elif not isinstance(value, (BNode, URIRef)):
            value, _type = term._castPythonToLiteral(value)
            if _type is None:
                value = Literal(value)
            else:
                value = Literal(value, datatype=_type)
        self.graph.add((self.asNode(), key, value))

    def get(self, key, lang=None):
        """ Returns triple related to this node. Can filter on lang

        :param key: Predicate of the triple
        :param lang: Language of the triple if applicable
        :rtype: Literal or BNode or URIRef
        """
        if lang is not None:
            for o in self.graph.objects(self.asNode(), key):
                if o.language == lang:
                    yield o
        else:
            for o in self.graph.objects(self.asNode(), key):
                yield o

    def get_single(self, key, lang=None):
        """ Returns a single triple related to this node.

        :param key: Predicate of the triple
        :param lang: Language of the triple if applicable
        :rtype: Literal or BNode or URIRef
        """
        if lang is not None:
            default = None
            for o in self.graph.objects(self.asNode(), key):
                default = o
                if o.language == lang:
                    return o
            return default
        else:
            for o in self.graph.objects(self.asNode(), key):
                return o

    def __getitem__(self, item):
        """ Quick access method. If

        :param item: Identifier
        :return: List or Literal or BNode or URIRef

        .. example::
            Metadata[Title, lang] == Metadata.get(Title, lang=lang)
            Metadata[Title] == [Metadata.get(Title, lang=lang1), Metadata.get(Title, lang=lang2)]
        """
        if isinstance(item, tuple):
            return self.get_single(item[0], item[1])
        return list(self.get(item))

    def remove(self, predicate=None, obj=None):
        """ Remove triple matching the predicate or the object

        :param predicate: Predicate to match, None to match all
        :param obj: Object to match, None to match all
        """
        self.graph.remove((self.asNode(), predicate, obj))

    def unlink(self, subj=None, predicate=None):
        """ Remove triple where Metadata is the object

        :param subj: Subject to match, None to match all
        :param predicate: Predicate to match, None to match all
        """
        self.graph.remove((subj, predicate, self.asNode()))

    def predicate_object(self, predicate=None, obj=None):
        """ Retrieve predicate and object around this object

        :param predicate: Predicate to match, None to match all
        :param obj: Object to match, None to match all

        :return: List of resources
        """
    def __export__(self, output=Mimetypes.JSON.Std, only=None, exclude=None, **kwargs):
        """ Export a set of Metadata

        :param output: Mimetype to export to
        :param only: Includes only term from given namespaces
        :param exclude: Includes only term from given namespaces
        :return: Formatted Export

        .. warning:: exclude and warning cannot be used together
        """
        graph = Graph()
        graph.namespace_manager = get_graph().namespace_manager

        if only is not None:
            _only = only
            only = [str(s) for s in only]
            for predicate in set(self.graph.predicates(subject=self.asNode())):
                if str(predicate) not in only:
                    prefix, namespace, name = self.graph.compute_qname(predicate)
                    if str(namespace) in only:
                        _only.append(predicate)
            for predicate, obj in self.graph[self.asNode()]:
                if predicate in _only:
                    graph.add((self.asNode(), predicate, obj))
        elif exclude is not None:
            _only = []
            exclude = [str(s) for s in exclude]
            for predicate in set(self.graph.predicates(subject=self.asNode())):
                prefix, namespace, name = self.graph.compute_qname(predicate)
                if str(predicate) not in exclude and not str(namespace) in exclude:
                    _only.append(predicate)
            for predicate, obj in self.graph[self.asNode()]:
                if predicate in _only:
                    graph.add((self.asNode(), predicate, obj))
        else:
            for predicate, object in self.graph[self.asNode()]:
                graph.add((self.asNode(), predicate, object))

        if output == Mimetypes.JSON.Std:
            out = {}
            for _, predicate, object in graph:
                predicate = str(predicate)
                if predicate not in out:
                    out[predicate] = {}
                if isinstance(object, Literal):
                    out[predicate][object.language] = object.title()
            del graph
            return out

        elif output == Mimetypes.JSON.LD:
            out = graph.serialize(format="json-ld", context={})
            del graph
            return out

        elif output == Mimetypes.XML.RDF:
            out = graph.serialize(format="xml")
            del graph
            return out

        elif output == Mimetypes.XML.CapiTainS.CTS:
            strings = []
            for pred, obj in graph.predicate_objects(self.asNode()):
                kwargs = {}
                if hasattr(obj, "language") and obj.language is not None:
                    kwargs["xml:lang"] = obj.language
                if hasattr(obj, "datatype") and obj.datatype is not None:
                    kwargs["rdf:type"] = obj.datatype
                strings.append(make_xml_node(graph, pred, text=obj, attributes=kwargs, complete=True))
            del graph
            return "\n".join(strings)

    @staticmethod
    def getOr(subject, predicate, *args, **kwargs):
        """ Retrieve a metadata node or generate a new one

        :param subject: Subject to which the metadata node should be connected
        :param predicate: Predicate by which the metadata node should be connected
        :return: Metadata for given node
        :rtype: Metadata

        """
        if (subject, predicate, None) in get_graph():
            return Metadata(node=get_graph().objects(subject, predicate).__next__())
        return Metadata(*args, **kwargs)
