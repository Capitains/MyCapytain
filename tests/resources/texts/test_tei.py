# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str

from MyCapytain.common.utils import xmlparser
from MyCapytain.resources.texts.tei import *
from MyCapytain.common.reference import Reference


class TestTEICitation(unittest.TestCase):
    def test_str(self):
        a = Citation(name="book", xpath="/tei:div[@n=\"?\"]", scope="/tei:TEI/tei:body/tei:text/tei:div")
        self.assertEqual(
            str(a),"<tei:cRefPattern n=\"book\" matchPattern=\"(\\w+)\" replacementPattern=\"#xpath(/tei:TEI/tei:body/tei:text/tei:div/tei:div[@n=\"$1\"])\"><tei:p>This pointer pattern extracts book</tei:p></tei:cRefPattern>"
        )
        b = Citation(name="chapter", xpath="/tei:div[@n=\"?\"]", scope="/tei:TEI/tei:body/tei:text/tei:div/tei:div[@n=\"?\"]")
        self.assertEqual(
            str(b),"<tei:cRefPattern n=\"chapter\" matchPattern=\"(\\w+)\.(\\w+)\" replacementPattern=\"#xpath(/tei:TEI/tei:body/tei:text/tei:div/tei:div[@n=\"$1\"]/tei:div[@n=\"$2\"])\"><tei:p>This pointer pattern extracts chapter</tei:p></tei:cRefPattern>"
        )
        a = Citation()
        self.assertEqual(str(a), "")

    def test_ingest_none(self):
        """ When list of node is empty or when not a list nor a node """
        a = Citation.ingest([])
        self.assertEqual(a, None)
        a = Citation.ingest({})
        self.assertEqual(a, None)

    def test_ingest_multiple(self):
        b = xmlparser("""
<tei:tei xmlns:tei="http://www.tei-c.org/ns/1.0">
<tei:cRefPattern n="line"
             matchPattern="(\\w+).(\\w+).(\\w+)"
             replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1' and @type='section']/tei:div[@n='$2']/tei:l[@n='$3'])">
    <tei:p>This pointer pattern extracts line</tei:p>
</tei:cRefPattern>
<tei:cRefPattern n="poem"
             matchPattern="(\\w+).(\\w+)"
             replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']/tei:div[@n='$2'])">
    <tei:p>This pointer pattern extracts poem</tei:p>
</tei:cRefPattern>
<tei:cRefPattern n="book"
             matchPattern="(\\w+)"
             replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1'])">
    <tei:p>This pointer pattern extracts book</tei:p>
</tei:cRefPattern>
</tei:tei>
""".replace("\n", "").replace("\s+", " "))

        a = Citation.ingest(b)

        self.assertEqual(
            str(a),
            """<tei:cRefPattern n="book" matchPattern="(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\'$1\'])"><tei:p>This pointer pattern extracts book</tei:p></tei:cRefPattern>"""
        )
        self.assertEqual(
            str(a.child),
            """<tei:cRefPattern n="poem" matchPattern="(\\w+)\.(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\'$1\']/tei:div[@n=\'$2\'])"><tei:p>This pointer pattern extracts poem</tei:p></tei:cRefPattern>"""
        )
        self.assertEqual(
            str(a.child.child),
            """<tei:cRefPattern n="line" matchPattern="(\\w+)\.(\\w+)\.(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\'$1\' and @type=\'section\']/tei:div[@n=\'$2\']/tei:l[@n=\'$3\'])"><tei:p>This pointer pattern extracts line</tei:p></tei:cRefPattern>"""
        )
        self.assertEqual(
            a.child.child.fill(Reference("1.2.3")),
            "/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\'1\' and @type=\'section\']/tei:div[@n=\'2\']/tei:l[@n=\'3\']"
        )

    def test_ingest_single(self):
        b = xmlparser("""
<tei:tei xmlns:tei="http://www.tei-c.org/ns/1.0">
<tei:cRefPattern n="line"
             matchPattern="(\\w+).(\\w+).(\\w+)"
             replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']/tei:div[@n='$2']/tei:l[@n='$3'])">
    <tei:p>This pointer pattern extracts book and poem and line</tei:p>
</tei:cRefPattern>
</tei:tei>
""".replace("\n", "").replace("\s+", " "))
        a = Citation.ingest(b)

        self.assertEqual(
            str(a),
            """<tei:cRefPattern n="line" matchPattern="(\\w+)\.(\\w+)\.(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\'$1\']/tei:div[@n=\'$2\']/tei:l[@n=\'$3\'])"><tei:p>This pointer pattern extracts line</tei:p></tei:cRefPattern>"""
        )

    def test_ingest_single_and(self):
        text = xmlparser("""
<tei:tei xmlns:tei="http://www.tei-c.org/ns/1.0">
    <tei:cRefPattern n="section" matchPattern="(.+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div[@type='edition']/tei:div[@n='$1' and @type='section'])" />
</tei:tei>
""".replace("\n", "").replace("\s+", " "))
        citation = Citation.ingest(text)
        self.maxDiff = None
        self.assertEqual(
            str(citation),
            """<tei:cRefPattern n="section" matchPattern="(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div[@type='edition']/tei:div[@n=\'$1\' and @type='section'])"><tei:p>This pointer pattern extracts section</tei:p></tei:cRefPattern>"""
        )
        self.assertEqual(citation.scope, "/tei:TEI/tei:text/tei:body/tei:div[@type='edition']")
        self.assertEqual(citation.xpath, "/tei:div[@n='?' and @type='section']")
        self.assertEqual(citation.fill("1"), "/tei:TEI/tei:text/tei:body/tei:div[@type='edition']/tei:div[@n=\'1\' and @type='section']")


class TestTEIPassage(unittest.TestCase):
    def test_text(self):
        """ Test text attribute """
        P = Passage(resource=xmlparser('<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>'))
        # Without exclusion0
        self.assertEqual(P.text(), "Ibis hello b ab excusso missus in astra sago. ")
        # With Exclusion
        self.assertEqual(P.text(exclude=["note"]), "Ibis ab excusso missus in astra sago. ")

    def test_str(self):
        """ Test STR conversion of xml """
        P = Passage(resource=xmlparser('<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>'))
        self.assertEqual(str(P), '<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>')

    def test_xml(self):
        X = xmlparser('<l n="8">Ibis <note>hello<a>b</a></note> ab excusso missus in astra <hi>sago.</hi> </l>')
        P = Passage(resource=X)
        self.assertIs(X, P.xml)
