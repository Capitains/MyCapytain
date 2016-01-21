# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str
from io import open
import xmlunittest
import warnings
from lxml import etree
from copy import copy

import MyCapytain.resources.texts.local
import MyCapytain.resources.texts.tei
import MyCapytain.common.reference
import MyCapytain.common.utils
import MyCapytain.errors



class TestLocalXMLTextImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):

    """ Test XML Implementation of resources found in local file """

    def setUp(self):
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.Text(resource=self.text)
        self.treeroot = etree._ElementTree()

        with open("tests/testing_data/texts/text_or_xpath.xml") as f:
            self.text_complex = MyCapytain.resources.texts.local.Text(resource=f)

    def tearDown(self):
        self.text.close()

    def testURN(self):
        """ Check that urn is set"""
        TEI = MyCapytain.resources.texts.local.Text(resource=self.TEI.xml, urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(str(TEI.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")

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

    def testFindComplexCitation(self):
        self.assertEqual(len(self.text_complex.citation), 2)

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

    def testValidReffs(self):
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

    def test_warning(self):
        with open("tests/testing_data/texts/duplicate_references.xml") as xml:
            text = MyCapytain.resources.texts.local.Text(resource=xml)
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            for i in [1,2,3]:
                passages = text.getValidReff(level=i)

        self.assertEqual(len(w), 3, "There should be warning on each level")
        self.assertEqual(issubclass(w[-1].category, MyCapytain.errors.DuplicateReference), True, "Warning should be DuplicateReference")
        self.assertEqual(str(w[0].message), "1", "Warning message should be list of duplicate")

    def test_wrong_main_scope(self):
        with open("tests/testing_data/texts/sample2.xml", "rb") as file:
            with self.assertRaises(MyCapytain.resources.texts.local.RefsDeclError):
                text = MyCapytain.resources.texts.local.Text(resource=file)

    def test_reffs(self):
        """ Check that every level is returned trough reffs property """
        self.assertEqual(("1" in self.TEI.reffs), True)
        self.assertEqual(("1.pr" in self.TEI.reffs), True)
        self.assertEqual(("2.40.8" in self.TEI.reffs), True)

    def test_complex_reffs(self):
        """ Test when there is a (something|something) xpath
        """
        self.assertEqual(("pr.1" in self.text_complex.reffs), True)

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

    def test_get_Passage_context(self):
        """ Check that get Passage contexts return right information """"""
        simple = self.TEI.getPassage(["1", "pr", "2"], hypercontext=True)
        self.assertEqual(
            simple, (["1", "pr", "2"], ["1", "pr", "2"]),
            "There should be two lists"
        )
        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2"), hypercontext=True)
        self.assertEqual(
            simple, (["1", "pr", "2"], ["1", "pr", "2"]),
            "There should be two lists"
        )
        complex = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.1-1.pr.7"), hypercontext=True)
        self.assertEqual(
            complex, (["1", "pr", "1"], ["1", "pr", "7"])
        )"""

    def test_clean_xpath(self):
        """ Cleaning XPATH and normalizing them """
        l = ['tei:text', 'tei:body', 'tei:div', "tei:div[@n='1']", "tei:div[@n='pr']", "tei:l[@n='2']"]
        self.assertEqual(self.TEI._normalizeXpath(l), l)

        l = ['tei:text', 'tei:body', 'tei:div', "tei:div[@n='1']", "", "tei:div[@n='pr']", "tei:l[@n='2']"]
        self.assertEqual(
            self.TEI._normalizeXpath(l),
            ['tei:text', 'tei:body', 'tei:div', "tei:div[@n='1']", "/tei:div[@n='pr']", "tei:l[@n='2']"],
            "Empty list element should be replaced with / in the next element"
        )

    def test_get_Passage_context_no_double_slash(self):
        """ Check that get Passage contexts return right information """
        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2"), hypercontext=True)
        str_simple = etree.tostring(simple, encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.TEI.citation
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.2")).text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (One reference Passage)"
        )

        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.pr.7"), hypercontext=True)
        str_simple = etree.tostring(simple, encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.TEI.citation
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.2")).text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level same parent range Passage)"
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.3")).text().strip(),
            "senserit, cum salva infimarum quoque personarum re-",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level same parent range Passage)"
        )
        self.assertEqual(
            text.getValidReff(level=3),
            ["1.pr.2", "1.pr.3", "1.pr.4", "1.pr.5", "1.pr.6", "1.pr.7"],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level same parent range Passage)"
        )

        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.1.6"), hypercontext=True)
        str_simple = etree.tostring(simple, encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.TEI.citation
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.2")).text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level range Passage)"
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.1.6")).text().strip(),
            "Rari post cineres habent poetae.",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level range Passage)"
        )
        self.assertEqual(
            text.getValidReff(level=3),
            [
                "1.pr.2", "1.pr.3", "1.pr.4", "1.pr.5", "1.pr.6", "1.pr.7",
                "1.pr.8", "1.pr.9", "1.pr.10", "1.pr.11", "1.pr.12", "1.pr.13",
                "1.pr.14", "1.pr.15", "1.pr.16", "1.pr.17", "1.pr.18", "1.pr.19",
                "1.pr.20", "1.pr.21", "1.pr.22",
                "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.1.6",
            ],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level range Passage)"
        )

        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.2"), hypercontext=True)
        str_simple = etree.tostring(simple, encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.TEI.citation
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.2")).text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.1.6")).text().strip(),
            "Rari post cineres habent poetae.",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            text.getValidReff(level=3),
            [
                "1.pr.2", "1.pr.3", "1.pr.4", "1.pr.5", "1.pr.6", "1.pr.7",
                "1.pr.8", "1.pr.9", "1.pr.10", "1.pr.11", "1.pr.12", "1.pr.13",
                "1.pr.14", "1.pr.15", "1.pr.16", "1.pr.17", "1.pr.18", "1.pr.19",
                "1.pr.20", "1.pr.21", "1.pr.22",
                "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.1.6",
            ],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )

    def test_copy_node_without_children(self):
        node = MyCapytain.common.utils.xmlparser("<a b='foo' xmlns='http://www.tei-c.org/ns/1.0'>M<b>c</b></a>")

        no_text = copy(node)
        no_text.text = None  # Remove text
        [no_text.remove(a) for a in no_text]  # Remove nodes
        copied_node = self.TEI._copyNode(node)
        self.assertEqual(
            etree.tostring(copied_node),
            etree.tostring(no_text),
            "Text without children should have no text nor xml nodes"
        )
        self.assertNotIn(
            "<b>",
            etree.tostring(copied_node, encoding=str),
            "Text without children should have no text nor xml nodes"
        )
        self.assertNotIn(
            "M",
            etree.tostring(copied_node, encoding=str),
            "Text without children should have no text nor xml nodes"
        )

    def test_copy_node_with_children(self):
        node = MyCapytain.common.utils.xmlparser("<a b='foo' xmlns='http://www.tei-c.org/ns/1.0'>M<b>c</b></a>")
        comparison = copy(node)

        copied_node = self.TEI._copyNode(node, children=True)
        self.assertEqual(
            etree.tostring(copied_node),
            etree.tostring(comparison),
            "Text without children should have no text nor xml nodes"
        )
        self.assertIn(
            "<b>",
            etree.tostring(copied_node, encoding=str),
            "Text without children should have no text nor xml nodes"
        )



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