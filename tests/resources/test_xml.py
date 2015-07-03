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


    def test_xml_Work_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI = TextInventory(resource=self.getCapabilities, id="TestInv")
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294"]["urn:cts:latinLit:phi1294.phi002"], Work)
