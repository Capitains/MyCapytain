import unittest
from io import open
from MyCapytain.resources.xml import *

class TestXMLImplementation(unittest.TestCase):

    """ Test XML Implementation of resources Endpoint request making """

    def setUp(self):
        self.getCapabilities = open("tests/testing_data/cts/getCapabilities.xml", "r")

    def test_xml_TextInventoryParsing(self):
        """ Tests TextInventory parses without errors """
        TI = TextInventory(resource=self.getCapabilities, id="TestInv")
        self.assertGreater(len(TI.textgroups), 0)