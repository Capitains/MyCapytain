# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import six

from io import open
from collections import defaultdict
from MyCapytain.resources.prototypes.cts import inventory as cts
from MyCapytain.common.reference import URN


class Resource(cts.CTSCollection):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        self.urn = None

    def parse(self, resource):
        return resource

    @property
    def id(self):
        return str(self.urn)


class TIV(cts.TextInventory):
    def parse(self, resource):
        self.textgroups = defaultdict(cts.TextGroup)
        return resource


class TestRepoProto(unittest.TestCase):
    def test_resource_proto(self):
        with self.assertRaises(NotImplementedError):
            a = cts.CTSCollection(resource="hello")

    def test_implementation(self):
        a = Resource(resource="hello")
        with self.assertRaises(KeyError):
            self.assertEqual(a[0], a)

    def test_equality(self):
        a = Resource(resource="hello")
        b = Resource(resource="hello2")
        c = Resource(resource=None)
        d = Resource(resource=None)

        self.assertNotEqual(a, b)
        self.assertNotEqual(a, 5)
        self.assertEqual((a == "i"), False)
        self.assertEqual(c, d)
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

        with six.assertRaisesRegex(self, KeyError, "urn:cts:greekLit is not part of this object"):
            a["urn:cts:greekLit"]

        self.assertEqual(a["urn:cts:greekLit:tg"], a)

        with six.assertRaisesRegex(self, KeyError, "urn:cts:greekLit:tg2 is not part of this object"):
            b["urn:cts:greekLit:tg2"]
        
    def test_edit_trans(self):
        a = cts.Edition()
        b = cts.Translation()
        self.assertIsInstance(a, cts.Text)
        self.assertIsInstance(b, cts.Text)
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
