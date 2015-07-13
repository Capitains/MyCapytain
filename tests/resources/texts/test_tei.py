# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str

from MyCapytain.resources.texts.tei import *


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