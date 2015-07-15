# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import six

from io import open
from collections import defaultdict
from MyCapytain.resources.proto.text import *
import MyCapytain.common.reference

class TestProtoResource(unittest.TestCase):
    """ Test for resource, mother class of Text and Passage """
    def test_init(self):
        a = Resource()
        self.assertEqual(a.resource, None)

        a = Resource(resource=False)
        self.assertEqual(a.resource, False)
        
        a.resource = True
        self.assertEqual(a.resource, True)

    def test_urn(self):
        """ Test setters and getters for urn """
        a = Resource()
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
        b = Text(urn="urn:cts:latinLit:tg.wk.v")
        self.assertEqual(str(b.urn), "urn:cts:latinLit:tg.wk.v")

class TestProtoText(unittest.TestCase):
    def test_init(self):
        a = Text()
        self.assertEqual(a.resource, None)

        a = Text(resource=False)
        self.assertEqual(a.resource, False)

        a.resource = True
        self.assertEqual(a.resource, True)

    def test_proto_reff(self):
        """ Test that getValidReff function are not implemented """
        a = Text()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError):
            a.getValidReff()

        # It takes two parameters, should not issue TypeError
        # Consistency check
        with self.assertRaises(NotImplementedError):
            a.getValidReff(level=1, reference=["1"])


    def test_proto_passage(self):
        """ Test that getPassage function are not implemented but are consistent"""
        a = Text()

        # For getPassage, reference arg is required
        with self.assertRaises(TypeError): 
            a.getPassage()
        # It should fail because not implemented
        with self.assertRaises(NotImplementedError): 
            a.getPassage(reference=None)


    def test_get_label(self):
        """ Test that getLabel function are not implemented but are consistent"""
        a = Text()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError): 
            a.getLabel()

    def test_urn(self):
        """ Test setters and getters for urn """
        a = Text()
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
        b = Text(urn="urn:cts:latinLit:tg.wk.v")
        self.assertEqual(str(b.urn), "urn:cts:latinLit:tg.wk.v")


    def test_reffs(self):
        """ Test property reff, should fail because it supposes validReff is implemented """
        a = Text()

        # It should fail because not implemented
        with self.assertRaises(NotImplementedError):
            a.reffs

    def test_citation(self):
        """ Test citation property setter and getter """
        a = Text()
        a.citation = MyCapytain.common.reference.Citation(name="label")
        self.assertIsInstance(a.citation, MyCapytain.common.reference.Citation)

        #On init ?
        b = Text(citation=MyCapytain.common.reference.Citation(name="label"))
        self.assertEqual(a.citation.name, "label")