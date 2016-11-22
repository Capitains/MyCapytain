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
import MyCapytain.resources.texts.encodings
import MyCapytain.common.reference
from MyCapytain.common.utils import Mimetypes
import MyCapytain.errors
from lxml import objectify
from tests.resources.texts.test_local import TestLocalXMLTextImplementation as TextTests
P = objectify.makeparser()


def objectifiedParser(file):
    return objectify.parse(file, parser=P)


class TestLocalXMLTextImplementation(TextTests, unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test XML Implementation of resources found in local file """

    def setUp(self):
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.Text(
            resource=objectifiedParser(self.text),
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
        )
        self.treeroot = etree._ElementTree()

        with open("tests/testing_data/texts/text_or_xpath.xml") as f:
            self.text_complex = MyCapytain.resources.texts.local.Text(
                resource=objectifiedParser(f),
                urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            )

        with open("tests/testing_data/texts/seneca.xml") as f:
            self.seneca = MyCapytain.resources.texts.local.Text(
                resource=objectifiedParser(f)
            )

    def tearDown(self):
        self.text.close()


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

        # ~Test simple set up
        a.urn = self.URN
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        # Test update on ID update
        a.reference = "1.pr.1"
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        # Should keep the ID if URN changes
        a.urn = self.URN_2
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat3:1.pr.1")
        # Test init
        a = MyCapytain.resources.texts.local.Passage(urn=self.URN)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        # Test init with id and URN
        a = MyCapytain.resources.texts.local.Passage(urn=self.URN, reference=["1", "pr", "1"])
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        # Should raise error if not URN for consistency
        with self.assertRaises(TypeError):
            a.urn = 1
        # Should work with plain text
        a = MyCapytain.resources.texts.local.Passage()
        a.urn = "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1"
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        self.assertEqual(str(a.reference), "1.pr.1")
        # This should affect id !
        # Test Id value on init
        a = MyCapytain.resources.texts.local.Passage(reference=["1", "pr", "1"])
        self.assertEqual(str(a.reference), "1.pr.1")

    def test_next(self):
        """ Test next property """
        # Normal passage checking
        # self.TEI.parse()
        p = self.TEI.getPassage(["1", "pr", "1"], simple=True)
        self.assertEqual(str(p.next.reference), "1.pr.2")

        # End of lowest level passage checking but not end of parent level
        p = self.TEI.getPassage(["1", "pr", "22"], simple=True)
        self.assertEqual(str(p.next.reference), "1.1.1")

        # End of lowest level passage and end of parent level
        p = self.TEI.getPassage(["1", "39", "8"], simple=True)
        self.assertEqual(str(p.next.reference), "2.pr.sa")

        # Last line should always be None
        p = self.TEI.getPassage(["2", "40", "8"], simple=True)
        self.assertIsNone(p.next)
        p = self.TEI.getPassage(["2", "40"], simple=True)
        self.assertIsNone(p.next)
        p = self.TEI.getPassage(["2"], simple=True)
        self.assertIsNone(p.next)

    def test_children(self):
        """ Test children property """
        # Normal children checking
        with open("tests/testing_data/texts/sample.xml", "rb") as text:
            self.TEI = MyCapytain.resources.texts.local.Text(resource=text)#, autoreffs=True)
            p = self.TEI.getPassage(["1", "pr"], simple=True)
            self.assertEqual(str(p.children["1.pr.1"].reference), "1.pr.1")

            p = self.TEI.getPassage(["1", "pr", "1"], simple=True)
            self.assertEqual(len(p.children), 0)

    def test_first(self):
        """ Test first property """
        # Test when there is one
        # self.TEI.parse()
        p = self.TEI.getPassage(["1", "pr"], simple=True)
        self.assertEqual(str(p.first.reference), "1.pr.1")
        # #And failing when no first
        p = self.TEI.getPassage(["1", "pr", "1"], simple=True)
        self.assertEqual(p.first, None)

    def test_last(self):
        """ Test last property """
        # self.TEI.parse()
        # Test when there is one
        p = self.TEI.getPassage(["1", "pr"], simple=True)
        self.assertEqual(str(p.last.reference), "1.pr.22")
        # #And failing when no last
        p = self.TEI.getPassage(["1", "pr", "1"], simple=True)
        self.assertEqual(p.last, None)

    def test_prev(self):
        """ Test prev property """
        # self.TEI.parse()
        # Normal passage checking
        p = self.TEI.getPassage(["2", "40", "8"], simple=True)
        self.assertEqual(str(p.prev.reference), "2.40.7")
        p = self.TEI.getPassage(["2", "40"], simple=True)
        self.assertEqual(str(p.prev.reference), "2.39")
        p = self.TEI.getPassage(["2"], simple=True)
        self.assertEqual(str(p.prev.reference), "1")

        # test failing passage
        p = self.TEI.getPassage(["1", "pr", "1"], simple=True)
        self.assertEqual(p.prev, None)
        p = self.TEI.getPassage(["1", "pr"], simple=True)
        self.assertEqual(p.prev, None)
        p = self.TEI.getPassage(["1"], simple=True)
        self.assertEqual(p.prev, None)

        # First child should get to parent's prev last child
        p = self.TEI.getPassage(["1", "1", "1"], simple=True)
        self.assertEqual(str(p.prev.reference), "1.pr.22")

        # Beginning of lowest level passage and beginning of parent level
        p = self.TEI.getPassage(["2", "pr", "sa"], simple=True)
        self.assertEqual(str(p.prev.reference), "1.39.8")


class TestPassageRange(unittest.TestCase):
    def setUp(self):
        with open("tests/testing_data/texts/sample.xml", "rb") as text:
            self.text = MyCapytain.resources.texts.local.Text(
                resource=text, urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            )
        self.passage = self.text.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.pr.7"))

    def test_errors(self):
        """ Ensure that some results throws errors according to some standards """
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.2-1.2")
        )
        with self.assertRaises(MyCapytain.errors.InvalidSiblingRequest, msg="Different range passage have no siblings"):
            a = DifferentRangePassage.next

        with self.assertRaises(MyCapytain.errors.InvalidSiblingRequest, msg="Different range passage have no siblings"):
            a = DifferentRangePassage.prev

    def test_prevnext_on_first_passage(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.1-1.2.1")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.2.2-1.5.2",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            DifferentRangePassage.prevId, None,
            "Prev reff should be none if we are on the first passage of the text"
        )

    def test_prevnext_on_close_to_first_passage(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.10-1.2.1")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.2.2-1.4.1",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "1.pr.1-1.pr.9",
            "Prev reff should start at the beginning of the text, no matter the length of the reference"
        )

    def test_prevnext_on_last_passage(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.39.2-2.40.8")
        )
        self.assertEqual(
            DifferentRangePassage.nextId, None,
            "Next reff should be none if we are on the last passage of the text"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "2.37.6-2.39.1",
            "Prev reff should be the same length as sibling"
        )

    def test_prevnext_on_close_to_last_passage(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.39.2-2.40.5")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "2.40.6-2.40.8",
            "Next reff should finish at the end of the text, no matter the length of the reference"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "2.37.9-2.39.1",
            "Prev reff should be the same length as sibling"
        )

    def test_prevnext(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.5-1.pr.6")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.pr.7-1.pr.8",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "1.pr.3-1.pr.4",
            "Prev reff should be the same length as sibling"
        )
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.5")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.pr.6",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "1.pr.4",
            "Prev reff should be the same length as sibling"
        )

        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.1",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            DifferentRangePassage.prevId, None,
            "Prev reff should be None when at the start"
        )

        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.40")
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "2.39",
            "Prev reff should be the same length as sibling"
        )
        self.assertEqual(
            DifferentRangePassage.nextId, None,
            "Next reff should be None when at the start"
        )

    def test_first_list(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.39")
        )
        self.assertEqual(
            str(DifferentRangePassage.firstId), "2.39.1",
            "First reff should be the first"
        )
        self.assertEqual(
            str(DifferentRangePassage.lastId), "2.39.2",
            "Last reff should be the last"
        )

        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.39-2.40")
        )
        self.assertEqual(
            str(DifferentRangePassage.firstId), "2.39.1",
            "First reff should be the first"
        )
        self.assertEqual(
            str(DifferentRangePassage.lastId), "2.40.8",
            "Last reff should be the last"
        )