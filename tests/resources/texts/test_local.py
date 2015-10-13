# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str
from io import open
import xmlunittest

import MyCapytain.resources.texts.local
import MyCapytain.resources.texts.tei
import MyCapytain.common.reference
        

class TestLocalXMLTextImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):

    """ Test XML Implementation of resources found in local file """

    def setUp(self):
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.Text(resource=self.text)

    def tearDown(self):
        self.text.close()

    def testFindCitation(self):
        self.assertEqual(
            str(self.TEI.citation),
            '<tei:cRefPattern n="book" matchPattern="(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\\\'$1\\\'])"><tei:p>This pointer pattern extracts book</tei:p></tei:cRefPattern>'
        )
        self.assertEqual(
            str(self.TEI.citation.child),
            '<tei:cRefPattern n="poem" matchPattern="(\\w+)\.(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\\\'$1\\\']/tei:div[@n=\\\'$2\\\'])"><tei:p>This pointer pattern extracts poem</tei:p></tei:cRefPattern>'
        )
        self.assertEqual(
            str(self.TEI.citation.child.child),
            '<tei:cRefPattern n="line" matchPattern="(\\w+)\.(\\w+)\.(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\\\'$1\\\']/tei:div[@n=\\\'$2\\\']/tei:l[@n=\\\'$3\\\'])"><tei:p>This pointer pattern extracts line</tei:p></tei:cRefPattern>'
        )

        self.assertEqual(len(self.TEI.citation), 3)

    def testCitationSetters(self):
        d = MyCapytain.resources.texts.tei.Citation()
        c = MyCapytain.common.reference.Citation(name="ahah", refsDecl="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']", child=None)
        b = MyCapytain.resources.texts.tei.Citation()
        a = MyCapytain.resources.texts.local.Text(citation=b)
        """ Test original setting """
        self.assertIs(a.citation, b)
        """ Test simple replacement """
        a.citation = d
        self.assertIs(a.citation, d)
        """ Test conversion """
        a.citation = c
        self.assertEqual(a.citation.name, "ahah")
        self.assertEqual(a.citation.child, None)
        self.assertEqual(a.citation.refsDecl, "/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']")
        self.assertEqual(a.citation.scope, "/tei:TEI/tei:text/tei:body/tei:div")
        self.assertEqual(a.citation.xpath, "/tei:div[@n='?']")

    def testFindCitation(self):
        # Test level 1
        self.assertEqual(self.TEI.getValidReff(), ["1", "2"])
        # Test level 2
        self.assertEqual(self.TEI.getValidReff(level=2)[0], "1.pr")
        # Test level 3
        self.assertEqual(self.TEI.getValidReff(level=3)[0], "1.pr.1")
        self.assertEqual(self.TEI.getValidReff(level=3)[-1], "2.40.8")

        # Test with reference and level
        self.assertEqual(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1"),level=3)[1], "2.1.2")
        self.assertEqual(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1"),level=3)[-1], "2.1.12")

        # Test with reference and level autocorrected because too small
        self.assertEqual(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1"),level=0)[-1], "2.1.12")
        self.assertEqual(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1"),level=2)[-1], "2.1.12")

        # Test when already too deep
        self.assertEqual(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1.1"),level=3), [])

        # Test wrong citation
        with self.assertRaises(KeyError): 
            self.assertEqual(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.hellno"),level=3), [])

    def test_wrong_main_scope(self):
        with open("tests/testing_data/texts/sample2.xml", "rb") as file:
            with self.assertRaises(MyCapytain.resources.texts.local.RefsDeclError):
                text = MyCapytain.resources.texts.local.Text(resource=file)

    def test_reffs(self):
        """ Check that every level is returned trough reffs property """
        self.assertEqual(("1" in self.TEI.reffs), True)
        self.assertEqual(("1.pr" in self.TEI.reffs), True)
        self.assertEqual(("2.40.8" in self.TEI.reffs), True)

    def test_urn(self):
        """ Test setters and getters for urn """

        # Should work with string
        self.TEI.urn = "urn:cts:latinLit:tg.wk.v" 
        self.assertEqual(isinstance(self.TEI.urn, MyCapytain.common.reference.URN), True)
        self.assertEqual(str(self.TEI.urn), "urn:cts:latinLit:tg.wk.v")

        # Test for URN
        self.TEI.urn = MyCapytain.common.reference.URN("urn:cts:latinLit:tg.wk.v2") 
        self.assertEqual(isinstance(self.TEI.urn, MyCapytain.common.reference.URN), True)
        self.assertEqual(str(self.TEI.urn), "urn:cts:latinLit:tg.wk.v2")

        # Test it fails if not basestring or URN
        with self.assertRaises(TypeError): 
            self.TEI.urn = 2

    def test_get_passage(self):
        a = self.TEI.getPassage(["1", "pr", "2"])
        self.assertEqual(a.text(), "tum, ut de illis queri non possit quisquis de se bene ")
        # With reference
        a = self.TEI.getPassage(MyCapytain.common.reference.Reference("2.5.5"))
        self.assertEqual(a.text(), "Saepe domi non es, cum sis quoque, saepe negaris: ")

    def test_get_passage_plus(self):
        """ Test GetPassage Plus """
        # No label in local 
        a = self.TEI.getPassagePlus(["1", "pr", "2"])

        self.assertEqual(a.prev, ["1", "pr", "1"])
        self.assertEqual(a.next, ["1", "pr", "3"])
        self.assertEqual(a.passage.text(), "tum, ut de illis queri non possit quisquis de se bene ")


class TestLocalXMLPassageImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test passage implementation """

    def setUp(self):
        self.URN = MyCapytain.common.reference.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.URN_2 = MyCapytain.common.reference.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat3")
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.Text(resource=self.text)

    def tearDown(self):
        self.text.close()

    def test_urn(self):
        """ Test URN and ids getters/setters """

        a = MyCapytain.resources.texts.local.Passage()
 
        #~Test simple set up
        a.urn = self.URN
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        # Test update on ID update
        a.id = ["1", "pr", "1"]
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        # Should keep the ID if URN changes
        a.urn = self.URN_2
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat3:1.pr.1")
        # Test init
        a = MyCapytain.resources.texts.local.Passage(urn=self.URN)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        # Test init with id and URN
        a = MyCapytain.resources.texts.local.Passage(urn=self.URN, id=["1", "pr", "1"])
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        # Should raise error if not URN for consistency
        with self.assertRaises(TypeError):
            a.urn = 1
        # Should work with plain text
        a = MyCapytain.resources.texts.local.Passage()
        a.urn = "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1"
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        self.assertEqual(a.id, ["1", "pr", "1"])
        # This should affect id !
        # Test Id value on init
        a = MyCapytain.resources.texts.local.Passage(id=["1", "pr", "1"])
        self.assertEqual(a.id, ["1", "pr", "1"])

    def test_next(self):
        """ Test next property """
        # Normal passage checking
        p = self.TEI.getPassage(["1", "pr", "1"])
        self.assertEqual(p.next.id, ["1", "pr", "2"])

        # End of lowest level passage checking but not end of parent level
        p = self.TEI.getPassage(["1", "pr", "22"])
        self.assertEqual(p.next.id, ["1", "1", "1"])

        # End of lowest level passage and end of parent level
        p = self.TEI.getPassage(["1", "39", "8"])
        self.assertEqual(p.next.id, ["2", "pr", "sa"])

        # Last line should always be None
        p = self.TEI.getPassage(["2", "40", "8"])
        self.assertIsNone(p.next)
        p = self.TEI.getPassage(["2", "40"])
        self.assertIsNone(p.next)
        p = self.TEI.getPassage(["2"])
        self.assertIsNone(p.next)

    def test_children(self):
        """ Test children property """
        # Normal children checking
        with open("tests/testing_data/texts/sample.xml", "rb") as text:
            self.TEI = MyCapytain.resources.texts.local.Text(resource=text)

            p = self.TEI.getPassage(["1", "pr"])
            self.assertEqual(p.children["1.pr.1"].id, ["1", "pr", "1"])

            p = self.TEI.getPassage(["1", "pr", "1"])
            self.assertEqual(len(p.children), 0)

    def test_first(self):
        """ Test first property """
        # Test when there is one
        p = self.TEI.getPassage(["1", "pr"])
        self.assertEqual(p.first.id, ["1", "pr", "1"])
        # #And failing when no first
        p = self.TEI.getPassage(["1", "pr", "1"])
        self.assertEqual(p.first, None)

    def test_last(self):
        """ Test last property """
        # Test when there is one
        p = self.TEI.getPassage(["1", "pr"])
        self.assertEqual(p.last.id, ["1", "pr", "22"])
        # #And failing when no last
        p = self.TEI.getPassage(["1", "pr", "1"])
        self.assertEqual(p.last, None)

    def test_prev(self):
        """ Test prev property """
        # Normal passage checking
        p = self.TEI.getPassage(["2", "40", "8"])
        self.assertEqual(p.prev.id, ["2", "40", "7"])
        p = self.TEI.getPassage(["2", "40"])
        self.assertEqual(p.prev.id, ["2", "39"])
        p = self.TEI.getPassage(["2"])
        self.assertEqual(p.prev.id, ["1"])

        # test failing passage
        p = self.TEI.getPassage(["1", "pr", "1"])
        self.assertEqual(p.prev, None)
        p = self.TEI.getPassage(["1", "pr"])
        self.assertEqual(p.prev, None)
        p = self.TEI.getPassage(["1"])
        self.assertEqual(p.prev, None)

        # First child should get to parent's prev last child
        p = self.TEI.getPassage(["1", "1", "1"])
        self.assertEqual(p.prev.id, ["1", "pr", "22"])

        # Beginning of lowest level passage and beginning of parent level
        p = self.TEI.getPassage(["2", "pr", "sa"])
        self.assertEqual(p.prev.id, ["1", "39", "8"])