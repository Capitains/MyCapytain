import unittest
from mock import patch
from MyCapytain.endpoints.cts5 import *


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
