from .base import *
from .base import _load_mock
from MyCapytain.resources.collections.dts._resolver import PaginatedProxy


class TestHttpDtsResolverCollection(unittest.TestCase):
    def setUp(self):
        reset_graph()
        self.root_uri = "http://foobar.com/api/dts"
        self.resolver = HttpDtsResolver(self.root_uri)

    def tearDown(self):
        reset_graph()

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

    @requests_mock.mock()
    def test_simple_collection_access(self, mock_set):
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri+"/collections?id=lasciva_roma",
            text=_load_mock("collection", "example2.json"),
            complete_qs=True
        )
        collection = self.resolver.getMetadata("lasciva_roma")
        self.assertEqual(
            1, collection.size,
            "There should be 3 collections"
        )
        self.assertEqual(
            "Priapeia", str(collection["urn:cts:latinLit:phi1103.phi001"].get_label()),
            "Titles of subcollection and subcollection should be "
            "stored under their IDs"
        )
        self.assertEqual(
            ["Thibault Clérice", "http://orcid.org/0000-0003-1852-9204"],
            sorted([
                str(obj)
                for obj in collection.metadata.get(
                    URIRef("http://purl.org/dc/terms/creator")
                )
            ])
        )

    @requests_mock.mock()
    def test_simple_collection_child_interaction(self, mock_set):
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri+"/collections?id=lasciva_roma",
            text=_load_mock("collection", "example2.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri+"/collections?id=urn:cts:latinLit:phi1103.phi001",
            text=_load_mock("collection", "example3.json"),
            complete_qs=True
        )

        collection_parent = self.resolver.getMetadata("lasciva_roma")
        collection = collection_parent.children["urn:cts:latinLit:phi1103.phi001"]

        self.assertEqual(
            {key: val for key, val in collection_parent.children.items()},
            {"urn:cts:latinLit:phi1103.phi001": collection},
            "Collections should retrieve children when retrieving metadata"
        )

        self.assertEqual(
            collection.metadata.get_single("http://purl.org/dc/terms/creator", lang="eng"),
            None,
            "Unfortunately, before it's resolved, this should not be filled."
        )

        self.assertEqual(collection.size, 1, "Size is parsed through retrieve")

        collection.retrieve()

        self.assertEqual(
            str(collection.metadata.get_single("http://purl.org/dc/terms/creator", lang="eng")),
            "Anonymous",
            "Metadata has been retrieved"
        )

        self.assertEqual(
            {collection_parent}, collection.parents,
            "The collection parents should be pre-defined"
        )

    @requests_mock.mock()
    def test_paginated_member_children(self, mock_set):
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc",
            text=_load_mock("collection", "paginated/page1.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc&page=2",
            text=_load_mock("collection", "paginated/page2.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc&page=3",
            text=_load_mock("collection", "paginated/page3.json"),
            complete_qs=True
        )
        collection = self.resolver.getMetadata("urn:enc")
        # Size is computed pre-reaching pages
        self.assertEqual(
            3, collection.size,
            "There should be 3 children collection"
        )
        self.assertIsInstance(collection.children, PaginatedProxy, "Proxied object is in place")
        # Then we test the children
        self.assertEqual(
            ["urn:enc:membre1", "urn:enc:membre2", "urn:enc:membre3"],
            sorted(list(collection.children.keys())),
            "Each page should be reached when iteratin over children"
        )

        self.assertIsInstance(collection.children, dict, "Proxied object is replaced")

    @requests_mock.mock()
    def test_paginated_member_children(self, mock_set):
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc",
            text=_load_mock("collection", "paginated/page1.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc&page=2",
            text=_load_mock("collection", "paginated/page2.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc&page=3",
            text=_load_mock("collection", "paginated/page3.json"),
            complete_qs=True
        )
        collection = self.resolver.getMetadata("urn:enc")
        # Size is computed pre-reaching pages
        self.assertEqual(
            3, collection.size,
            "There should be 3 children collection"
        )
        self.assertIsInstance(collection.children, PaginatedProxy, "Proxied object is in place")
        # Then we test the children
        self.assertEqual(
            ["urn:enc:membre1", "urn:enc:membre2", "urn:enc:membre3"],
            sorted(list(collection.children.keys())),
            "Each page should be reached when iteratin over children"
        )

        self.assertIsInstance(collection.children, dict, "Proxied object is replaced")

    @requests_mock.mock()
    def test_paginated_member_parents(self, mock_set):
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc",
            text=_load_mock("collection", "paginated/parent_root.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc&nav=parents",
            text=_load_mock("collection", "paginated/page1.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc&page=2&nav=parents",
            text=_load_mock("collection", "paginated/page2.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri+"/collections?id=urn:enc&page=3&nav=parents",
            text=_load_mock("collection", "paginated/page3.json"),
            complete_qs=True
        )
        collection = self.resolver.getMetadata("urn:enc")
        # Size is computed pre-reaching pages
        self.assertEqual(
            0, collection.size,
            "There should be no children collections"
        )
        self.assertIsInstance(collection.parents, PaginatedProxy, "Proxied object is in place")
        # Then we test the children
        self.assertEqual(
            ["urn:enc:membre1", "urn:enc:membre2", "urn:enc:membre3"],
            sorted([x.id for x in collection.parents]),
            "Each page should be reached when iterating over parents"
        )

        self.assertIsInstance(collection.parents, set, "Proxied object is replaced")

    @requests_mock.mock()
    def test_readable_descendants(self, mock_set):
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri+"/collections?",
            text=_load_mock("collection", "readableDescendants/coll1.json"),
            complete_qs=True
        )

        def add_mock(mocks, id_):
            mocks.get(
                self.root_uri+"/collections?id=%2Fcoll"+id_,
                text=_load_mock("collection", "readableDescendants/coll"+id_+".json"),
                complete_qs=True
            )
        add_mock(mock_set, "1_1")
        add_mock(mock_set, "1_1_1")
        add_mock(mock_set, "1_2")
        add_mock(mock_set, "1_2_1")
        add_mock(mock_set, "1_2_2")
        add_mock(mock_set, "1_2_2_1")

        root = self.resolver.getMetadata()

        self.assertEqual(
            ["/coll1_1_1", "/coll1_2_1", "/coll1_2_2_1"],
            sorted([str(c.id) for c in root.readableDescendants]),
            "Collections should be retrieved automatically"
        )
        history = [history.url for history in mock_set.request_history]

        self.assertNotIn(
            self.root_uri+"/collections?id=%2Fcoll1_2_2_1",
            history,
            "Resource should not be parsed"
        )
