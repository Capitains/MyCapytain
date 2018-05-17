import unittest

import responses

from MyCapytain.retrievers.dts import HttpDtsRetriever
from MyCapytain.common.utils import _Navigation
from urllib.parse import parse_qs, urlparse, urljoin


_SERVER_URI = "http://domainname.com/api/dts/"
patch_args = ("MyCapytain.retrievers.dts.requests.get", )


class TestDtsParsing(unittest.TestCase):
    """ Test Cts5 Endpoint request making """

    def setUp(self):
        self.cli = HttpDtsRetriever(_SERVER_URI)

    @property
    def calls(self):
        return list([
            (
                urljoin(
                    _SERVER_URI,
                    urlparse(call.request.url).path
                ),
                parse_qs(urlparse(call.request.url).query)
            )
            for call in responses.calls
        ])

    def assertInCalls(self, uri, qs=None, index=None):
        """ Asserts that URI and QueryString have been contacted"""
        if index:
            called_uri, called_qs = self.calls[index]
            self.assertEqual(called_uri, uri)
            self.assertEqual(called_qs, qs)
            return
        self.assertIn(
            (uri, qs), self.calls
        )

    @staticmethod
    def add_index_response():
        """ Add a simple index response for the dynamic routing """
        responses.add(
            responses.GET, _SERVER_URI,
            json={
              "@context": "/dts/api/contexts/EntryPoint.jsonld",
              "@id": "/dts/api/",
              "@type": "EntryPoint",
              "collections": "./collections/",
              "documents": "./documents/",
              "navigation": "./navigation"
            }
        )

    @staticmethod
    def add_index_with_query_string_response():
        """ Add an index response which contains URI using Query String """
        responses.add(
            responses.GET, _SERVER_URI,
            json={
              "@context": "/dts/api/contexts/EntryPoint.jsonld",
              "@id": "/dts/api/",
              "@type": "EntryPoint",
              "collections": "?api=collections",
              "documents": "?api=documents",
              "navigation": "?api=navigation"
            }
        )

    @staticmethod
    def add_collection_response(uri=None):
        """ Adds a collection response to the given URI """
        if uri is None:
            uri = _SERVER_URI+"collections/?nav=children"
        responses.add(
            responses.GET, uri,
            json={
                "@context": {
                    "@base": "http://www.w3.org/ns/hydra/context.jsonld",
                    "dct": "http://purl.org/dc/terms/",
                    "dts": "https://w3id.org/dts/api#",
                    "dc": "http://purl.org/dc/elements/1.1/",
                    "tei": "http://www.tei-c.org/ns/1.0",
                },
                "@id" : "lettres_de_poilus",
                "@type" : "Collection",
                "totalItems" : "10000",
                "title": "Collection Générale de l'École Nationale des Chartes",
                "dts:dublincore": {
                    "dc:publisher": ["École Nationale des Chartes", "https://viaf.org/viaf/167874585"],
                    "dc:title": [
                        {"fre" : "Collection Générale de l'École Nationale des Chartes"}
                    ]
                },
                "member": ["member 190 up to 200"],
                "view": {
                    "@id": "/api/dts/collections/?id=lettres_de_poilus&page=19",
                    "@type": "PartialCollectionView",
                    "first": "/api/dts/collections/?id=lettres_de_poilus&page=1",
                    "previous": "/api/dts/collections/?id=lettres_de_poilus&page=18",
                    "next": "/api/dts/collections/?id=lettres_de_poilus&page=20",
                    "last": "/api/dts/collections/?id=lettres_de_poilus&page=500"
                }
            },
            headers={
                "Content-Type": "application/ld+json",
                "Link": '</api/dts/collections/?id=lettres_de_poilus&page=1>; rel="first",'
                        '</api/dts/collections/?id=lettres_de_poilus&page=18>; rel="previous", '
                        '</api/dts/collections/?id=lettres_de_poilus&page=20>; rel="next", '
                        '</api/dts/collections/?id=lettres_de_poilus&page=500>; rel="last"'
            }
        )

    @responses.activate
    def test_routes(self):
        self.add_index_response()
        self.assertEqual(
            self.cli.routes["collections"].path, _SERVER_URI + "collections/"
        )
        self.assertEqual(
            self.cli.routes["documents"].path, _SERVER_URI + "documents/"
        )
        self.assertEqual(
            self.cli.routes["navigation"].path, _SERVER_URI + "navigation"
        )

    @responses.activate
    def test_get_collection_headers_parsing_and_hit(self):
        """ Check that the right URI is connected"""
        self.add_index_response()
        self.add_collection_response()

        response, pagination = self.cli.get_collection()
        self.assertEqual(
            pagination,
            _Navigation("18", "20", "500", None, "1")
        )

        self.assertInCalls(_SERVER_URI+"collections/", {"nav": ["children"]}, )

    @responses.activate
    def test_querystring_type_of_route(self):
        """ Check that routes using Query String, such as ?api=documents
        works with new parameters
        """
        self.add_index_with_query_string_response()
        self.add_collection_response(
            uri=_SERVER_URI+"?api=collections&id=Hello&page=19&nav=parents"
        )
        response, pagination = self.cli.get_collection(
            collection_id="Hello",
            nav="parents",
            page=19
        )

        self.assertEqual(
            pagination,
            _Navigation("18", "20", "500", None, "1")
        )
        self.assertInCalls(_SERVER_URI, {}, 0)
        self.assertInCalls(
            uri=_SERVER_URI,
            qs={
                "api": ["collections"],
                "id": ["Hello"],
                "page": ["19"],
                "nav": ["parents"]
            },
            index=1
        )
