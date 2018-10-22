from .base import *
from .base import _load_mock
from link_header import LinkHeader, Link


def make_links(root="http://foobar.com/api/dts", **kwargs):
    header = LinkHeader(
            [
                Link(root+"/"+val, rel=key)
                for key, val in kwargs.items()
            ]
        )
    return {
        "Link": str(header)
    }


class TestHttpDtsResolverDocument(unittest.TestCase):
    def setUp(self):
        self.root_uri = "http://foobar.com/api/dts"
        self.resolver = HttpDtsResolver(self.root_uri)

    @requests_mock.mock()
    def test_retrieve_full(self, mock_set):
        """ Grab a doc then check its metadata """
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri + "/documents?id=document_id",
            text=_load_mock("document", "example.xml"),
            complete_qs=True,
            headers=make_links(collection="/collections/?id=document_id")
        )
        mock_set.get(
            self.root_uri + "/collections?id=document_id",
            text=_load_mock("document", "collection.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri + "/navigation?groupby=1&level=1&id=document_id",
            text=_load_mock("document", "nav.json"),
            complete_qs=True
        )
        doc = self.resolver.getTextualNode(textId="document_id")
        self.assertIn(
            "Full Text", doc.export(Mimetypes.PLAINTEXT),
            "Text of the response should be exportable"
        )
        self.assertEqual(
            "document_id", doc.id, "Document ID should be set"
        )
        self.assertEqual(
            "Titulus", str(doc.get_title(lang="la")), "Titles are retrieved"
        )
        self.assertEqual(
            "Aemilius Baehrens", str(doc.metadata.get_single("http://purl.org/dc/terms/contributor")),
            "Contributor can be retrieved"
        )
        self.assertEqual(1, doc.depth, "Depth should be set up")

        self.assertEqual(
            DtsReferenceSet(
                DtsReference("1", type_="psg"),
                DtsReference("2", type_="psg"),
                DtsReference("3", type_="psg"),
                level=1,
                citation=DtsCitation(name="psg")
            ), doc.childIds, "Children IDs should be retrieved"
        )

    @requests_mock.mock()
    def test_retrieve_full_then_child(self, mock_set):
        """ Grab a doc then grab subpassages """
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri + "/documents?id=document_id",
            text=_load_mock("document", "example.xml"),
            complete_qs=True,
            headers=make_links(collection=self.root_uri+"/collections?id=document_id")
        )
        mock_set.get(
            self.root_uri + "/collections?id=document_id",
            text=_load_mock("document", "collection.json"),
            complete_qs=True
        )
        mock_set.get(
            self.root_uri + "/navigation?groupby=1&level=1&id=document_id",
            text=_load_mock("document", "nav.json"),
            complete_qs=True
        )
        # Adding child
        mock_set.get(
            self.root_uri + "/documents?id=document_id&ref=1",
            text=_load_mock("document", "sequence/passage_1.xml"),
            complete_qs=True,
            headers=make_links(
                collection=self.root_uri+"/collections?id=document_id",
                up=self.root_uri+"/document?id=document_id",
                next=self.root_uri+"/document?id=document_id&ref=2"
            )
        )
        doc = self.resolver.getTextualNode(textId="document_id")
        child = doc.getTextualNode(DtsReference("1"))
        self.assertIn(
            "Passage 1", child.export(Mimetypes.PLAINTEXT),
            "Text of the response should be exportable"
        )

    @requests_mock.mock()
    def test_retrieve_child_then_moving(self, mock_set):
        """ Retrieve child passage then checkout others by navigation using link headers"""
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri + "/documents?id=document_id",
            text=_load_mock("document", "example.xml"),
            complete_qs=True,
            headers=make_links(collection=self.root_uri+"/collections?id=document_id")
        )
        # Adding child
        mock_set.get(
            self.root_uri + "/documents?id=document_id&ref=1",
            text=_load_mock("document", "sequence/passage_1.xml"),
            complete_qs=True,
            headers=make_links(
                collection=self.root_uri+"/collections?id=document_id",
                up=self.root_uri+"/document?id=document_id",
                next=self.root_uri+"/document?id=document_id&ref=2"
            )
        )
        # Adding child
        mock_set.get(
            self.root_uri + "/documents?id=document_id&ref=2",
            text=_load_mock("document", "sequence/passage_2.xml"),
            complete_qs=True,
            headers=make_links(
                collection=self.root_uri+"/collections?id=document_id",
                up=self.root_uri+"/document?id=document_id",
                prev=self.root_uri+"/document?id=document_id&ref=1",
                next=self.root_uri+"/document?id=document_id&ref=3"
            )
        )
        # Adding child
        mock_set.get(
            self.root_uri + "/documents?id=document_id&ref=3",
            text=_load_mock("document", "sequence/passage_3.xml"),
            complete_qs=True,
            headers=make_links(
                collection=self.root_uri+"/collections?id=document_id",
                up=self.root_uri+"/document?id=document_id",
                prev=self.root_uri+"/document?id=document_id&ref=2"
            )
        )
        doc = self.resolver.getTextualNode(textId="document_id")
        child = doc.getTextualNode(DtsReference("1"))
        self.assertIn(
            "Passage 1", child.export(Mimetypes.PLAINTEXT),
            "Text of the response should be exportable"
        )
        self.assertEqual(
            DtsReference("2"), child.nextId, "Next passage is 2 !"
        )
        self.assertIn(
            "Passage 2", child.next.export(Mimetypes.PLAINTEXT),
            "No specific queries need to be written for the following passage"
        )
        self.assertIn(
            "Passage 3", child.next.next.export(Mimetypes.PLAINTEXT),
            "No specific queries need to be written for the following passage"
        )

    @requests_mock.mock()
    def test_retrieve_child_start_end_then_moving(self, mock_set):
        """ Retrieve child passage with range ID then checkout others by navigation using link headers"""
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        # Adding child
        mock_set.get(
            self.root_uri + "/documents?id=document_id&start=1&end=2",
            text=_load_mock("document", "sequence/passage_1.xml"),
            complete_qs=True,
            headers=make_links(
                collection=self.root_uri+"/collections?id=document_id",
                up=self.root_uri+"/document?id=document_id",
                next=self.root_uri+"/document?id=document_id&start=3&end=4"
            )
        )
        # Adding child
        mock_set.get(
            self.root_uri + "/documents?id=document_id&start=3&end=4",
            text=_load_mock("document", "sequence/passage_2.xml"),
            complete_qs=True,
            headers=make_links(
                collection=self.root_uri+"/collections?id=document_id",
                up=self.root_uri+"/document?id=document_id",
                prev=self.root_uri+"/document?id=document_id&start=1&end=2",
                next=self.root_uri+"/document?id=document_id&start=5&end=6"
            )
        )
        # Adding child
        mock_set.get(
            self.root_uri + "/documents?id=document_id&start=5&end=6",
            text=_load_mock("document", "sequence/passage_3.xml"),
            complete_qs=True,
            headers=make_links(
                collection=self.root_uri+"/collections?id=document_id",
                up=self.root_uri+"/document?id=document_id",
                prev=self.root_uri+"/document?id=document_id&start=3&end=4"
            )
        )
        child = self.resolver.getTextualNode(textId="document_id", subreference=DtsReference("1", "2"))
        self.assertIn(
            "Passage 1", child.export(Mimetypes.PLAINTEXT),
            "Text of the response should be exportable"
        )
        self.assertEqual(
            DtsReference("3", "4"), child.nextId, "Next passage is 3 to 4 !"
        )
        self.assertEqual(
            DtsReference("1", "2"), child.reference, "Child reference is good"
        )
        self.assertIn(
            "Passage 2", child.next.export(Mimetypes.PLAINTEXT),
            "No specific queries need to be written for the following passage"
        )
        self.assertIn(
            "Passage 3", child.next.next.export(Mimetypes.PLAINTEXT),
            "No specific queries need to be written for the following passage"
        )
