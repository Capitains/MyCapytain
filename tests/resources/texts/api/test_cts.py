# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from six import text_type as str
from io import open

from MyCapytain.resources.texts.api.cts import Passage, Text
from MyCapytain.retrievers.cts5 import CTS
from MyCapytain.common.reference import Reference, Citation, URN
from MyCapytain.common.metadata import Metadata
from MyCapytain.common.utils import xmlparser
from MyCapytain.common.constants import NS, Mimetypes, NAMESPACES
from MyCapytain.errors import MissingAttribute
import mock

with open("tests/testing_data/cts/getValidReff.xml") as f:
    GET_VALID_REFF = xmlparser(f)
with open("tests/testing_data/cts/getpassage.xml") as f:
    GET_PASSAGE = xmlparser(f)
with open("tests/testing_data/cts/getpassageplus.xml") as f:
    GET_PASSAGE_PLUS = xmlparser(f)
with open("tests/testing_data/cts/getprevnexturn.xml") as f:
    NEXT_PREV = xmlparser(f)
with open("tests/testing_data/cts/getFirstUrn.xml") as f:
    Get_FIRST = xmlparser(f)
with open("tests/testing_data/cts/getFirstUrnEmpty.xml") as f:
    Get_FIRST_EMPTY = xmlparser(f)
with open("tests/testing_data/cts/getlabel.xml") as f:
    GET_LABEL = xmlparser(f)
with open("tests/testing_data/cts/getValidReff.1.1.xml") as f:
    GET_VALID_REFF_1_1 = xmlparser(f)


