# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.metadata
   :synopsis: Metadata related objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals
from MyCapytain.common.constants import Mimetypes, Exportable, GRAPH
from rdflib import BNode, Literal, Graph


class Metadata(BNode, Exportable):
    """ A metadatum aggregation object provided to centralize metadata

    :param keys: A metadata field names list
    :type keys: [text_type]

    :cvar EXPORT_TO: List of exportable supported formats
    :cvar DEFAULT_EXPORT: Default export (CTS XML Inventory)
    :cvar STORE: RDF Store
    """
    EXPORT_TO = [Mimetypes.JSON.Std, Mimetypes.XML.RDF, Mimetypes.XML.RDFa, Mimetypes.JSON.LD]
    DEFAULT_EXPORT = Mimetypes.JSON.Std
    
    def __init__(self, *args, **kwargs):
        super(Metadata, self).__init__(*args, **kwargs)
        self.__graph__ = GRAPH

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
        if not isinstance(value, Literal):
            value = Literal(value, lang=lang)
        self.graph.add((self, key, value))

    def get(self, key, lang=None):
        """ Returns a triple related to this node

        :param key: Predicate of the triple
        :param lang: Language of the triple if applicable
        :rtype: Literal or BNode or URIRef
        """
        if lang is not None:
            default = None
            for o in self.graph.objects(self, key):
                default = o
                if o.language == lang:
                    return o
            return default
        else:
            for o in self.graph.objects(self, key):
                return o

    def get_all(self, key):
        """ Returns a triple related to this node

        :param key: Predicate of the triple
        :rtype: List of [Literal or BNode or URIRef]
        """
        for o in self.graph.objects(self, key):
            yield o

    def __getitem__(self, item):
        """ Quick access method. If

        :param item: Identifier
        :return: List or Literal or BNode or URIRef

        .. example::
            Metadata[Title, lang] == Metadata.get(Title, lang=lang)
            Metadata[Title] == [Metadata.get(Title, lang=lang1), Metadata.get(Title, lang=lang2)]
        """
        if isinstance(item, tuple):
            return self.get(item[0], item[1])
        return list(self.graph[self:item])

    def __export__(self, output=Mimetypes.JSON.Std, **kwargs):
        """ Export a set of Metadata

        :param output: Mimetype to export to
        :return: Formatted Export
        """
        graph = Graph()
        graph.namespace_manager = GRAPH.namespace_manager
        for predicate, object in self.graph[self]:
            graph.add((self, predicate, object))

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

    @staticmethod
    def getOr(subject, predicate, *args, **kwargs):
        """ Retrieve a metadata node or generate a new one

        :param subject: Subject to which the metadata node should be connected
        :param predicate: Predicate by which the metadata node should be connected
        :return: Metadata for given node
        :rtype: Metadata

        """
        if (subject, predicate, None) in GRAPH:
            return GRAPH.objects(subject, predicate).__next__()
        return Metadata(*args, **kwargs)
