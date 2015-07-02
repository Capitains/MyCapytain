import unittest

from MyCapytain.endpoints.proto import *


class TestEndpointsProto(unittest.TestCase):

    """ Testing prototypes endpoints """

    def setUp(self):
        self.ahab = Ahab("http://ahab.com")
        self.cts = CTS("http://ahab.com")

    def test_init_Ahab(self):
        """ Test that init register the Ahab endpoint url"""
        self.assertEqual(self.ahab.endpoint, "http://ahab.com")

    def test_raise_Ahab_proto(self):
        """ Tests that methods raises NotImplementedError """
        with self.assertRaises(NotImplementedError):
            self.ahab.search("query", "urn")

        with self.assertRaises(NotImplementedError):
            self.ahab.permalink("urn")

    def test_raise_Ahab_search_arguments(self):
        """ Tests that methods have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.ahab.search(
                query="query", urn="urn", start=1, limit=5, format="json")

    def test_raise_Ahab_permalink_arguments(self):
        """ Tests that methods have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.ahab.permalink(urn="urn", format="json")

    def test_init_CTS(self):
        """ Test that init register the CTS endpoint url"""
        self.assertEqual(self.ahab.endpoint, "http://ahab.com")

    def test_raise_CTS_proto(self):
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

    def test_raise_CTS_getCapabilities_arguments(self):
        """ Tests that methods getCapabilities have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getCapabilities(inventory="inventory")

    def test_raise_CTS_getValidReff_arguments(self):
        """ Tests that methods getValidReff have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getValidReff(urn="urn", inventory="inventory", level=1)

    def test_raise_CTS_getPassage_arguments(self):
        """ Tests that methods getPassage have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getPassage(urn="urn", inventory="inventory", context=1)

    def test_raise_CTS_getPassagePlus_arguments(self):
        """ Tests that methods getPassagePlus have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getPassagePlus(urn="urn", inventory="inventory", context=1)

    def test_raise_CTS_getFirstUrn_arguments(self):
        """ Tests that methods getFirstUrn have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getFirstUrn(urn="urn", inventory="inventory")

    def test_raise_CTS_getPrevNextUrn_arguments(self):
        """ Tests that methods getPrevNextUrn have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getPrevNextUrn(urn="urn", inventory="inventory")

    def test_raise_CTS_getLabel_arguments(self):
        """ Tests that methods getLabel have consistent arguments"""
        with self.assertRaises(NotImplementedError):
            self.cts.getLabel(urn="urn", inventory="inventory")


if __name__ == '__main__':
    unittest.main()