class TestAPIText(unittest.TestCase):
    """ Test CTS API implementation of PrototypeText
    """
    def setUp(self):
        a = Citation(
            name="line",
            refsDecl="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1' and @type='section']/tei:div[@n='$2']/tei:l[@n='$3']"
        )
        b = Citation(
            name="poem",
            child=a,
            refsDecl="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1' and @type='section']/tei:div[@n='$2']"
        )
        self.citation = Citation(
            name="book",
            child=b,
            refsDecl="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1' and @type='section']"
        )
        self.endpoint = CTS("http://services.perseids.org/api/cts")

    def test_init(self):
        """ Test the __init__ parameters of PrototypeText
        """
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)
        with self.assertRaises(MissingAttribute):
            Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=None)
        self.assertEqual(str(text.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(text.retriever, self.endpoint)
        self.assertEqual(text.citation, self.citation)

        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation,
                    metadata=Metadata(keys=["testing_init"]))
        self.assertIsInstance(text.metadata.metadata["testing_init"], Metadatum)

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
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
        self.assertEqual(reffs[0], "1.pr.1")

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_export_fulltext(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)
        requests.return_value.text = GET_PASSAGE

        # Test with -1
        export = text.export(Mimetypes.PYTHON.ETREE)
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            }
        )
        self.assertEqual(
            export.xpath(".//tei[@n='1']/text()", magic_string=False),
            [],
            "Export should be used correctly"
        )

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_getpassage_variabletypes(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)
        requests.return_value.text = GET_PASSAGE

        # Test with -1
        _ = text.getTextualNode(subreference=Reference("1.1"))
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
            }
        )
        # Test with -1
        _ = text.getTextualNode(subreference=URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.2"))
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.2"
            }
        )
        # Test with -1
        _ = text.getTextualNode(subreference=["1", "1", "1"])
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.1"
            }
        )

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_getpassage(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)
        requests.return_value.text = GET_PASSAGE

        # Test with -1
        passage = text.getTextualNode(subreference="1.1")
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
        passage = text.getTextualNode()
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            }
        )

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
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

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_get_prev_next_urn(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=self.endpoint)
        requests.return_value.text = NEXT_PREV
        _prev, _next = text.getPrevNextUrn("1.1")
        self.assertEqual(_prev, "1.pr", "Endpoint should be called and URN should be parsed")
        self.assertEqual(_next, "1.2", "Endpoint should be called and URN should be parsed")

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_first_urn(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=self.endpoint)
        requests.return_value.text = Get_FIRST
        first = text.getFirstUrn()
        self.assertEqual(
            str(first), "1.pr",
            "Endpoint should be called and URN should be parsed"
        )
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetFirstUrn",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            }
        )

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_first_urn_when_empty(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=self.endpoint)
        requests.return_value.text = Get_FIRST_EMPTY
        first = text.getFirstUrn()
        self.assertEqual(
            first, None,
            "Endpoint should be called and none should be returned if there is none"
        )
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetFirstUrn",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            }
        )

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_init_without_citation(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=self.endpoint)
        requests.return_value.text = GET_PASSAGE

        # Test with -1
        text.getTextualNode(subreference="1.1")
        requests.assert_called_with(
            "http://services.perseids.org/api/cts",
            params={
                "request": "GetPassage",
                "urn": "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
            }
        )
        self.assertEqual(text.citation.name, "book")

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_getLabel(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=self.endpoint)
        requests.return_value.text = GET_LABEL

        collection = text.getLabel()
        self.assertEqual(str(collection.metadata.get(NAMESPACES.CTS.label, "eng")), "Epigrammata")

    @mock.patch("MyCapytain.retrievers.cts5.requests.get", create=True)
    def test_reffs(self, requests):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=self.endpoint, citation=self.citation)
        requests.side_effect = [
            mock.Mock(text=GET_VALID_REFF),
            mock.Mock(text=GET_VALID_REFF),
            mock.Mock(text=GET_VALID_REFF)
        ]

        reffs = text.reffs
        self.assertEqual(len(requests.mock_calls), 3)
        requests.assert_called_with(
            'http://services.perseids.org/api/cts',
            params={'urn': 'urn:cts:latinLit:phi1294.phi002.perseus-lat2', 'request': 'GetValidReff', 'level': '3'}
        )
        # And when no citation length
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat3", retriever=self.endpoint)
        requests.side_effect = [
            mock.Mock(text=GET_LABEL),
            mock.Mock(text=GET_VALID_REFF),
            mock.Mock(text=GET_VALID_REFF),
            mock.Mock(text=GET_VALID_REFF)
        ]
        reffs = text.reffs
        self.assertEqual(len(requests.mock_calls), 7)
        requests.assert_called_with(
            'http://services.perseids.org/api/cts',
            params={'urn': 'urn:cts:latinLit:phi1294.phi002.perseus-lat3', 'request': 'GetValidReff', 'level': '3'}
        )

    def test_siblings_raise(self):
        text = Text(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            retriever=self.endpoint
        )
        with self.assertRaises(NotImplementedError):
            text.prev
        with self.assertRaises(NotImplementedError):
            text.prevId
        with self.assertRaises(NotImplementedError):
            text.siblingsId
        with self.assertRaises(NotImplementedError):
            text.next
        with self.assertRaises(NotImplementedError):
            text.nextId

    def test_get_first(self):
        self.endpoint.getPassage = mock.MagicMock(return_value=GET_PASSAGE)
        self.endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        passage = Text(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            retriever=self.endpoint
        )

        # When next does not exist from the original resource
        first = passage.first
        self.endpoint.getFirstUrn.assert_called_with("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.endpoint.getPassage.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr")
        self.assertEqual(first.xml, GET_PASSAGE.xpath("//tei:TEI", namespaces=NS)[0])
        self.assertIsInstance(first, Passage)

    def test_get_first_id(self):
        self.endpoint.getPassage = mock.MagicMock(return_value=GET_PASSAGE)
        self.endpoint.getPrevNextUrn = mock.MagicMock(return_value=NEXT_PREV)
        self.endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF_1_1)
        passage = Text(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            retriever=self.endpoint
        )

        # When next does not exist from the original resource
        self.assertEqual(
            str(passage.firstId), "1.pr",
            "FirstId should resolve"
        )

    def test_get_siblings(self):
        self.endpoint.getPassage = mock.MagicMock(return_value=GET_PASSAGE)
        self.endpoint.getPrevNextUrn = mock.MagicMock(return_value=NEXT_PREV)
        self.endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF_1_1)
        text = Text(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            retriever=self.endpoint
        )
        passage = text.getTextualNode("1.1")
        self.assertEqual(
            passage.siblingsId, ("1.pr", "1.2"),
            "SiblingsId should resolve"
        )

        # When next does not exist from the original resource
        self.endpoint.getPrevNextUrn.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        )

    def test_get_last_id(self):
        self.endpoint.getPassage = mock.MagicMock(return_value=GET_PASSAGE)
        self.endpoint.getPrevNextUrn = mock.MagicMock(return_value=NEXT_PREV)
        self.endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF_1_1)
        passage = Text(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            retriever=self.endpoint
        )

        # When next does not exist from the original resource
        self.assertEqual(
            str(passage.lastId), "1.1.6",
            "FirstId should resolve"
        )

    def test_child_id(self):
        """ Test next property, given that next information already exists or not)
        """
        self.endpoint.getPassage = mock.MagicMock(return_value=GET_PASSAGE)
        self.endpoint.getPrevNextUrn = mock.MagicMock(return_value=NEXT_PREV)
        self.endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF_1_1)
        passage = Text(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            retriever=self.endpoint
        )

        self.assertEqual(
            passage.childIds,
            [
                "1.1.1",
                "1.1.2",
                "1.1.3",
                "1.1.4",
                "1.1.5",
                "1.1.6"
            ],
            "ChildIds should resolve"
        )

    def test_children(self):
        """ Test next property, given that next information already exists or not)
        """

        self.endpoint.getPassage = mock.MagicMock(return_value=GET_PASSAGE)
        self.endpoint.getPrevNextUrn = mock.MagicMock(return_value=NEXT_PREV)
        self.endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF_1_1)
        passage = Text(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            retriever=self.endpoint
        )

        self.assertEqual(len(list(passage.children)), 6)
        self.assertEqual(
            [str(x.urn) for x in passage.children],
            [
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.1",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.2",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.3",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.4",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.5",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.6"
            ],
            "Passage should be retrieved and have the correct URN"
        )


