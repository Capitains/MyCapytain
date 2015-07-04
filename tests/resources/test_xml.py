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
        print(len(tx.parents))
        self.assertEqual(tx[3], TI)


