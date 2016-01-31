# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str
from io import open

from MyCapytain.common.utils import xmlparser, NS
from MyCapytain.resources.texts.api import *
from MyCapytain.resources.texts.tei import Citation
from MyCapytain.endpoints.cts5 import CTS
from MyCapytain.common.reference import Reference, URN
from lxml import etree
import mock

with open("tests/testing_data/cts/getValidReff.xml") as f:
    GET_VALID_REFF = xmlparser(f)
with open("tests/testing_data/cts/getpassage.xml") as f:
    GET_PASSAGE = xmlparser(f)
with open("tests/testing_data/cts/getpassageplus.xml") as f:
    GET_PASSAGE_PLUS = xmlparser(f)
with open("tests/testing_data/cts/getprevnexturn.xml") as f:
    NEXT_PREV = xmlparser(f)
with open("tests/testing_data/cts/getlabel.xml") as f:
    GET_LABEL = xmlparser(f)


class TestAPIText(unittest.TestCase):
    """ Test CTS API implementation of Text
    """
    def setUp(self):
        a = Citation(
            name="line"
        )
        b = Citation(
            name="poem",
            child=a
        )
        self.citation = Citation(
            name="book",
            child=b
        )
        self.endpoint = CTS("http://services.perseids.org/api/cts")

    def test_init(self):
        """ Test the __init__ parameters of Text
        """
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)
        self.assertEqual(str(text.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(text.resource, self.endpoint)
        self.assertEqual(text.citation, self.citation)

        text = Text(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            self.endpoint,
            citation=self.citation,
            metadata=MyCapytain.common.metadata.Metadata(["testing"])
        )
        self.assertIsInstance(text.metadata["testing"], MyCapytain.common.metadata.Metadatum)

    @mock.patch("MyCapytain.endpoints.cts5.requests.get", create=True)
    def test_getvalidreff(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)
        requests.return_value.text = GET_VALID_REFF

        # Test with -1
        text.getValidReff(level=-1)
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetValidReff",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
                "level": "3"
            }
        )

        # Test with level 2
        text.getValidReff(level=2)
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetValidReff",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
                "level": "2"
            }
        )

        # Test with no level
        text.getValidReff()
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetValidReff",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2",
                "level": "1"
            }
        )

        # Test with a ref as str
        text.getValidReff(reference="1.pr")
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetValidReff",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr",
                "level": "1"
            }
        )

        # Test with a ref as subreference
        reffs = text.getValidReff(reference=Reference("1.pr"))
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetValidReff",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr",
                "level": "1"
            }
        )

        # Test the parsing
        self.assertEqual(reffs[0], "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")

    @mock.patch("MyCapytain.endpoints.cts5.requests.get", create=True)
    def test_getpassage(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)
        requests.return_value.text = GET_PASSAGE

        # Test with -1
        passage = text.getPassage(reference="1.1")
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
            }
        )

        self.assertIsInstance(passage, Passage)
        self.assertEqual(str(passage.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
        self.assertEqual(
            passage.xml.findall(".//{http://www.tei-c.org/ns/1.0}l[@n='1']")[0].text,
            "Hic est quem legis ille, quem requiris, "
        )

        # Test without reference
        passage = text.getPassage()
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            }
        )

    @mock.patch("MyCapytain.endpoints.cts5.requests.get", create=True)
    def test_getpassageplus(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint)
        requests.return_value.text = GET_PASSAGE_PLUS

        # Test with -1
        passage = text.getPassagePlus(reference="1.1")
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassagePlus",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
            }
        )

        self.assertIsInstance(passage, Passage)
        self.assertEqual(str(passage.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
        self.assertEqual(
            passage.xml.findall(".//{http://www.tei-c.org/ns/1.0}l[@n='1']")[0].text,
            "Hic est quem legis ille, quem requiris, "
        )
        self.assertEqual(text.citation.name, "book")
        self.assertEqual(len(text.citation), 3)

        # Test without reference
        text.getPassagePlus()
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassagePlus",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            }
        )

    @mock.patch("MyCapytain.endpoints.cts5.requests.get", create=True)
    def test_get_prev_next_urn(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", resource=self.endpoint)
        requests.return_value.text = NEXT_PREV
        _prev, _next = text.getPrevNextUrn("1.1")
        self.assertEqual(str(_prev.reference), "1.pr", "Endpoint should be called and URN should be parsed")
        self.assertEqual(str(_next.reference), "1.2", "Endpoint should be called and URN should be parsed")

    @mock.patch("MyCapytain.endpoints.cts5.requests.get", create=True)
    def test_init_without_citation(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", resource=self.endpoint)
        requests.return_value.text = GET_PASSAGE

        # Test with -1
        text.getPassage(reference="1.1")
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
            }
        )
        self.assertEqual(text.citation.name, "book")

    @mock.patch("MyCapytain.endpoints.cts5.requests.get", create=True)
    def test_getLabel(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", resource=self.endpoint)
        requests.return_value.text = GET_LABEL

        label = text.getLabel()
        self.assertEqual(label["title"]["eng"], "Epigrammata")

    @mock.patch("MyCapytain.endpoints.cts5.requests.get", create=True)
    def test_reffs(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", citation=self.citation, resource=self.endpoint)
        requests.return_value.text = GET_VALID_REFF

        reffs = text.reffs
        self.assertEqual(len(requests.mock_calls), 3)
        requests.assert_called_with(
            'http://services.perseids.org/api/cts',
            params={'urn': 'urn:cts:latinLit:phi1294.phi002.perseus-lat2', 'request': 'GetValidReff', 'level': '3'}
        )
        # And when no citation length
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat3", resource=self.endpoint)

        reffs = text.reffs
        self.assertEqual(len(requests.mock_calls), 6)
        requests.assert_called_with(
            'http://services.perseids.org/api/cts',
            params={'urn': 'urn:cts:latinLit:phi1294.phi002.perseus-lat3', 'request': 'GetValidReff', 'level': '3'}
        )


class TestCTSPassage(unittest.TestCase):
    """ Test CTS API implementation of Text
    """

    def setUp(self):
        a = Citation(
            name="line"
        )
        b = Citation(
            name="poem",
            child=a
        )
        self.citation = Citation(
            name="book",
            child=b
        )
        self.url = "http://services.perseids.org/api/cts"
        self.endpoint = CTS(self.url)
        self.endpoint.getPassage = mock.MagicMock(return_value=GET_PASSAGE)
        self.endpoint.getPrevNextUrn = mock.MagicMock(return_value=NEXT_PREV)
        self.text = Text(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation
        )

    def test_next_getprevnext(self):
        """ Test next property, given that next information already exists or not)
        """

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            parent=self.text
        )

        # When next does not exist from the original resource
        __next = passage.next

        self.endpoint.getPrevNextUrn.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        )
        self.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.2"
        )
        self.assertEqual(__next.xml, GET_PASSAGE.xpath("//tei:TEI", namespaces=NS)[0])
        self.assertIsInstance(__next, Passage)

    def test_next_resource(self):
        """ Test next property, given that next information already exists
        """
        # Now with a resource containing prevnext

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE_PLUS,
            parent=self.text
        )

        # When next does not exist from the original resource
        __next = passage.next
        # print(self.endpoint.getPrevNextUrn.mock_calls)
        self.endpoint.getPassage.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.2")
        self.assertEqual(__next.xml, GET_PASSAGE.xpath("//tei:TEI", namespaces=NS)[0])
        self.assertIsInstance(__next, Passage)


    def test_prev_getprevnext(self):
        """ Test next property, given that next information already exists or not)
        """
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            parent=self.text
        )

        # When next does not exist from the original resource
        __prev = passage.prev
        self.endpoint.getPrevNextUrn.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
        self.endpoint.getPassage.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr")
        self.assertEqual(__prev.xml, GET_PASSAGE.xpath("//tei:TEI", namespaces=NS)[0])
        self.assertIsInstance(__prev, Passage)

    def test_prev_resource(self):
        """ Test next property, given that next information already exists
        """
        # Now with a resource containing prevnext

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE_PLUS,
            parent=self.text
        )

        # When next does not exist from the original resource
        __prev = passage.prev
        self.endpoint.getPassage.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr")
        self.assertEqual(__prev.xml, GET_PASSAGE.xpath("//tei:TEI", namespaces=NS)[0])
        self.assertIsInstance(__prev, Passage)

    def test_unicode_text(self):
        """ Test text properties for pypy
        """
        # Now with a resource containing prevnext

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            parent=self.text
        )

        self.assertIn("لا یا ایها الساقی ادر کاسا و ناولها ###", passage.text())