class TestCTSPassage(unittest.TestCase):
    """ Test CTS API implementation of PrototypeText
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
        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF)
        self.endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        self.text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", self.endpoint, citation=self.citation)

    def test_next_getprevnext(self):
        """ Test next property, given that next information already exists or not)
        """

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
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
            retriever=self.endpoint
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
            retriever=self.endpoint
        )

        # When next does not exist from the original resource
        __prev = passage.prev
        self.endpoint.getPrevNextUrn.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
        self.endpoint.getPassage.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr")
        self.assertEqual(__prev.xml, GET_PASSAGE.xpath("//tei:TEI", namespaces=NS)[0])
        self.assertIsInstance(__prev, Passage)

    def test_prev_prev_next_property(self):
        """ Test reference property
        As of 0.1.0, .next and prev are URNs
        """
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        # When next does not exist from the original resource
        self.assertEqual(passage.prevId, "1.pr")
        self.assertEqual(passage.nextId, "1.2")
        self.assertEqual(passage.siblingsId, ("1.pr", "1.2"))
        self.endpoint.getPrevNextUrn.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")

    def test_prev_resource(self):
        """ Test next property, given that next information already exists
        """
        # Now with a resource containing prevnext

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE_PLUS,
            retriever=self.endpoint
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
            retriever=self.endpoint
        )

        self.assertIn("لا یا ایها الساقی ادر کاسا و ناولها ###", passage.text)

    def test_first_urn(self):
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=self.endpoint)
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )
        self.assertEqual(
            passage.firstId, "1.pr",
            "Endpoint should be called and URN should be parsed"
        )
        self.endpoint.getFirstUrn.assert_called_with(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1"
        )

    def test_get_first(self):
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        # When next does not exist from the original resource
        first = passage.first
        self.endpoint.getFirstUrn.assert_called_with("urn:cts:latinLit:phi1294.phi002.perseus-lat2:1")
        self.endpoint.getPassage.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr")
        self.assertEqual(first.xml, GET_PASSAGE.xpath("//tei:TEI", namespaces=NS)[0])
        self.assertIsInstance(first, Passage)

    def test_get_first_id(self):
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        # When next does not exist from the original resource
        self.assertEqual(
            str(passage.firstId), "1.pr",
            "FirstId should resolve"
        )

    def test_get_last_id(self):
        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF_1_1)
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        # When next does not exist from the original resource
        self.assertEqual(
            str(passage.lastId), "1.1.6",
            "FirstId should resolve"
        )

    def test_parentId(self):
        """ Test next property, given that next information already exists or not)
        """

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        self.assertEqual(
            passage.parentId, "1",
            "ParentId should resolve"
        )
        self.assertIsInstance(
            passage.parent, Passage,
            "Parent Passage should be a passage"
        )
        self.endpoint.getPassage.assert_called_with(urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1")


    def test_prev_id(self):
        """ Test next property, given that next information already exists or not)
        """

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        self.assertEqual(
            passage.prevId, "1.pr",
            "PrevId should resolve"
        )

    def test_next_id(self):
        """ Test next property, given that next information already exists or not)
        """

        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        self.assertEqual(
            passage.nextId, "1.2",
            "NextId should resolve"
        )

    def test_child_id(self):
        """ Test next property, given that next information already exists or not)
        """

        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF_1_1)
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        self.assertEqual(
            passage.childIds,
            [
                "1.1.1",
                "1.1.2",
                "1.1.3",
                "1.1.4",
                "1.1.5",
                "1.1.6"
            ],
            "Passage should be retrieved and have the correct URN"
        )

    def test_children(self):
        """ Test next property, given that next information already exists or not)
        """

        self.endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF_1_1)
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            resource=GET_PASSAGE,
            retriever=self.endpoint
        )

        self.assertEqual(len(list(passage.children)), 6)
        self.assertEqual(
            [str(x.urn) for x in passage.children],
            [
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.1",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.2",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.3",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.4",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.5",
                "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.6"
            ],
            "FirstId should resolve"
        )

    def test_first_urn_when_empty(self):

        endpoint = CTS(self.url)
        endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST_EMPTY)
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=endpoint)
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
            resource=GET_PASSAGE,
            retriever=endpoint
        )
        first = passage.firstId
        endpoint.getFirstUrn.assert_called_with(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1"
        )
        self.assertEqual(
            first, None,
            "Endpoint should be called and none should be returned if there is none"
        )

    def test_first_urn_whenfullurn(self):
        endpoint = CTS(self.url)
        endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=endpoint)
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
            resource=GET_PASSAGE,
            retriever=endpoint
        )
        first = passage.getFirstUrn("urn:cts:latinLit:phi1294.phi02.perseus-lat2:1.1")
        endpoint.getFirstUrn.assert_called_with(
            "urn:cts:latinLit:phi1294.phi02.perseus-lat2:1.1"
        )
        self.assertEqual(
            first, "1.pr",
            "Parsing should be done and getFirstUrn should treat correctly full urn"
        )

    def test_first_urn_whenreference(self):
        endpoint = CTS(self.url)
        endpoint.getFirstUrn = mock.MagicMock(return_value=Get_FIRST)
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=endpoint)
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
            resource=GET_PASSAGE,
            retriever=endpoint
        )
        first = passage.getFirstUrn("1.1")
        endpoint.getFirstUrn.assert_called_with(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        )
        self.assertEqual(
            first, "1.pr",
            "Parsing should be done and getFirstUrn should treat correctly full urn"
        )

    def test_get_reffs_contextual(self):
        """ Ensure getReffs works with context """
        endpoint = CTS(self.url)
        endpoint.getValidReff = mock.MagicMock(return_value=GET_VALID_REFF)
        text = Text("urn:cts:latinLit:phi1294.phi002.perseus-lat2", retriever=endpoint)
        passage = Passage(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
            resource=GET_PASSAGE,
            retriever=endpoint
        )
        passage.getReffs()
        endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1",
            level=2
        )

