# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
import six
from MyCapytain.utils import *

class TestReferenceImplementation(unittest.TestCase):

    """ Test how reference reacts """

    def test_str_function(self):
        a = Reference("1-1")
        self.assertEqual(str(a), "1-1")

    def test_str_getitem(self):
        a = Reference("1.1@Achilles[0]-1.10@Atreus[3]")
        self.assertEqual(a["any"], "1.1@Achilles[0]-1.10@Atreus[3]")
        self.assertEqual(a["start"], "1.1@Achilles[0]")
        self.assertEqual(a["start_list"], ["1", "1"])
        self.assertEqual(a["start_sub"][0], "Achilles")
        self.assertEqual(a["end"], "1.10@Atreus[3]")
        self.assertEqual(a["end_list"], ["1", "10"])
        self.assertEqual(a["end_sub"][1], "3")
        self.assertEqual(a["end_sub"], ("Atreus", "3"))

    def test_int_getItem(self):
        a = Reference("1.1@Achilles-1.10@Atreus[3]")
        self.assertEqual(a[1], "1.1@Achilles")
        self.assertEqual(a[2], ["1", "1"])
        self.assertEqual(a[3][0], "Achilles")
        self.assertEqual(a[4], "1.10@Atreus[3]")
        self.assertEqual(a[5], ["1", "10"])
        self.assertEqual(a[6][1], "3")
        self.assertEqual(a[6], ("Atreus", "3"))

    def test_Unicode_Support(self):
        a = Reference("1.1@καὶ[0]-1.10@Ἀλκιβιάδου[3]")
        self.assertEqual(a[1], "1.1@καὶ[0]")
        self.assertEqual(a[2], ["1", "1"])
        self.assertEqual(a[3][0], "καὶ")
        self.assertEqual(a[4], "1.10@Ἀλκιβιάδου[3]")
        self.assertEqual(a[5], ["1", "10"])
        self.assertEqual(a[6][1], "3")
        self.assertEqual(a[6], ("Ἀλκιβιάδου", "3"))

    def test_NoWord_Support(self):
        a = Reference("1.1@[0]-1.10@Ἀλκιβιάδου[3]")
        self.assertEqual(a[1], "1.1@[0]")
        self.assertEqual(a[3][0], "")
        self.assertEqual(a[3][1], "0")

    def test_No_End_Support(self):
        a = Reference("1.1@[0]")
        self.assertEqual(a[4], None)
        self.assertEqual(a[1], "1.1@[0]")
        self.assertEqual(a[3][0], "")
        self.assertEqual(a[3][1], "0")

    def test_equality(self):
        a = Reference("1.1@[0]")
        b = Reference("1.1@[0]")
        c = Reference("1.1@[1]")
        d = "1.1@[0]"
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)


