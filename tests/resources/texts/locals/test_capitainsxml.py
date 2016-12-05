# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from io import open

import xmlunittest
from lxml import etree

import MyCapytain.common.reference
import MyCapytain.common.utils
import MyCapytain.errors
import MyCapytain.resources.texts.encodings
import MyCapytain.resources.texts.locals.tei
from tests.resources.commonTests import CapitainsXmlTextTest, CapitainsXmlPassageTests, CapitainsXMLRangePassageTests


class TestLocalXMLTextImplementation(CapitainsXmlTextTest, unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test XML Implementation of resources found in local file """

    def setUp(self):
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.locals.tei.Text(
            resource=self.text,
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
        )
        self.treeroot = etree._ElementTree()

        with open("tests/testing_data/texts/text_or_xpath.xml") as f:
            self.text_complex = MyCapytain.resources.texts.locals.tei.Text(
                resource=f,
                urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            )

        with open("tests/testing_data/texts/seneca.xml") as f:
            self.seneca = MyCapytain.resources.texts.locals.tei.Text(
                resource=f
            )

    def tearDown(self):
        self.text.close()


class TestLocalXMLPassageImplementation(CapitainsXmlPassageTests, unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test passage implementation """
    simple = False

    def setUp(self):
        self.URN = MyCapytain.common.reference.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.URN_2 = MyCapytain.common.reference.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat3")
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.locals.tei.Text(resource=self.text)

        assert self.simple is False, "Simple should be False"

    def tearDown(self):
        self.text.close()


class TestLocalXMLSimplePassageImplementation(CapitainsXmlPassageTests, unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test passage implementation """
    simple = True

    def setUp(self):
        self.URN = MyCapytain.common.reference.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.URN_2 = MyCapytain.common.reference.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat3")
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.locals.tei.Text(resource=self.text)

        assert self.simple is True, "Simple should be True"

    def tearDown(self):
        self.text.close()


class TestPassageRange(CapitainsXMLRangePassageTests, unittest.TestCase):
    def setUp(self):
        with open("tests/testing_data/texts/sample.xml", "rb") as text:
            self.text = MyCapytain.resources.texts.locals.tei.Text(
                resource=text, urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            )
        self.passage = self.text.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.pr.7"))
