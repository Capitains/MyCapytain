from .base import *
from .base import _load_mock, _load_json_mock


class TestHttpDtsResolverCollection(unittest.TestCase):
    def setUp(self):
        self.root_uri = "http://foobar.com/api/dts"
        self.resolver = HttpDtsResolver(self.root_uri)

    @requests_mock.mock()
    def test_simple_root_access(self, mock_set):
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri+"/collections",
            text=_load_mock("collection", "example1.json"),
            complete_qs=True
        )
        collection = self.resolver.getMetadata()
        self.assertEqual(
            3, collection.size,
            "There should be 3 collections"
        )
        self.assertEqual(
            "Cartulaires", str(collection["/cartulaires"].get_label()),
            "Titles of subcollection and subcollection should be "
            "stored under their IDs"
        )
        self.assertEqual(
            "Collection Générale de l'École Nationale des Chartes",
            str(collection.get_label()),
            "Label of the main collection should be correctly parsed"
        )
        self.assertEqual(
            ["https://viaf.org/viaf/167874585", "École Nationale des Chartes"],
            sorted([
                str(obj)
                for obj in collection.metadata.get(
                    URIRef("http://purl.org/dc/terms/publisher")
                )
            ])
        )
