# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str
from codecs import open
import xmlunittest

import MyCapytain.resources.texts.local
import MyCapytain.resources.texts.tei
import MyCapytain.common.reference

class TestLocalXMLImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):

    """ Test XML Implementation of resources found in local file """

    def setUp(self):
        self.text = open("tests/testing_data/texts/sample.xml", "r")
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
