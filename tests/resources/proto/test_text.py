# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import text_type as str

import unittest

from MyCapytain.common.reference import URN, Citation

from MyCapytain.resources.prototypes.text import *
from MyCapytain.common.constants import RDF_NAMESPACES
import MyCapytain.common.reference
import MyCapytain.common.metadata


class TestProtoResource(unittest.TestCase):
    """ Test for resource, mother class of CtsTextMetadata and CapitainsCtsPassage """
    def test_init(self):
        a = CtsNode(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(a.id, "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(a.urn, URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2"))
        self.assertIsInstance(a.citation, Citation)


        a.resource = True
        self.assertEqual(a.resource, True)

    def test_urn(self):
        """ Test setters and getters for urn """
        a = CtsNode()
        # Should work with string
        a.urn = "urn:cts:latinLit:tg.wk.v" 
        self.assertEqual(isinstance(a.urn, MyCapytain.common.reference._capitains_cts.URN), True)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:tg.wk.v")

        # Test for URN
        a.urn = MyCapytain.common.reference._capitains_cts.URN("urn:cts:latinLit:tg.wk.v2")
        self.assertEqual(isinstance(a.urn, MyCapytain.common.reference._capitains_cts.URN), True)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:tg.wk.v2")

        # Test it fails if not basestring or URN
        with self.assertRaises(TypeError): 
            a.urn = 2

        # Test Resource setting works out as well
        b = CtsText(urn="urn:cts:latinLit:tg.wk.v")
        self.assertEqual(str(b.urn), "urn:cts:latinLit:tg.wk.v")


class TestProtoText(unittest.TestCase):
    """ Test the text prototype, mainly to ensure consistency """

    def test_init(self):
        """ Test init works correctly """
        a = CtsText("someId")

        #  Test with metadata
        a = CtsText("someId")
        self.assertIsInstance(a.metadata, MyCapytain.common.metadata.Metadata)

        m = MyCapytain.common.metadata.Metadata()
        m.add(RDF_NAMESPACES.CTS.title, "I am a metadata", "fre")
        a = CtsText(metadata=m)
        self.assertEqual(str(a.metadata.get_single(RDF_NAMESPACES.CTS.title, "fre")), "I am a metadata")

    def test_proto_reff(self):
        """ Test that getValidReff function are not implemented """
        a = CtsText()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError):
            a.getValidReff()

        # It takes two parameters, should not issue TypeError
        # Consistency check
        with self.assertRaises(NotImplementedError):
            a.getValidReff(level=1, reference=["1"])

    def test_proto_passage(self):
        """ Test that getPassage function are not implemented but are consistent"""
        a = CtsText()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError):
            a.getTextualNode(subreference=None)

    def test_get_label(self):
        """ Test that getLabel function are not implemented but are consistent"""
        a = CtsText()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError): 
            a.getLabel()

    def test_urn(self):
        """ Test setters and getters for urn """
        a = CtsText()
        # Should work with string
        a.urn = "urn:cts:latinLit:tg.wk.v" 
        self.assertEqual(isinstance(a.urn, MyCapytain.common.reference._capitains_cts.URN), True)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:tg.wk.v")

        # Test for URN
        a.urn = MyCapytain.common.reference._capitains_cts.URN("urn:cts:latinLit:tg.wk.v2")
        self.assertEqual(isinstance(a.urn, MyCapytain.common.reference._capitains_cts.URN), True)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:tg.wk.v2")

        # Test it fails if not basestring or URN
        with self.assertRaises(TypeError): 
            a.urn = 2

        # Test original setting works out as well
        b = CtsText(urn="urn:cts:latinLit:tg.wk.v")
        self.assertEqual(str(b.urn), "urn:cts:latinLit:tg.wk.v")

    def test_reffs(self):
        """ Test property reff, should fail because it supposes validReff is implemented """
        a = CtsText()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError):
            a.reffs

    def test_citation(self):
        """ Test citation property setter and getter """
        a = CtsText()
        a.citation = MyCapytain.common.reference._capitains_cts.Citation(name="label")
        self.assertIsInstance(a.citation, MyCapytain.common.reference._capitains_cts.Citation)

        #On init ?
        b = CtsText(citation=MyCapytain.common.reference._capitains_cts.Citation(name="label"))
        self.assertEqual(b.citation.name, "label")
