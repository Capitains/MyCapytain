# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from io import open
from MyCapytain.resources.xml import *

class TestXMLImplementation(unittest.TestCase):

    """ Test XML Implementation of resources Endpoint request making """

    def setUp(self):
        self.getCapabilities = open("tests/testing_data/cts/getCapabilities.xml", "r")

    def tearDown(self):
        self.getCapabilities.close()

    def test_xml_TextInventoryParsing(self):
        """ Tests TextInventory parses without errors """
        TI = TextInventory(resource=self.getCapabilities, id="TestInv")
        self.assertGreater(len(TI.textgroups), 0)

    def test_xml_TextInventory_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI = TextInventory(resource=self.getCapabilities, id="TestInv")
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294"], TextGroup)
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294.phi002"], Work)
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002"].urn), "urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"], Text)
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")

    def test_xml_Work_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI = TextInventory(resource=self.getCapabilities, id="TestInv")
        tg = TI["urn:cts:latinLit:phi1294"]
        self.assertIsInstance(tg["urn:cts:latinLit:phi1294.phi002"], Work)
        self.assertEqual(str(tg["urn:cts:latinLit:phi1294.phi002"].urn), "urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(tg["urn:cts:latinLit:phi1294.phi002.perseus-lat2"], Text)
        self.assertEqual(str(tg["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")

    def test_get_parent(self):
        TI = TextInventory(resource=self.getCapabilities, id="TestInv")
        tg = TI["urn:cts:latinLit:phi1294"]
        wk = TI["urn:cts:latinLit:phi1294.phi002"]
        tx = TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"]
        self.assertEqual(tg[1], TI)
        self.assertEqual(wk[1], tg)
        self.assertEqual(wk[2], TI)
        self.assertEqual(tx[1], wk)
        self.assertEqual(tx[2], tg)
        self.assertEqual(tx[3], TI)

    def test_translation(self):
        TI = TextInventory(resource=self.getCapabilities, id="TestInv")
        tr = TI["urn:cts:latinLit:phi1294.phi002.perseus-eng2"]
        self.assertIsInstance(tr, Text)
        self.assertEqual(tr.subtype, "Translation")

    def test_parse_string(self):
        TI = TextInventory(
            id="TestInv",
            resource="""
<ti:TextInventory xmlns:ti="http://chs.harvard.edu/xmlns/cts" tiid="thibault3">
    <ti:textgroup urn="urn:cts:greekLit:tlg0003">
        <ti:groupname xml:lang="en">Thucydides</ti:groupname>
        <ti:groupname xml:lang="eng">Thucydides</ti:groupname>
        <ti:groupname>Thucydides</ti:groupname>
        <ti:work urn="urn:cts:greekLit:tlg0003.tlg001" xml:lang="grc">
            <ti:title xml:lang="en">The Peloponnesian War</ti:title>
            <ti:title xml:lang="eng">The Peloponnesian War</ti:title>
        </ti:work>
    </ti:textgroup>
</ti:TextInventory>
            """
        )
        self.assertEqual(str(TI["urn:cts:greekLit:tlg0003.tlg001"].urn), "urn:cts:greekLit:tlg0003.tlg001")

    def test_parse_error(self):
        with self.assertRaises(TypeError):
            TI = TextInventory(
                id="TestInv",
                resource=5
            )
