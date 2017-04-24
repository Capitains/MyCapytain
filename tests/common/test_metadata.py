# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from MyCapytain.common.metadata import Metadata
from MyCapytain.common.constants import RDF_NAMESPACES, Mimetypes
from unittest import TestCase
from operator import attrgetter

import rdflib


class TestMetadata(TestCase):
    def test_add_value(self):
        m = Metadata()
        m.add(RDF_NAMESPACES.CTS.title, "Title")
        self.assertEqual(
            m.get_single(RDF_NAMESPACES.CTS.title),
            rdflib.term.Literal('Title')
        )

        m.add(RDF_NAMESPACES.CTS.number, 5)
        self.assertEqual(
            m.get_single(RDF_NAMESPACES.CTS.number),
            rdflib.term.Literal('5', datatype=rdflib.term._XSD_INTEGER)
        )

        m.add(RDF_NAMESPACES.CTS.description, "Titre", "fre")
        self.assertEqual(
            m.get_single(RDF_NAMESPACES.CTS.description, "fre"),
            rdflib.term.Literal('Titre', 'fre')
        )
        self.assertIn(
            m.get_single(RDF_NAMESPACES.CTS.description, "eng"),
            [rdflib.term.Literal('Titre', 'fre'), rdflib.term.Literal('Titre')]
        )

    def test_get(self):
        m = Metadata()
        m.add(RDF_NAMESPACES.CTS.title, "Title")
        m.add(RDF_NAMESPACES.CTS.title, "Title", lang="eng")
        m.add(RDF_NAMESPACES.CTS.title, "SubTitle", lang="eng")
        self.assertCountEqual(
            list(m.get(RDF_NAMESPACES.CTS.title)),
            [
                rdflib.term.Literal('Title'),
                rdflib.term.Literal('Title', lang="eng"),
                rdflib.term.Literal('SubTitle', lang="eng")
            ]
        )
        self.assertCountEqual(
            list(m.get(RDF_NAMESPACES.CTS.title, lang="eng")),
            [
                rdflib.term.Literal('Title', lang="eng"),
                rdflib.term.Literal('SubTitle', lang="eng")
            ]
        )

    def test_get_item(self):
        m = Metadata()
        m.add(RDF_NAMESPACES.CTS.title, "Title")
        m.add(RDF_NAMESPACES.CTS.title, "Title", lang="eng")
        m.add(RDF_NAMESPACES.CTS.title, "SubTitle", lang="eng")
        self.assertCountEqual(
            m[RDF_NAMESPACES.CTS.title],
            [
                rdflib.term.Literal('Title'),
                rdflib.term.Literal('Title', lang="eng"),
                rdflib.term.Literal('SubTitle', lang="eng")
            ]
        )
        self.assertIn(
            m[RDF_NAMESPACES.CTS.title, "eng"],
            [
                rdflib.term.Literal('Title', lang="eng"),
                rdflib.term.Literal('SubTitle', lang="eng")
            ]
        )

    def test_remove_unlink(self):
        m = Metadata()
        b = rdflib.BNode()
        m.add(RDF_NAMESPACES.CTS.title, "Title")
        m.add(RDF_NAMESPACES.CTS.title, "Title", lang="eng")
        m.add(RDF_NAMESPACES.CTS.title, "SubTitle", lang="eng")
        m.add(RDF_NAMESPACES.CTS.description, "SubTitle", lang="eng")
        m.add(RDF_NAMESPACES.CTS.description, "SubTitle", lang="fre")
        m.graph.add((b, RDF_NAMESPACES.TEI.nobodycares, m.asNode()))

        self.assertCountEqual(
            m[RDF_NAMESPACES.CTS.title],
            [
                rdflib.term.Literal('Title'),
                rdflib.term.Literal('Title', lang="eng"),
                rdflib.term.Literal('SubTitle', lang="eng")
            ]
        )
        m.remove(RDF_NAMESPACES.CTS.title)
        self.assertEqual(m[RDF_NAMESPACES.CTS.title], [])
        self.assertCountEqual(m[RDF_NAMESPACES.CTS.description], [
                rdflib.term.Literal('SubTitle', lang="fre"),
                rdflib.term.Literal('SubTitle', lang="eng")
        ])
        self.assertEqual(
            list(m.graph.subject_predicates(m.asNode())),
            [(b, RDF_NAMESPACES.TEI.nobodycares)]
        )
        m.unlink()
        self.assertEqual(
            list(m.graph.subject_predicates(m.asNode())),
            []
        )