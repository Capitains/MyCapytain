from MyCapytain.resources.collections.dts import DTSCollection
from MyCapytain.common.constants import Mimetypes, set_graph, bind_graph
from unittest import TestCase
import json


class TestDtsCollection(TestCase):
    def setUp(self):
        # The following line ensure that graphs care cleared between tests
        set_graph(bind_graph())

    def get_collection(self, number):
        """ Get a collection for tests

       :param number: ID of the test collection
       :return: JSON of the test collection as Python object
        """
        with open("tests/testing_data/dts/collection_{}.json".format(number)) as f:
            collection = json.load(f)
        return collection

    def reorder_orderable(self, exported):
        """ Reorded orderable keys

       :param exported: Exported Collection to DTS
       :return: Sorted exported collection
        """
        if "member" in exported:
            exported["member"] = sorted(exported["member"], key=lambda x: x["@id"])
        for key, values in exported.get("dts:dublincore", {}).items():
            if isinstance(values, list) and isinstance(values[0], str):
                exported["dts:dublincore"][key] = sorted(values)
            elif isinstance(values, list) and isinstance(values[0], dict):
                exported["dts:dublincore"][key] = sorted(values, key=lambda x: x["@value"])
        return exported

    def test_simple_collection(self):
        coll = self.get_collection(1)
        parsed = DTSCollection.parse(coll)
        exported = self.reorder_orderable(parsed.export(Mimetypes.JSON.DTS.Std))

        self.assertEqual(
            exported,
            {
                '@context': {
                    'dct': 'http://purl.org/dc/terms/',
                    'dts': 'https://w3id.org/dts/api#',
                    '@vocab': 'https://www.w3.org/ns/hydra/core#',
                    'skos': 'http://www.w3.org/2004/02/skos/core#'},
                '@id': 'general',
                '@type': 'Collection',
                'member': [
                    {'@id': '/cartulaires',
                     '@type': 'Collection',
                     'totalItems': 1,
                     'description': 'Collection de cartulaires '
                                          "d'Île-de-France et de ses "
                                          'environs',
                     'title': 'Cartulaires'},
                    {'@id': '/lasciva_roma',
                     '@type': 'Collection',
                     'totalItems': 1,
                     'description': 'Collection of primary '
                                          'sources of interest in the '
                                          "studies of Ancient World's "
                                          'sexuality',
                     'title': 'Lasciva Roma'},
                    {'@id': '/lettres_de_poilus',
                                 '@type': 'Collection',
                                 'totalItems': 1,
                                 'description': 'Collection de lettres de '
                                                      'poilus entre 1917 et 1918',
                                 'title': 'Correspondance des poilus'}],
                'totalItems': 3,
                'title': "Collection Générale de l'École Nationale des "
                               'Chartes',
                'dts:dublincore': {'dct:publisher': ['https://viaf.org/viaf/167874585',
                                                     'École Nationale des Chartes'],
                                    'dct:title': [{'@language': 'fre',
                                                  '@value': "Collection Générale de l'École "
                                                            'Nationale des Chartes'}]},
                'dts:extensions': {'skos:prefLabel': "Collection Générale de l'École "
                                                      'Nationale des Chartes'}
            }
        )

    def test_collection_single_member_with_types(self):
        coll = self.get_collection(2)
        parsed = DTSCollection.parse(coll)
        exported = self.reorder_orderable(parsed.export(Mimetypes.JSON.DTS.Std))
        self.assertEqual(
            exported,
            {
                "@context": {
                    'dct': 'http://purl.org/dc/terms/',
                    'dts': 'https://w3id.org/dts/api#',
                    '@vocab': 'https://www.w3.org/ns/hydra/core#',
                    'skos': 'http://www.w3.org/2004/02/skos/core#'
                },
                "@id": "lasciva_roma",
                "@type": "Collection",
                "totalItems": 2,
                "title": "Lasciva Roma",
                "description": "Collection of primary sources of interest in the studies of Ancient World's sexuality",
                "dts:dublincore": {
                    "dct:creator": [
                        "Thibault Clérice", "http://orcid.org/0000-0003-1852-9204"
                    ],
                    "dct:title": [
                        {"@language": "lat", "@value": "Lasciva Roma"}
                    ],
                    "dct:description": [
                        {
                            "@language": "eng",
                            "@value": "Collection of primary sources of interest in "
                                      "the studies of Ancient World's sexuality"
                        }
                    ]
                },
                'dts:extensions': {'skos:prefLabel': 'Lasciva Roma'},
                "member": [
                    {
                        "@id": "urn:cts:latinLit:phi1103.phi001",
                        "title": "Priapeia",
                        "@type": "Collection",
                        "totalItems": 1
                    }
                ]
            }
        )

    def test_collection_with_complex_child(self):
        coll = self.get_collection(3)
        parsed = DTSCollection.parse(coll)
        exported = self.reorder_orderable(parsed.export(Mimetypes.JSON.DTS.Std))
        self.assertEqual(
            exported,
            {
                "@context": {
                    'dct': 'http://purl.org/dc/terms/',
                    'dts': 'https://w3id.org/dts/api#',
                    '@vocab': 'https://www.w3.org/ns/hydra/core#',
                    'skos': 'http://www.w3.org/2004/02/skos/core#'
                },
                "@id": "urn:cts:latinLit:phi1103.phi001",
                "@type": "Collection",
                "title": "Priapeia",
                "dts:dublincore": {
                    "dct:type": "http://chs.harvard.edu/xmlns/cts#work",
                    "dct:creator": [
                        {"@language": "eng", "@value": "Anonymous"}
                    ],
                    "dct:language": ["eng", "lat"],
                    "dct:title": [{"@language": "lat", "@value": "Priapeia"}],
                    "dct:description": [{
                       "@language": "eng",
                       "@value": "Anonymous lascivious Poems "
                    }]
                },
                'dts:extensions': {'skos:prefLabel': 'Priapeia'},
                "totalItems": 1,
                "member": [{
                        "@id": "urn:cts:latinLit:phi1103.phi001.lascivaroma-lat1",
                        "@type": "Resource",
                        "title": "Priapeia",
                        "description": "Priapeia based on the edition of Aemilius Baehrens",
                        "totalItems": 0
                 }]
            }
        )

        # The child_collection should be equal to the collection 4 with the fixed @context
        coll_4 = self.get_collection(4)
        coll_4["@context"] = {
            'dct': 'http://purl.org/dc/terms/',
            'dts': 'https://w3id.org/dts/api#',
            '@vocab': 'https://www.w3.org/ns/hydra/core#',
            'skos': 'http://www.w3.org/2004/02/skos/core#'
        }
        # Not supported at the moment
        del coll_4["dts:passage"]
        del coll_4["dts:references"]
        del coll_4["dts:download"]

        coll_4['dts:extensions'] = {'skos:prefLabel': 'Priapeia'}

        child_collection = parsed.members[0]
        child_collection_exported = self.reorder_orderable(child_collection.export(Mimetypes.JSON.DTS.Std))
        self.assertEqual(
            self.reorder_orderable(coll_4),
            child_collection_exported
        )

    def test_collection_with_cite_depth_but_no_structure(self):
        coll = self.get_collection(5)
        parsed = DTSCollection.parse(coll)
        exported = self.reorder_orderable(parsed.export(Mimetypes.JSON.DTS.Std))
        self.assertEqual(exported["dts:citeDepth"], 7, "There should be a cite depth property")
        self.assertNotIn("dts:citeStructure", exported, "CiteStructure was not defined")
