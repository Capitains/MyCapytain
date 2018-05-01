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

    def test_parse(self):
        coll = self.get_collection(1)
        from pprint import pprint
        pprint(DTSCollection.parse(coll).export(Mimetypes.JSON.DTS.Std))
