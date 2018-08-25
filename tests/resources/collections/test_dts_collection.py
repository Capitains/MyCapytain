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
        exported["hydra:member"] = sorted(exported["hydra:member"], key=lambda x: x["@id"])
        for key, values in exported["dts:dublincore"].items():
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
                    'hydra': 'https://www.w3.org/ns/hydra/core#',
                    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                    'skos': 'http://www.w3.org/2004/02/skos/core#'},
                '@id': 'general',
                '@type': 'hydra:Collection',
                'hydra:member': [
                    {'@id': '/cartulaires',
                     '@type': 'hydra:Collection',
                     'hydra:totalItems': 1,
                     'hydra:description': 'Collection de cartulaires '
                                          "d'Île-de-France et de ses "
                                          'environs',
                     'hydra:title': 'Cartulaires'},
                    {'@id': '/lasciva_roma',
                     '@type': 'hydra:Collection',
                     'hydra:totalItems': 1,
                     'hydra:description': 'Collection of primary '
                                          'sources of interest in the '
                                          "studies of Ancient World's "
                                          'sexuality',
                     'hydra:title': 'Lasciva Roma'},
                    {'@id': '/lettres_de_poilus',
                                 '@type': 'hydra:Collection',
                                 'hydra:totalItems': 1,
                                 'hydra:description': 'Collection de lettres de '
                                                      'poilus entre 1917 et 1918',
                                 'hydra:title': 'Correspondance des poilus'}],
                'hydra:totalItems': 3,
                'hydra:title': "Collection Générale de l'École Nationale des "
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
                    'hydra': 'https://www.w3.org/ns/hydra/core#',
                    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                    'skos': 'http://www.w3.org/2004/02/skos/core#'
                },
                "@id": "lasciva_roma",
                "@type": "hydra:Collection",
                "hydra:totalItems": 2,
                "hydra:title": "Lasciva Roma",
                "hydra:description": "Collection of primary sources of interest in the studies of Ancient World's sexuality",
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
                "hydra:member": [
                    {
                        "@id": "urn:cts:latinLit:phi1103.phi001",
                        "hydra:title": "Priapeia",
                        "@type": "hydra:Collection",
                        "hydra:totalItems": 1
                    }
                ]
            }
        )

    def test_collection_with_complexe_child(self):
        coll = self.get_collection(3)
        parsed = DTSCollection.parse(coll)
        exported = self.reorder_orderable(parsed.export(Mimetypes.JSON.DTS.Std))
        self.assertEqual(
            exported,
            {
                "@context": {
                    'dct': 'http://purl.org/dc/terms/',
                    'dts': 'https://w3id.org/dts/api#',
                    'hydra': 'https://www.w3.org/ns/hydra/core#',
                    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                    'skos': 'http://www.w3.org/2004/02/skos/core#',
                    #  "tei": "http://www.tei-c.org/ns/1.0"
                },
                "@id": "urn:cts:latinLit:phi1103.phi001",
                "@type": "hydra:Collection",
                "hydra:title": "Priapeia",
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
                "hydra:totalItems": 1,
                "hydra:member": [{
                        "@id": "urn:cts:latinLit:phi1103.phi001.lascivaroma-lat1",
                        "@type": "hydra:Resource",
                        "hydra:title": "Priapeia",
                        "hydra:description": "Priapeia based on the edition of Aemilius Baehrens",
                        "hydra:totalItems": 0
                 }]
            }
        )