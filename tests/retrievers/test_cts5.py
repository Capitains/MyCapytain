import unittest
from mock import patch
from MyCapytain.retrievers.cts5 import *


class TestEndpointsCTS5(unittest.TestCase):

    """ Test CTS5 Endpoint request making """

    def setUp(self):
        self.cts = CTS("http://domainname.com/rest/cts")

    def test_request_CTS_getCapabilities_arguments(self):
        """ Tests that methods getCapabilities maps correctly to request"""
        with patch('requests.get') as patched_get:
            self.cts.getCapabilities(inventory="inventory")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetCapabilities"
                }
            )

    def test_request_CTS_getValidReff_arguments(self):
        """ Tests that methods getValidReff maps correctly to request"""
        with patch('requests.get') as patched_get:
            self.cts.getValidReff(urn="urn", inventory="inventory", level=1)
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetValidReff",
                    "level": "1",
                    "urn": "urn"
                }
            )
        with patch('requests.get') as patched_get:
            self.cts.getValidReff(urn="urn", inventory="inventory")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetValidReff",
                    "urn": "urn"
                }
            )

    def test_request_CTS_getPassage_arguments(self):
        """ Tests that methods getPassage maps correctly to request"""
        with patch('requests.get') as patched_get:
            self.cts.getPassage(urn="urn", inventory="inventory", context=1)
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetPassage",
                    "context": "1",
                    "urn": "urn"
                }
            )
        with patch('requests.get') as patched_get:
            self.cts.getPassage(urn="urn", inventory="inventory")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetPassage",
                    "urn": "urn"
                }
            )

    def test_call_with_default(self):
        inv = CTS("http://domainname.com/rest/cts", inventory="annotsrc")
        with patch('requests.get') as patched_get:
            inv.getPassage(urn="urn")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "annotsrc",
                    "request": "GetPassage",
                    "urn": "urn"
                }
            )

    def test_request_CTS_getPassagePlus_arguments(self):
        """ Tests that methods getPassagePlus maps correctly to request"""
        with patch('requests.get') as patched_get:
            self.cts.getPassagePlus(
                urn="urn", inventory="inventory", context=1)
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetPassagePlus",
                    "context": "1",
                    "urn": "urn"
                }
            )
        with patch('requests.get') as patched_get:
            self.cts.getPassagePlus(urn="urn", inventory="inventory")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetPassagePlus",
                    "urn": "urn"
                }
            )

    def test_request_CTS_getFirstUrn_arguments(self):
        """ Tests that methods getFirstUrn maps correctly to request"""
        with patch('requests.get') as patched_get:
            self.cts.getFirstUrn(urn="urn", inventory="inventory")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetFirstUrn",
                    "urn": "urn"
                }
            )

    def test_request_CTS_getPrevNextUrn_arguments(self):
        """ Tests that methods getPrevNextUrn maps correctly to request"""
        with patch('requests.get') as patched_get:
            self.cts.getPrevNextUrn(urn="urn", inventory="inventory")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetPrevNextUrn",
                    "urn": "urn"
                }
            )

    def test_request_CTS_getLabel_arguments(self):
        """ Tests that methods getLabel maps correctly to request"""
        with patch('requests.get') as patched_get:
            self.cts.getLabel(urn="urn", inventory="inventory")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "inv": "inventory",
                    "request": "GetLabel",
                    "urn": "urn"
                }
            )

    def test_get_siblings(self):
        """ Ensure Citable Text Service getMetadata is correctly routed """
        with patch('requests.get') as patched_get:
            self.cts.getSiblings("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.1")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "request": "GetPrevNextUrn",
                    "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
                }
            )

    def test_get_children(self):
        """ Ensure Citable Text Service getMetadata is correctly routed """
        with patch('requests.get') as patched_get:
            self.cts.getChildren("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "request": "GetValidReff",
                    "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
                    "level": "1"
                }
            )
        with patch('requests.get') as patched_get:
            self.cts.getChildren("urn:cts:latinLit:phi1294.phi002.perseus-lat2", reference="1.1")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "request": "GetValidReff",
                    "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
                    "level": "3"
                }
            )

        with patch('requests.get') as patched_get:
            self.cts.getChildren("urn:cts:latinLit:phi1294.phi002.perseus-lat2", reference="1", depth=2)
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "request": "GetValidReff",
                    "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
                    "level": "3"
                }
            )

    def test_get_metadata(self):
        """ Ensure Citable Text Service getMetadata is correctly routed """
        with patch('requests.get') as patched_get:
            self.cts.getMetadata()
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "request": "GetCapabilities"
                }
            )
        with patch('requests.get') as patched_get:
            self.cts.getMetadata(objectId="urn")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "request": "GetCapabilities",
                    "urn": "urn"
                }
            )

    def test_get_text(self):
        """ Ensure Citable Text Service getText is correctly routed """
        with patch('requests.get') as patched_get:
            self.cts.getText(textId="urn", metadata=True)
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "request": "GetPassagePlus",
                    "urn": "urn"
                }
            )
        with patch('requests.get') as patched_get:
            self.cts.getText(textId="urn", reference="1.1")
            patched_get.assert_called_once_with(
                "http://domainname.com/rest/cts", params={
                    "request": "GetPassage",
                    "urn": "urn:1.1"
                }
            )