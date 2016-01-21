# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from MyCapytain.common.utils import *
from copy import copy


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

    def test_copy_node_without_children(self):
        node = xmlparser("<a b='foo' xmlns='http://www.tei-c.org/ns/1.0'>M<b>c</b></a>")

        no_text = copy(node)
        no_text.text = None  # Remove text
        [no_text.remove(a) for a in no_text]  # Remove nodes
        copied_node = copyNode(node)
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
        node = xmlparser("<a b='foo' xmlns='http://www.tei-c.org/ns/1.0'>M<b>c</b></a>")
        comparison = copy(node)

        copied_node = copyNode(node, children=True)
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