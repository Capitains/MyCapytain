# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from MyCapytain.resolvers.cts.local import CTSCapitainsLocalResolver
from MyCapytain.common.constants import NS, Mimetypes, NAMESPACES, GRAPH
from MyCapytain.common.reference import URN, Reference
from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.resources.prototypes.cts.inventory import PrototypeTextGroup, PrototypeText as TextMetadata
from MyCapytain.resources.prototypes.text import Passage
from unittest import TestCase


class TestXMLFolderResolverBehindTheScene(TestCase):
    """ Test behind the scene functions of the Resolver """
    def test_resource_parser(self):
        """ Test that the initiation finds correctly the resources """
        Repository = CTSCapitainsLocalResolver(["./tests/testing_data/farsiLit"])
        self.assertEqual(
            Repository.inventory["urn:cts:farsiLit:hafez"].urn, URN("urn:cts:farsiLit:hafez"),
            "Hafez is found"
        )
        self.assertEqual(
            len(Repository.inventory["urn:cts:farsiLit:hafez"].works), 1,
            "Hafez has one child"
        )
        self.assertEqual(
            Repository.inventory["urn:cts:farsiLit:hafez.divan"].urn, URN("urn:cts:farsiLit:hafez.divan"),
            "Divan is found"
        )
        self.assertEqual(
            len(Repository.inventory["urn:cts:farsiLit:hafez.divan"].texts), 3,
            "Divan has 3 children"
        )

    def test_text_resource(self):
        """ Test to get the text resource to perform other queries """
        Repository = CTSCapitainsLocalResolver(["./tests/testing_data/farsiLit"])
        text, metadata = Repository.__getText__("urn:cts:farsiLit:hafez.divan.perseus-eng1")
        self.assertEqual(
            len(text.citation), 4,
            "Object has a citation property of length 4"
        )
        self.assertEqual(
            text.getTextualNode(Reference("1.1.1.1")).export(output=Mimetypes.PLAINTEXT),
            "Ho ! Saki, pass around and offer the bowl (of love for God) : ### ",
            "It should be possible to retrieve text"
        )

    def test_get_capabilities(self):
        """ Check Get Capabilities """
        Repository = CTSCapitainsLocalResolver(
            ["./tests/testing_data/farsiLit"]
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__()[0]), 4,
            "General no filter works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(category="edition")[0]), 2,
            "Type filter works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(lang="ger")[0]), 1,
            "Filtering on language works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(category="edition", lang="ger")[0]), 0,
            "Type filter + lang works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(category="translation", lang="ger")[0]), 1,
            "Type filter + lang works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(page=1, limit=2, pagination=True)[0]), 2,
            "Pagination works without other filters"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(page=2, limit=2, pagination=True)[0]), 2,
            "Pagination works without other filters at list end"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:farsiLit")[0]), 3,
            "URN Filtering works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:latinLit")[0]), 1,
            "URN Filtering works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:farsiLit:hafez.divan.perseus-eng1")[0]), 1,
            "Complete URN filtering works"
        )

    def test_get_shared_textgroup_cross_repo(self):
        """ Check Get Capabilities """
        Repository = CTSCapitainsLocalResolver(
            [
                "./tests/testing_data/farsiLit",
                "./tests/testing_data/latinLit2"
            ]
        )
        self.assertIsNotNone(
            Repository.__getText__("urn:cts:latinLit:phi1294.phi002.perseus-lat2"),
            "We should find perseus-lat2"
        )
        self.assertIsNotNone(
            Repository.__getText__("urn:cts:latinLit:phi1294.phi002.opp-lat2"),
            "We should find perseus-lat2"
        )

    def test_get_capabilities_nocites(self):
        """ Check Get Capabilities latinLit data"""
        Repository = CTSCapitainsLocalResolver(
            ["./tests/testing_data/latinLit"]
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:latinLit:stoa0045.stoa008.perseus-lat2")[0]), 0,
            "Texts without citations were ignored"
        )

    def test_pagination(self):
        self.assertEqual(
            CTSCapitainsLocalResolver.pagination(2, 30, 150), (30, 60, 2, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            CTSCapitainsLocalResolver.pagination(4, 40, 150), (120, 150, 4, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            CTSCapitainsLocalResolver.pagination(5, 40, 150), (120, 150, 4, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            CTSCapitainsLocalResolver.pagination(5, 100, 150), (100, 150, 2, 50),
            " Pagination should give corrected page and correct count"
        )
        self.assertEqual(
            CTSCapitainsLocalResolver.pagination(5, 110, 150), (40, 50, 5, 10),
            " Pagination should use default limit (10) when getting too much "
        )


class TextXMLFolderResolver(TestCase):
    """ Ensure working state of resolver """
    def setUp(self):
        GRAPH.remove((None, None, None))
        self.resolver = CTSCapitainsLocalResolver(["./tests/testing_data/latinLit2"])

    def test_getPassage_full(self):
        """ Test that we can get a full text """
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )

        children = list(passage.getReffs())

        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], '1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(
                output=Mimetypes.PYTHON.ETREE
            ).xpath(
                ".//tei:div[@n='1']/tei:div[@n='1']/tei:l[@n='1']/text()", namespaces=NS, magic_string=False
            ),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_subreference(self):
        """ Test that we can get a subreference text passage"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.1")

        # We check we made a reroute to GetPassage request
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )

        children = list(passage.getReffs())

        self.assertEqual(
            children[0], '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_full_metadata(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", metadata=True)

        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            str(passage.metadata[NAMESPACES.CTS.term("title"), "eng"]), "Epigrammata",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[NAMESPACES.CTS.term("groupname"),"eng"]), "Martial",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[NAMESPACES.CTS.term("label"), "eng"]), "Epigrams",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[NAMESPACES.CTS.term("description"), "eng"]),
            "M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.name, "book",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            len(passage.citation), 3,
            "Local Inventory Files should be parsed and aggregated correctly"
        )

        children = list(passage.getReffs(level=3))
        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], '1.pr.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(
                output=Mimetypes.PYTHON.ETREE
            ).xpath(
                ".//tei:div[@n='1']/tei:div[@n='1']/tei:l[@n='1']/text()", namespaces=NS, magic_string=False
            ),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_prevnext(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1",  metadata=True
        )

        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            passage.prevId, "1.pr",
            "Previous Passage ID should be parsed"
        )
        self.assertEqual(
            passage.nextId, "1.2",
            "Next Passage ID should be parsed"
        )

        children = list(passage.getReffs())
        # Ensure navigability
        self.assertIn(
            "verentia ludant; quae adeo antiquis auctoribus defuit, ut",
            passage.prev.export(output=Mimetypes.PLAINTEXT),
            "Left and Right Navigation should be available"
        )
        self.assertIn(
            "Qui tecum cupis esse meos ubicumque libellos ",
            passage.next.export(output=Mimetypes.PLAINTEXT),
            "Left and Right Navigation should be available"
        )

        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_metadata_prevnext(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1", metadata=True, prevnext=True
        )
        self.assertIsInstance(
            passage, Passage,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            str(passage.metadata[NAMESPACES.CTS.term("title"), "eng"]), "Epigrammata",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[NAMESPACES.CTS.term("groupname"), "eng"]), "Martial",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[NAMESPACES.CTS.term("label"), "eng"]), "Epigrams",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[NAMESPACES.CTS.term("description"), "eng"]),
            "M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.name, "book",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            len(passage.citation), 3,
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.prevId, "1.pr",
            "Previous Passage ID should be parsed"
        )
        self.assertEqual(
            passage.nextId, "1.2",
            "Next Passage ID should be parsed"
        )
        children = list(passage.getReffs())
        # Ensure navigability
        self.assertIn(
            "verentia ludant; quae adeo antiquis auctoribus defuit, ut",
            passage.prev.export(output=Mimetypes.PLAINTEXT),
            "Left and Right Navigation should be available"
        )
        self.assertIn(
            "Qui tecum cupis esse meos ubicumque libellos ",
            passage.next.export(output=Mimetypes.PLAINTEXT),
            "Left and Right Navigation should be available"
        )

        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export PrototypeText should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=NS, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getMetadata_full(self):
        """ Checks retrieval of Metadata information """
        metadata = self.resolver.getMetadata()
        self.assertIsInstance(
            metadata, Collection,
            "Resolver should return a collection object"
        )
        self.assertIsInstance(
            metadata.members[0], Collection,
            "Members of Inventory should be TextGroups"
        )
        self.assertEqual(
            len(metadata.descendants), 43,
            "There should be as many descendants as there is edition, translation, works and textgroup + 1 for "
            "default inventory"
        )
        self.assertEqual(
            len(metadata.readableDescendants), 25,
            "There should be as many readable descendants as there is edition, translation(25 ed+tr)"
        )
        self.assertEqual(
            len([x for x in metadata.readableDescendants if isinstance(x, TextMetadata)]), 25,
            "There should be 24 editions + 1 translations in readableDescendants"
        )
        self.assertEqual(
            len(metadata.export(output=Mimetypes.PYTHON.ETREE).xpath(
                "//ti:edition[@urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2']", namespaces=NS)), 1,
            "There should be one node in exported format corresponding to lat2"
        )
        print(metadata.export(output=Mimetypes.JSON.DTS.Std))
        self.assertCountEqual(
            [x["@id"] for x in metadata.export(output=Mimetypes.JSON.DTS.Std)["@graph"]["dts:members"]],
            ["urn:cts:latinLit:phi1294", "urn:cts:latinLit:phi0959",
             "urn:cts:greekLit:tlg0003", "urn:cts:latinLit:phi1276"],
            "There should be 4 Members in DTS JSON"
        )

    def test_getMetadata_subset(self):
        """ Checks retrieval of Metadata information """
        metadata = self.resolver.getMetadata(objectId="urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(
            metadata, Collection,
            "Resolver should return a collection object"
        )
        self.assertIsInstance(
            metadata.members[0], TextMetadata,
            "Members of PrototypeWork should be Texts"
        )
        self.assertEqual(
            len(metadata.descendants), 1,
            "There should be as many descendants as there is edition, translation"
        )
        self.assertEqual(
            len(metadata.readableDescendants), 1,
            "There should be 1 edition in readableDescendants"
        )
        self.assertEqual(
            len([x for x in metadata.readableDescendants if isinstance(x, TextMetadata)]), 1,
            "There should be 1 edition in readableDescendants"
        )
        self.assertIsInstance(
            metadata.parent, PrototypeTextGroup,
            "First parent should be PrototypeTextGroup"
        )
        self.assertIsInstance(
            metadata.parents[0], PrototypeTextGroup,
            "First parent should be PrototypeTextGroup"
        )
        self.assertEqual(
            len(metadata.export(output=Mimetypes.PYTHON.ETREE).xpath(
                "//ti:edition[@urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2']", namespaces=NS)), 1,
            "There should be one node in exported format corresponding to lat2"
        )
        self.assertEqual(
            [x["@id"] for x in metadata.export(output=Mimetypes.JSON.DTS.Std)["@graph"]["dts:members"]],
            ["urn:cts:latinLit:phi1294.phi002.perseus-lat2"],
            "There should be one member in DTS JSON"
        )

    def test_getSiblings(self):
        """ Ensure getSiblings works well """
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1"
        )
        self.assertEqual(
            previous, "1.pr",
            "Previous should be well computed"
        )
        self.assertEqual(
            nextious, "1.2",
            "Previous should be well computed"
        )

    def test_getSiblings_nextOnly(self):
        """ Ensure getSiblings works well when there is only the next passage"""
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.pr"
        )
        self.assertEqual(
            previous, None,
            "Previous Should not exist"
        )
        self.assertEqual(
            nextious, "1.1",
            "Next should be well computed"
        )

    def test_getSiblings_prevOnly(self):
        """ Ensure getSiblings works well when there is only the previous passage"""
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="14.223"
        )
        self.assertEqual(
            previous, "14.222",
            "Previous should be well computed"
        )
        self.assertEqual(
            nextious, None,
            "Next should not exist"
        )

    def test_getReffs_full(self):
        """ Ensure getReffs works well """
        reffs = self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=1)
        self.assertEqual(
            len(reffs), 14,
            "There should be 14 books"
        )
        self.assertEqual(
            reffs[0], "1"
        )

        reffs = self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=2)
        self.assertEqual(
            len(reffs), 1527,
            "There should be 1527 poems"
        )
        self.assertEqual(
            reffs[0], "1.pr"
        )

        reffs = self.resolver.getReffs(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2",
            subreference="1.1",
            level=1
        )
        self.assertEqual(
            len(reffs), 6,
            "There should be 6 references"
        )
        self.assertEqual(
            reffs[0], "1.1.1"
        )
