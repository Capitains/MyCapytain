# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str

from MyCapytain.common.utils import xmlparser
from MyCapytain.resources.texts.api import *
from MyCapytain.resources.texts.tei import Citation
from MyCapytain.endpoints.cts5 import CTS
from MyCapytain.common.reference import Reference, URN
import mock


with open("tests/testing_data/cts/getValidReff.xml") as f:
    GET_VALID_REFF = xmlparser(f)
with open("tests/testing_data/cts/getpassage.xml") as f:
    GET_PASSAGE = xmlparser(f)
with open("tests/testing_data/cts/getprevnexturn.xml") as f:
    NEXT_PREV = xmlparser(f)


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
        self.endpoint = CTS("http://services.perseids.org/api/cts")
        self.endpoint.getPassage = mock.MagicMock(return_value=GET_PASSAGE)
        self.endpoint.getPrevNextUrn = mock.MagicMock(return_value=NEXT_PREV)
        self.text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)

    def test_next(self):
        """ Test next property, given that next information already exists or not)
        """
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            parent=self.text
        )

        # When next does not exist from the original resource
        __next = passage.next
        self.endpoint.getPrevNextUrn.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
        self.endpoint.getPassage.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.2")

