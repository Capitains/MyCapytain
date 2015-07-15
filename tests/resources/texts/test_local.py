# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str
from io import open
import xmlunittest

import MyCapytain.resources.texts.local
import MyCapytain.resources.texts.tei
import MyCapytain.common.reference

class TestLocalXMLImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):

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

        # Test with passage and level
        self.assertEqual(self.TEI.getValidReff(passage=MyCapytain.common.reference.Reference("2.1"),level=3)[1], "2.1.2")
        self.assertEqual(self.TEI.getValidReff(passage=MyCapytain.common.reference.Reference("2.1"),level=3)[-1], "2.1.12")

        # Test with passage and level autocorrected because too small
        self.assertEqual(self.TEI.getValidReff(passage=MyCapytain.common.reference.Reference("2.1"),level=0)[-1], "2.1.12")
        self.assertEqual(self.TEI.getValidReff(passage=MyCapytain.common.reference.Reference("2.1"),level=2)[-1], "2.1.12")

        # Test when already too deep
        self.assertEqual(self.TEI.getValidReff(passage=MyCapytain.common.reference.Reference("2.1.1"),level=3), [])

        # Test wrong citation
        with self.assertRaises(KeyError): 
            self.assertEqual(self.TEI.getValidReff(passage=MyCapytain.common.reference.Reference("2.hellno"),level=3), [])


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