import unittest
from MyCapytain.utils import *

class TestReferenceImplementation(unittest.TestCase):

    """ Test how reference reacts """

    def test_str_function(self):
        a = Reference("1-1")
        self.assertEqual(str(a), "1-1")

    def test_str_getitem(self):
        a = Reference("1.1@Achilles[0]-1.10@Atreus[3]")
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
        a = URN("urn:cts:greekLit:textgroup.work:1")
        self.assertEqual(a["full"], "urn:cts:greekLit:textgroup.work:1")
        self.assertEqual(a["urn_namespace"], "urn:cts")
        self.assertEqual(a["cts_namespace"], "urn:cts:greekLit")
        self.assertEqual(a["textgroup"], "urn:cts:greekLit:textgroup")
        self.assertEqual(a["work"], "urn:cts:greekLit:textgroup.work")
        self.assertIsNone(a["text"])
        self.assertEqual(a["passage"], "urn:cts:greekLit:textgroup.work:1")
        self.assertEqual(a["reference"], Reference("1"))
        self.assertEqual(a["start"], "urn:cts:greekLit:textgroup.work:1")
        self.assertIsNone(a["end"])