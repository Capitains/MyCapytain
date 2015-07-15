# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import six

from io import open
from collections import defaultdict
from MyCapytain.resources.proto import inventory
from MyCapytain.common.reference import URN

class Resource(inventory.Resource):
    def parse(self, resource):
        return resource

class TIV(inventory.TextInventory):
    def parse(self, resource):
        self.textgroups = defaultdict(inventory.TextGroup)
        return resource

class TestRepoProto(unittest.TestCase):
    def test_resource_proto(self):
        with self.assertRaises(NotImplementedError):
            a = inventory.Resource(resource="hello")

    def test_implementation(self):
        a = Resource(resource="hello")
        self.assertEqual(a[0], a)
        self.assertIsNone(a[3.4])

    def test_equality(self):
        a = Resource(resource="hello")
        b = Resource(resource="hello2")
        c = Resource(resource=None)
        d = Resource(resource=None)

        self.assertNotEqual(a, b)
        self.assertNotEqual(a, 5)
        self.assertEqual((a == "i"), False)
        self.assertNotEqual(c, d)
        c.urn = "hello"
        d.urn = c.urn 
        self.assertEqual(c, d)
        c.resource = "AHAH"
        self.assertNotEqual(c, d)
        d.resource = "AHAH"
        self.assertEqual(c, d)

    def test_urn_access(self):
        # Limited to what's possible in proto...
        a = Resource(resource="hello")
        a.urn = URN("urn:cts:greekLit:tg")

        b = TIV(resource="hello")

        with six.assertRaisesRegex(self, ValueError, "Not valid urn"):
            a["urn:cts:greekLit"]

        self.assertEqual(a["urn:cts:greekLit:tg"], a)

        with six.assertRaisesRegex(self, ValueError, "Unrecognized urn at level"):
            b["urn:cts:greekLit:tg2"]
        
    def test_edit_trans(self):
        a = inventory.Edition()
        b = inventory.Translation()
        self.assertIsInstance(a, inventory.Text)
        self.assertIsInstance(b, inventory.Text)
        self.assertEqual(a.subtype, "Edition")
        self.assertEqual(b.subtype, "Translation")

    def test_write(self):
        a = Resource(resource="hello")
        with self.assertRaises(NotImplementedError):
            a.export()

    def test_str(self):
        a = Resource(resource="hello")
        with self.assertRaises(NotImplementedError):
            str(a)
