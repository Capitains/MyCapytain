# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str

from MyCapytain.resources.text.tei import *


class TestTEICitation(unittest.TestCase):
    def test_str(self):
        a = Citation(name="book", xpath="/tei:TEI/tei:body/tei:text/tei:div", scope="/tei:div[@n=\"1\"]")
        self.assertEqual(
            str(a),"<tei:cRefPattern n=\"book\" matchPattern=\"(\\w+)\" replacementPattern=\"#xpath(/tei:TEI/tei:body/tei:text/tei:div/tei:div[@n=\"$1\"])\"><tei:p>This pointer pattern extracts book</tei:p></tei:cRefPattern>"
        )