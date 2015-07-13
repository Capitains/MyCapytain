# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str
from codecs import open
import xmlunittest

import MyCapytain.resources.texts.local


class TestLocalXMLImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):

    """ Test XML Implementation of resources Endpoint request making """

    def setUp(self):
        self.text = open("tests/testing_data/texts/sample.xml", "r")
        self.TEI = MyCapytain.resources.texts.local.Text(resource=self.text)

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