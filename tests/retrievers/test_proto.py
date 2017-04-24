import unittest

from MyCapytain.retrievers.prototypes import *


class TestEndpointsProto(unittest.TestCase):

    """ Testing prototypes retrievers """

    def setUp(self):
        self.cts = CtsRetriever("http://ahab.com")

    def test_raise_Cts_proto(self):
        """ Tests that methods raises NotImplementedError """
        with self.assertRaises(NotImplementedError):
            self.cts.getCapabilities("inventory")

        with self.assertRaises(NotImplementedError):
            self.cts.getValidReff("urn", "inventory")

        with self.assertRaises(NotImplementedError):
            self.cts.getPassage("urn", "inventory")

        with self.assertRaises(NotImplementedError):
            self.cts.getPassagePlus("urn", "inventory")

        with self.assertRaises(NotImplementedError):
            self.cts.getFirstUrn("urn", "inventory")

        with self.assertRaises(NotImplementedError):
            self.cts.getPrevNextUrn("urn", "inventory")

        with self.assertRaises(NotImplementedError):
            self.cts.getLabel("urn", "inventory")

    def test_raise_CitableTextServicesProto(self):
        """ Ensure nothing is implemented """
        Proto = CitableTextServiceRetriever("url")
        with self.assertRaises(NotImplementedError):
            Proto.getMetadata(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        with self.assertRaises(NotImplementedError):
            Proto.getTextualNode(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        with self.assertRaises(NotImplementedError):
            Proto.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        with self.assertRaises(NotImplementedError):
            Proto.getSiblings(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1")

    def test_raise_Cts_getCapabilities_arguments(self):
        """ Tests that methods getCapabilities have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getCapabilities(inventory="inventory")

    def test_raise_Cts_getValidReff_arguments(self):
        """ Tests that methods getValidReff have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getValidReff(urn="urn", inventory="inventory", level=1)

    def test_raise_Cts_getPassage_arguments(self):
        """ Tests that methods getPassage have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getPassage(urn="urn", inventory="inventory", context=1)

    def test_raise_Cts_getPassagePlus_arguments(self):
        """ Tests that methods getPassagePlus have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getPassagePlus(urn="urn", inventory="inventory", context=1)

    def test_raise_Cts_getFirstUrn_arguments(self):
        """ Tests that methods getFirstUrn have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getFirstUrn(urn="urn", inventory="inventory")

    def test_raise_Cts_getPrevNextUrn_arguments(self):
        """ Tests that methods getPrevNextUrn have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getPrevNextUrn(urn="urn", inventory="inventory")

    def test_raise_Cts_getLabel_arguments(self):
        """ Tests that methods getLabel have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getLabel(urn="urn", inventory="inventory")


if __name__ == '__main__':
    unittest.main()
