from MyCapytain.resolvers.cts.api import HttpCTSResolver
from MyCapytain.retrievers.cts5 import CTS
from MyCapytain.common.utils import xmlparser, Mimetypes, NS
from MyCapytain.resources.prototypes.text import Passage

from unittest import TestCase
from mock import MagicMock


with open("tests/testing_data/cts/getpassage.xml") as f:
    GET_PASSAGE = xmlparser(f)
with open("tests/testing_data/cts/getpassageplus.xml") as f:
    GET_PASSAGE_PLUS = xmlparser(f)
with open("tests/testing_data/cts/getprevnexturn.xml") as f:
    NEXT_PREV = xmlparser(f)
with open("tests/testing_data/cts/getValidReff.1.1.xml") as f:
    GET_VALID_REFF = xmlparser(f)
with open("tests/testing_data/cts/getCapabilities.xml") as f:
    GET_CAPABILITIES = xmlparser(f)


class TestHttpCTSResolver(TestCase):
    def setUp(self):
        self.resolver = HttpCTSResolver(CTS("http://localhost"))
        self.resolver.endpoint.getPassagePlus = MagicMock(return_value=GET_PASSAGE_PLUS)
        self.resolver.endpoint.getPassage = MagicMock(return_value=GET_PASSAGE)
        self.resolver.endpoint.getPrevNextUrn = MagicMock(return_value=NEXT_PREV)
        self.resolver.endpoint.getValidReff = MagicMock(return_value=GET_VALID_REFF)
        self.resolver.endpoint.getCapabilities = MagicMock(return_value=GET_CAPABILITIES)

    def test_getPassage_full(self):
        """ Test that we can get a full text """
        passage = self.resolver.getPassage("urn:cts:latinLit:phi1294.phi002.perseus-lat2")

        # We check we made a reroute to GetPassage request
        self.resolver.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
        )
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )

        children = list(passage.getReffs())

        # We check the passage is able to perform further requests and is well instantiated
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            level=1
        )
        self.assertEqual(
            children[0], 'urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export Text should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_subreference(self):
        """ Test that we can get a subreference text passage"""
        passage = self.resolver.getPassage("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.1")

        # We check we made a reroute to GetPassage request
        self.resolver.endpoint.getPassage.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1"
        )
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )

        children = list(passage.getReffs())

        # We check the passage is able to perform further requests and is well instantiated
        self.resolver.endpoint.getValidReff.assert_called_with(
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1",
            level=1
        )
        self.assertEqual(
            children[0], 'urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export Text should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

