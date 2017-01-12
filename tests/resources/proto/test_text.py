# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import text_type as str

import unittest

from MyCapytain.resources.prototypes.text import *
import MyCapytain.common.reference
import MyCapytain.common.metadata


class TestProtoResource(unittest.TestCase):
    """ Test for resource, mother class of PrototypeText and Passage """
    def test_init(self):
        a = CTSNode(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(a.id, "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(a.urn, URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2"))
        self.assertIsInstance(a.citation, Citation)


        a.resource = True
        self.assertEqual(a.resource, True)

    def test_urn(self):
        """ Test setters and getters for urn """
        a = CTSNode()
        # Should work with string
        a.urn = "urn:cts:latinLit:tg.wk.v" 
        self.assertEqual(isinstance(a.urn, MyCapytain.common.reference.URN), True)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:tg.wk.v")

        # Test for URN
        a.urn = MyCapytain.common.reference.URN("urn:cts:latinLit:tg.wk.v2") 
        self.assertEqual(isinstance(a.urn, MyCapytain.common.reference.URN), True)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:tg.wk.v2")

        # Test it fails if not basestring or URN
        with self.assertRaises(TypeError): 
            a.urn = 2

        # Test Resource setting works out as well
        b = CitableText(urn="urn:cts:latinLit:tg.wk.v")
        self.assertEqual(str(b.urn), "urn:cts:latinLit:tg.wk.v")


class TestProtoText(unittest.TestCase):
    """ Test the text prototype, mainly to ensure consistency """

    def test_init(self):
        """ Test init works correctly """
        a = CitableText()

        #  Test with metadata
        a = CitableText()
        self.assertIsInstance(a.metadata, MyCapytain.common.metadata.Metadata)

        m = MyCapytain.common.metadata.Metadata(keys=["title", "author"])
        m["title"]["fre"] = "I am a metadata"
        a = CitableText(metadata=m)
        self.assertEqual(a.metadata["title"]["fre"], "I am a metadata")

    def test_proto_reff(self):
        """ Test that getValidReff function are not implemented """
        a = CitableText()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError):
            a.getValidReff()

        # It takes two parameters, should not issue TypeError
        # Consistency check
        with self.assertRaises(NotImplementedError):
            a.getValidReff(level=1, reference=["1"])

    def test_proto_passage(self):
        """ Test that getPassage function are not implemented but are consistent"""
        a = CitableText()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError):
            a.getTextualNode(subreference=None)

    def test_get_label(self):
        """ Test that getLabel function are not implemented but are consistent"""
        a = CitableText()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError): 
            a.getLabel()

    def test_urn(self):
        """ Test setters and getters for urn """
        a = CitableText()
        # Should work with string
        a.urn = "urn:cts:latinLit:tg.wk.v" 
        self.assertEqual(isinstance(a.urn, MyCapytain.common.reference.URN), True)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:tg.wk.v")

        # Test for URN
        a.urn = MyCapytain.common.reference.URN("urn:cts:latinLit:tg.wk.v2") 
        self.assertEqual(isinstance(a.urn, MyCapytain.common.reference.URN), True)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:tg.wk.v2")

        # Test it fails if not basestring or URN
        with self.assertRaises(TypeError): 
            a.urn = 2

        # Test original setting works out as well
        b = CitableText(urn="urn:cts:latinLit:tg.wk.v")
        self.assertEqual(str(b.urn), "urn:cts:latinLit:tg.wk.v")

    def test_reffs(self):
        """ Test property reff, should fail because it supposes validReff is implemented """
        a = CitableText()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError):
            a.reffs

    def test_citation(self):
        """ Test citation property setter and getter """
        a = CitableText()
        a.citation = MyCapytain.common.reference.Citation(name="label")
        self.assertIsInstance(a.citation, MyCapytain.common.reference.Citation)

        #On init ?
        b = CitableText(citation=MyCapytain.common.reference.Citation(name="label"))
        self.assertEqual(b.citation.name, "label")
