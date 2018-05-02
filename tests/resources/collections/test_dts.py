from MyCapytain.resources.collections.dts import DTSCollection
from MyCapytain.common.constants import Mimetypes
from unittest import TestCase
import json


class TestDtsCollection(TestCase):

    def get_collection(self, number):
        """ Get a collection for tests

        :param number: ID of the test collection
        :return: JSON of the test collection as Python object
        """
        with open("tests/testing_data/dts/collection_{}.json".format(number)) as f:
            collection = json.load(f)
        return collection

    def test_parse_member(self):
        coll = self.get_collection(1)
        parsed = DTSCollection.parse(coll)
        exported = parsed.export(Mimetypes.JSON.DTS.Std)
        exported["dts:members"] = sorted(exported["dts:members"], key=lambda x: x["@id"])
        exported["dts:dublincore"]["dct:publisher"] = sorted(exported["dts:dublincore"]["dct:publisher"])
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
                'dts:members': [
                    {'@id': '/cartulaires',
                     '@type': 'hydra:Collection',
                     'dts:totalItems': 1,
                     'hydra:description': 'Collection de cartulaires '
                                          "d'Île-de-France et de ses "
                                          'environs',
                     'hydra:title': 'Cartulaires'},
                    {'@id': '/lasciva_roma',
                     '@type': 'hydra:Collection',
                     'dts:totalItems': 1,
                     'hydra:description': 'Collection of primary '
                                          'sources of interest in the '
                                          "studies of Ancient World's "
                                          'sexuality',
                     'hydra:title': 'Lasciva Roma'},
                    {'@id': '/lettres_de_poilus',
                                 '@type': 'hydra:Collection',
                                 'dts:totalItems': 1,
                                 'hydra:description': 'Collection de lettres de '
                                                      'poilus entre 1917 et 1918',
                                 'hydra:title': 'Correspondance des poilus'}],
                'dts:totalItems': 3,
                'hydra:title': "Collection Générale de l'École Nationale des "
                               'Chartes',
                'dts:dublincore': {'dct:publisher': ['https://viaf.org/viaf/167874585',
                                                     'École Nationale des Chartes'],
                                    'dct:title': {'@language': 'fre',
                                                  '@value': "Collection Générale de l'École "
                                                            'Nationale des Chartes'}},
                'dts:extensions': {'skos:prefLabel': "Collection Générale de l'École "
                                                      'Nationale des Chartes'}
            }
        )
