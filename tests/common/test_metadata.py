# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import six
from collections import defaultdict
from MyCapytain.common.metadata import Metadata, Metadatum

class TestMetadatum(unittest.TestCase):
    def test_init(self):
        a = Metadatum("title")
        self.assertEqual(a.name, "title")

    def test_set_item(self):
        a = Metadatum("title")
        a["eng"] = "Epigrams"
        self.assertEqual(a["eng"], "Epigrams")
        # It should set a default too
        self.assertEqual(a["fre"], "Epigrams")
        # But not twice
        a["fre"] = "Epigrammes"
        self.assertEqual(a["spa"], "Epigrams")
        self.assertEqual(a["fre"], "Epigrammes")
        # Set tuples with one value
        a[("lat", "grc")] = "Epigrammata"
        self.assertEqual(a["lat"], "Epigrammata")
        self.assertEqual(a["grc"], "Epigrammata")
        # Set tuples with tuples
        a = Metadatum("title")
        a[("lat", "grc")] = ("Epigrammata", "ἐπιγραμματον")
        self.assertEqual(a["lat"], "Epigrammata")
        self.assertEqual(a["grc"], "ἐπιγραμματον")
        # Set error because key is wrong
        with six.assertRaisesRegex(self, TypeError, "Only basestring or tuple instances are accepted as key"):
            a[3.5] = "test"
        with six.assertRaisesRegex(self, ValueError, "Less values than keys detected"):
            a[("lat", "grc")] = ["Epigrammata"]
        

    def test_init_with_children(self):
        a = Metadatum("title", [
                ("eng", "Epigrams"),
                ("fre", "Epigrammes")
            ])
        self.assertEqual(a["fre"], "Epigrammes")
        self.assertEqual(a["eng"], "Epigrams")

    def test_override_default(self):
        a = Metadatum("title", [
                ("eng", "Epigrams"),
                ("fre", "Epigrammes")
            ])
        self.assertEqual(a["spa"], "Epigrams")
        a.setDefault("fre")
        self.assertEqual(a["spa"], "Epigrammes")
        # If key is not available, should raise an error
        with six.assertRaisesRegex(self, ValueError, "Can not set a default to an unknown key"):
            a.setDefault(None)

    def test_len(self):
        a = Metadatum("title", [
                ("eng", "Epigrams"),
                ("fre", "Epigrammes")
            ])
        self.assertEqual(len(a), 2)

    def test_get_item(self):
        a = Metadatum("title", [
                ("eng", "Epigrams"),
                ("fre", "Epigrammes")
            ])
        self.assertEqual(a[0], "Epigrams")
        self.assertEqual(a["eng"], "Epigrams")
        self.assertEqual(a["spa"], "Epigrams")
        self.assertEqual(a[1], "Epigrammes")
        # Access through tuple !
        self.assertEqual(a[(0,1)], ("Epigrams", "Epigrammes"))
        with self.assertRaises(KeyError):
            z = a[2]

        a.default = None
        with self.assertRaises(KeyError):
            z = a["spa"]

    def test_iter(self):
        data = [
                ("eng", "Epigrams"),
                ("fre", "Epigrammes")
            ]
        a = Metadatum("title", [
                ("eng", "Epigrams"),
                ("fre", "Epigrammes")
            ])

        testdata = [(k, v) for k, v in a]
        self.assertEqual(list(a), testdata)

        a["lat"] = "Epigrammata"
        testdata = [(k, v) for k, v in a]
        self.assertEqual(testdata, data + [("lat", "Epigrammata")])

        i = 0
        d=[]
        for k, v in a:
            d.append(k)
            break
        self.assertEqual(d, ["eng"])

        i = 0
        d=[]
        for k, v in a:
            d.append(k)
            if i == 1:
                break
            i += 1
        self.assertEqual(d, ["eng", "fre"])


class TestMetadata(unittest.TestCase):
    def test_init(self):
        a = Metadata()
        self.assertTrue(hasattr(a, "metadata"), True)
        self.assertTrue(isinstance(a.metadata, defaultdict))

        a = Metadata(keys=["title"])
        self.assertTrue(isinstance(a.metadata["title"], Metadatum))

    def test_set(self):
        a = Metadata()
        a["title"] = [("eng", "Epigrams")]
        self.assertEqual(a["title"]["eng"], "Epigrams")
        a[("desc", "label")] = ([("eng", "desc")], [("eng", "lbl"), ("fre", "label")])
        self.assertEqual(a["desc"]["eng"], "desc")
        self.assertEqual(a["label"][("eng", "fre")], ("lbl", "label"))

    def test_get(self):
        a = Metadata()
        m1 = Metadatum("desc", [("eng", "desc")])
        m2 = Metadatum("label", [("eng", "lbl"), ("fre", "label")])
        a[("desc", "label")] = (m1, m2)
        self.assertEqual(a[("desc", "label")], (m1, m2))

        self.assertEqual(a[0], m1)
        with self.assertRaises(KeyError):
            z = a[2]
        with self.assertRaises(KeyError):
            z = a["textgroup"]

        with six.assertRaisesRegex(self, TypeError, "Only basestring or tuple instances are accepted as key"):
            a[3.5] = "test"
        with six.assertRaisesRegex(self, ValueError, "Less values than keys detected"):
            a[("lat", "grc")] = ["Epigrammata"]

    def test_iter(self):
        a = Metadata()
        m1 = Metadatum("desc", [("eng", "desc")])
        m2 = Metadatum("label", [("eng", "lbl"), ("fre", "label")])
        a["desc"] = m1
        a["label"] = m2

        i = 0
        d=[]
        d2=[]
        for k, v in a:
            d.append(k)
            d2.append(v)
            if i == 1:
                break
            i += 1
        self.assertEqual(d, ["desc", "label"])
        self.assertEqual(d2, [m1, m2])

        i = 0
        d=[]
        d2=[]
        for k, v in a:
            d.append(k)
            d2.append(v)
            break
        self.assertEqual(d, ["desc"])
        self.assertEqual(d2, [m1])

        self.assertEqual(list(a), [("desc", m1), ("label", m2)])

    def test_len(self):
        a = Metadata()
        m1 = Metadatum("desc", [("eng", "desc")])
        m2 = Metadatum("label", [("eng", "lbl"), ("fre", "label")])
        a["desc"] = m1
        self.assertEqual(len(a), 1)
        a["label"] = m2
        self.assertEqual(len(a), 2)
        a["z"] = 1.5
        self.assertEqual(len(a), 2)

    def test_add(self):
        """ Test sum of two Metadata objects  """
        a = Metadata()
        m1 = Metadatum("desc", [("eng", "desc")])
        m2 = Metadatum("label", [("eng", "lbl"), ("fre", "label")])
        a["desc"] = m1
        a["label"] = m2

        b = Metadata()
        m3 = Metadatum("desc", [("fre", "Omelette")])
        m4 = Metadatum("title", [("eng", "ttl"), ("fre", "titre")])
        b[("desc", "title")] = (m3, m4)

        c = a + b
        self.assertEqual(len(c), 3)
        self.assertEqual(len(c["desc"]), 2)

