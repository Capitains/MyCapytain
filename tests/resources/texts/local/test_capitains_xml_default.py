# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from io import open

import xmlunittest
from lxml import etree

import MyCapytain.common.reference
import MyCapytain.common.reference._capitains_cts
import MyCapytain.common.utils
import MyCapytain.errors
import MyCapytain.resources.texts.base.tei
import MyCapytain.resources.texts.local.capitains.cts
from tests.resources.texts.local.commonTests import CapitainsXmlTextTest, CapitainsXmlPassageTests, CapitainsXMLRangePassageTests


class TestLocalXMLTextImplementation(CapitainsXmlTextTest, unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test XML Implementation of resources found in local file """

    def setUp(self):
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(
            resource=self.text,
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
        )
        self.treeroot = etree._ElementTree()

        with open("tests/testing_data/texts/text_or_xpath.xml") as f:
            self.text_complex = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(
                resource=f,
                urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            )

        with open("tests/testing_data/texts/seneca.xml") as f:
            self.seneca = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(
                resource=f
            )

    def parse(self, file):
        with open(file) as f:
            text = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(
                resource=f
            )
        return text

    def tearDown(self):
        self.text.close()


class TestLocalXMLPassageImplementation(CapitainsXmlPassageTests, unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test passage implementation """
    simple = False

    def setUp(self):
        self.URN = MyCapytain.common.reference._capitains_cts.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.URN_2 = MyCapytain.common.reference._capitains_cts.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat3")
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(resource=self.text)
        with open("tests/testing_data/latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml", "rb") as f:
            self.FULL_EPIGRAMMATA = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(resource=f)
        assert self.simple is False, "Simple should be False"

    def tearDown(self):
        self.text.close()


class TestLocalXMLSimplePassageImplementation(CapitainsXmlPassageTests, unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test passage implementation """
    simple = True

    def setUp(self):
        self.URN = MyCapytain.common.reference._capitains_cts.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.URN_2 = MyCapytain.common.reference._capitains_cts.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat3")
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(resource=self.text)
        with open("tests/testing_data/latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml", "rb") as f:
            self.FULL_EPIGRAMMATA = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(resource=f)

        assert self.simple is True, "Simple should be True"

    def tearDown(self):
        self.text.close()


class TestPassageRange(CapitainsXMLRangePassageTests, unittest.TestCase):
    def setUp(self):
        with open("tests/testing_data/texts/sample.xml", "rb") as text:
            self.text = MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText(
                resource=text, urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            )
        self.passage = self.text.getTextualNode(MyCapytain.common.reference._capitains_cts.CtsReference("1.pr.2-1.pr.7"))