class TestURNImplementation(unittest.TestCase):

    """ Test how reference reacts """

    def test_str_function(self):
        a = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(str(a), "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")

    def test_int_access(self):
        a = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a[0], "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a[1], "cts")
        self.assertEqual(a[2], "greekLit")
        self.assertEqual(a[3], "tlg0012")
        self.assertEqual(a[4], "tlg001")
        self.assertEqual(a[5], "mth-01")
        self.assertEqual(a[6], "1.1@Achilles-1.10@the[2]")
        self.assertEqual(a[7], Reference("1.1@Achilles-1.10@the[2]"))

    def test_str_access(self):
        a = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a["full"], "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a["urn_namespace"], "urn:cts")
        self.assertEqual(a["cts_namespace"], "urn:cts:greekLit")
        self.assertEqual(a["textgroup"], "urn:cts:greekLit:tlg0012")
        self.assertEqual(a["work"], "urn:cts:greekLit:tlg0012.tlg001")
        self.assertEqual(a["text"], "urn:cts:greekLit:tlg0012.tlg001.mth-01")
        self.assertEqual(a["passage"], "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a["reference"], Reference("1.1@Achilles-1.10@the[2]"))
        self.assertEqual(a["start"], "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles")
        self.assertEqual(a["end"], "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.10@the[2]")

    def test_equality(self):
        a = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        b = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        c = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[3]")
        d = "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]"
        self.assertEqual(a,b)
        self.assertNotEqual(a,c)
        self.assertNotEqual(a,d)

    def test_full_emptiness(self):
        a = URN("urn:cts:greekLit")
        self.assertEqual(a["full"], "urn:cts:greekLit")
        self.assertEqual(a["urn_namespace"], "urn:cts")
        self.assertEqual(a["cts_namespace"], "urn:cts:greekLit")
        self.assertIsNone(a["textgroup"])
        self.assertIsNone(a["work"])
        self.assertIsNone(a["text"])
        self.assertIsNone(a["passage"])
        self.assertIsNone(a["reference"])
        self.assertIsNone(a["start"])
        self.assertIsNone(a["end"])

    def test_from_textgroup_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup")
        self.assertEqual(a["full"], "urn:cts:greekLit:textgroup")
        self.assertEqual(a["urn_namespace"], "urn:cts")
        self.assertEqual(a["cts_namespace"], "urn:cts:greekLit")
        self.assertEqual(a["textgroup"], "urn:cts:greekLit:textgroup")
        self.assertIsNone(a["work"])
        self.assertIsNone(a["text"])
        self.assertIsNone(a["passage"])
        self.assertIsNone(a["reference"])
        self.assertIsNone(a["start"])
        self.assertIsNone(a["end"])


    def test_from_work_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup.work")
        self.assertEqual(a["full"], "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a["urn_namespace"], "urn:cts")
        self.assertEqual(a["cts_namespace"], "urn:cts:greekLit")
        self.assertEqual(a["textgroup"], "urn:cts:greekLit:textgroup")
        self.assertEqual(a["work"], "urn:cts:greekLit:textgroup.work")
        self.assertIsNone(a["text"])
        self.assertIsNone(a["passage"])
        self.assertIsNone(a["reference"])
        self.assertIsNone(a["start"])
        self.assertIsNone(a["end"])

    def test_from_text_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup.work.text")
        self.assertEqual(a["full"], "urn:cts:greekLit:textgroup.work.text")
        self.assertEqual(a["urn_namespace"], "urn:cts")
        self.assertEqual(a["cts_namespace"], "urn:cts:greekLit")
        self.assertEqual(a["textgroup"], "urn:cts:greekLit:textgroup")
        self.assertEqual(a["work"], "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a["text"], "urn:cts:greekLit:textgroup.work.text")
        self.assertIsNone(a["passage"])
        self.assertIsNone(a["reference"])
        self.assertIsNone(a["start"])
        self.assertIsNone(a["end"])

    def test_no_end_text_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup.work.text:1")
        self.assertEqual(a["full"], "urn:cts:greekLit:textgroup.work.text:1")
        self.assertEqual(a["urn_namespace"], "urn:cts")
        self.assertEqual(a["cts_namespace"], "urn:cts:greekLit")
        self.assertEqual(a["textgroup"], "urn:cts:greekLit:textgroup")
        self.assertEqual(a["work"], "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a["text"], "urn:cts:greekLit:textgroup.work.text")
        self.assertEqual(a["passage"], "urn:cts:greekLit:textgroup.work.text:1")
        self.assertEqual(a["reference"], Reference("1"))
        self.assertEqual(a["start"], "urn:cts:greekLit:textgroup.work.text:1")
        self.assertIsNone(a["end"])

    def test_missing_text_in_passage_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup.work:1-2")
        self.assertEqual(a["full"], "urn:cts:greekLit:textgroup.work:1-2")
        self.assertEqual(a["urn_namespace"], "urn:cts")
        self.assertEqual(a["cts_namespace"], "urn:cts:greekLit")
        self.assertEqual(a["textgroup"], "urn:cts:greekLit:textgroup")
        self.assertEqual(a["work"], "urn:cts:greekLit:textgroup.work")
        self.assertIsNone(a["text"])
        self.assertEqual(a["passage"], "urn:cts:greekLit:textgroup.work:1-2")
        self.assertEqual(a["reference"], Reference("1-2"))
        self.assertEqual(a["start"], "urn:cts:greekLit:textgroup.work:1")
        self.assertEqual(a["end"], "urn:cts:greekLit:textgroup.work:2")

    def test_warning_on_empty(self):
        with self.assertRaises(ValueError):
            a = URN("urn:cts")

    def test_len(self):
        a = URN("urn:cts:greekLit")
        self.assertEqual(len(a), 2)

    def test_greater(self):
        a = URN("urn:cts:greekLit")
        b = URN("urn:cts:greekLit:textgroup")
        self.assertGreater(b, a)

    def test_lower(self):
        a = URN("urn:cts:greekLit")
        b = URN("urn:cts:greekLit:textgroup")
        self.assertEqual(a < b, True)

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
            print(a[2])

        a.default = None
        with self.assertRaises(KeyError):
            print(a["spa"])
