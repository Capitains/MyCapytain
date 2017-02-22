# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from six import text_type as str

import unittest
from MyCapytain.common.utils import *
from copy import copy as deepcopy


class TestUtils(unittest.TestCase):

    def test_clean_xpath(self):
        """ Cleaning XPATH and normalizing them """
        l = ['tei:text', 'tei:body', 'tei:div', "tei:div[@n='1']", "tei:div[@n='pr']", "tei:l[@n='2']"]
        self.assertEqual(normalizeXpath(l), l)

        l = ['tei:text', 'tei:body', 'tei:div', "tei:div[@n='1']", "", "tei:div[@n='pr']", "tei:l[@n='2']"]
        self.assertEqual(
            normalizeXpath(l),
            ['tei:text', 'tei:body', 'tei:div', "tei:div[@n='1']", "/tei:div[@n='pr']", "tei:l[@n='2']"],
            "Empty list element should be replaced with / in the next element"
        )