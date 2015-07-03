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