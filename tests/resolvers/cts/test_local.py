# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from MyCapytain.resolvers.cts.local import CtsCapitainsLocalResolver
from MyCapytain.common.constants import XPATH_NAMESPACES, Mimetypes, RDF_NAMESPACES, get_graph
from MyCapytain.common.reference._capitains_cts import CtsReference, URN
from MyCapytain.errors import InvalidURN, UnknownObjectError, UndispatchedTextError
from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.resources.prototypes.cts.inventory import CtsTextgroupMetadata, CtsTextMetadata as TextMetadata, \
    CtsTranslationMetadata, CtsTextInventoryMetadata, CtsCommentaryMetadata, CtsTextInventoryCollection
from MyCapytain.resources.prototypes.cts.text import PrototypeCtsPassage
from MyCapytain.resolvers.utils import CollectionDispatcher
from unittest import TestCase


class TestXMLFolderResolverBehindTheScene(TestCase):
    """ Test behind the scene functions of the Resolver """
    def test_resource_parser(self):
        """ Test that the initiation finds correctly the resources """
        Repository = CtsCapitainsLocalResolver(["./tests/testing_data/farsiLit"])
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
        Repository = CtsCapitainsLocalResolver(["./tests/testing_data/farsiLit"])
        text, metadata = Repository.__getText__("urn:cts:farsiLit:hafez.divan.perseus-eng1")
        self.assertEqual(
            len(text.citation), 4,
            "Object has a citation property of length 4"
        )
        self.assertEqual(
            text.getTextualNode(CtsReference("1.1.1.1")).export(output=Mimetypes.PLAINTEXT),
            "Ho ! Saki, pass around and offer the bowl (of love for God) : ### ",
            "It should be possible to retrieve text"
        )

    def test_missing_text_resource(self):
        """ Test to make sure the correct warning is raised if a text is missing """
        with self.assertLogs(CtsCapitainsLocalResolver(["./tests/testing_data/missing_text"]).logger) as cm:
            Repository = CtsCapitainsLocalResolver(["./tests/testing_data/missing_text"])
            text, metadata = Repository.__getText__("urn:cts:farsiLit:hafez.divan.missing_text")
            self.assertIsNone(text)
        self.assertIn('WARNING:root:The file '
                      './tests/testing_data/missing_text/data/hafez/divan/hafez.divan.missing_text.xml '
                      'is mentioned in the metadata but does not exist', cm.output)
        self.assertIn(
            'ERROR:root:./tests/testing_data/missing_text/data/hafez/divan/hafez.divan.missing_text.xml is not present',
            cm.output
        )

    def test_get_capabilities(self):
        """ Check Get Capabilities """
        Repository = CtsCapitainsLocalResolver(
            ["./tests/testing_data/farsiLit"]
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__()[0]), 5,
            "General no filter works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(category="edition")[0]), 2,
            "Type filter works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(category="commentary")[0]), 1,
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
            len(Repository.__getTextMetadata__(category="commentary", lang="lat")[0]), 1,
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
            len(Repository.__getTextMetadata__(urn="urn:cts:latinLit")[0]), 2,
            "URN Filtering works"
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:farsiLit:hafez.divan.perseus-eng1")[0]), 1,
            "Complete URN filtering works"
        )

    def test_get_shared_textgroup_cross_repo(self):
        """ Check Get Capabilities """
        Repository = CtsCapitainsLocalResolver(
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
        Repository = CtsCapitainsLocalResolver(
            ["./tests/testing_data/latinLit"]
        )
        self.assertEqual(
            len(Repository.__getTextMetadata__(urn="urn:cts:latinLit:stoa0045.stoa008.perseus-lat2")[0]), 0,
            "Texts without citations were ignored"
        )

    def test_pagination(self):
        self.assertEqual(
            CtsCapitainsLocalResolver.pagination(2, 30, 150), (30, 60, 2, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            CtsCapitainsLocalResolver.pagination(4, 40, 150), (120, 150, 4, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            CtsCapitainsLocalResolver.pagination(5, 40, 150), (120, 150, 4, 30),
            " Pagination should return Array limits "
        )
        self.assertEqual(
            CtsCapitainsLocalResolver.pagination(5, 100, 150), (100, 150, 2, 50),
            " Pagination should give corrected page and correct count"
        )
        self.assertEqual(
            CtsCapitainsLocalResolver.pagination(5, 110, 150), (40, 50, 5, 10),
            " Pagination should use default limit (10) when getting too much "
        )


class TextXMLFolderResolver(TestCase):
    """ Ensure working state of resolver """
    def setUp(self):
        get_graph().remove((None, None, None))
        self.resolver = CtsCapitainsLocalResolver(["./tests/testing_data/latinLit2"])

    def test_getPassage_full(self):
        """ Test that we can get a full text """
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertIsInstance(
            passage, PrototypeCtsPassage,
            "GetPassage should always return passages objects"
        )

        children = passage.getReffs()

        # We check the passage is able to perform further requests and is well instantiated
        self.assertEqual(
            children[0], CtsReference('1'),
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export CtsTextMetadata should work correctly"
        )

        self.assertEqual(
            passage.export(
                output=Mimetypes.PYTHON.ETREE
            ).xpath(
                ".//tei:div[@n='1']/tei:div[@n='1']/tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False
            ),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_no_canonical(self):
        """ Test that we can get a subreference text passage where no canonical exists"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi0959.phi010.perseus-eng2", "2")
        self.assertEqual(
            passage.export(Mimetypes.PLAINTEXT), "Omne fuit Musae carmen inerme meae; ",
            "CapitainsCtsPassage should resolve if directly asked"
        )
        with self.assertRaises(UnknownObjectError):
            passage = self.resolver.getTextualNode("urn:cts:latinLit:phi0959.phi010", "2")
        with self.assertRaises(InvalidURN):
            passage = self.resolver.getTextualNode("urn:cts:latinLit:phi0959", "2")

    def test_getPassage_subreference(self):
        """ Test that we can get a subreference text passage"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", "1.1")

        # We check we made a reroute to GetPassage request
        self.assertIsInstance(
            passage, PrototypeCtsPassage,
            "GetPassage should always return passages objects"
        )

        children = list(passage.getReffs())

        self.assertEqual(
            str(children[0]), '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export CtsTextMetadata should work correctly"
        )
        canonical = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002", "1.1")
        self.assertEqual(
            passage.export(output=Mimetypes.PLAINTEXT),
            canonical.export(output=Mimetypes.PLAINTEXT),
            "Canonical text should work"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_full_metadata(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2", metadata=True)

        self.assertIsInstance(
            passage, PrototypeCtsPassage,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("title"), "eng"]), "Epigrammata",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("groupname"), "eng"]), "Martial",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("label"), "eng"]), "Epigrams",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("description"), "eng"]),
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
            children[0], CtsReference('1.pr.1'),
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export CtsTextMetadata should work correctly"
        )

        self.assertEqual(
            passage.export(
                output=Mimetypes.PYTHON.ETREE
            ).xpath(
                ".//tei:div[@n='1']/tei:div[@n='1']/tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False
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
            passage, PrototypeCtsPassage,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            passage.prevId, CtsReference("1.pr"),
            "Previous CapitainsCtsPassage ID should be parsed"
        )
        self.assertEqual(
            passage.nextId, CtsReference("1.2"),
            "Next CapitainsCtsPassage ID should be parsed"
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
            str(children[0]), '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export CtsTextMetadata should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False),
            ["Hic est quem legis ille, quem requiris, "],
            "Export to Etree should give an Etree or Etree like object"
        )

    def test_getPassage_metadata_prevnext(self):
        """ Test that we can get a full text with its metadata"""
        passage = self.resolver.getTextualNode(
            "urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1", metadata=True, prevnext=True
        )
        self.assertIsInstance(
            passage, PrototypeCtsPassage,
            "GetPassage should always return passages objects"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("title"), "eng"]), "Epigrammata",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("groupname"), "eng"]), "Martial",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("label"), "eng"]), "Epigrams",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            str(passage.metadata[RDF_NAMESPACES.CTS.term("description"), "eng"]),
            "M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.name, "poem",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.citation.root.name, "book",
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            len(passage.citation.root), 3,
            "Local Inventory Files should be parsed and aggregated correctly"
        )
        self.assertEqual(
            passage.prevId, CtsReference("1.pr"),
            "Previous CapitainsCtsPassage ID should be parsed"
        )
        self.assertEqual(
            passage.nextId, CtsReference("1.2"),
            "Next CapitainsCtsPassage ID should be parsed"
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
            str(children[0]), '1.1.1',
            "Resource should be string identifiers"
        )

        self.assertIn(
            "Hic est quem legis ille, quem requiris,", passage.export(output=Mimetypes.PLAINTEXT),
            "Export CtsTextMetadata should work correctly"
        )

        self.assertEqual(
            passage.export(output=Mimetypes.PYTHON.ETREE).xpath(".//tei:l[@n='1']/text()", namespaces=XPATH_NAMESPACES, magic_string=False),
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
            len(metadata.descendants), 44,
            "There should be as many descendants as there is edition, translation, commentary, works and textgroup + 1 "
            "for default inventory"
        )
        self.assertEqual(
            len(metadata.readableDescendants), 26,
            "There should be as many readable descendants as there is edition, translation, commentary (26 ed+tr+cm)"
        )
        self.assertEqual(
            len([x for x in metadata.readableDescendants if isinstance(x, TextMetadata)]), 26,
            "There should be 24 editions + 1 translation + 1 commentary in readableDescendants"
        )
        self.assertEqual(
            len(metadata.export(output=Mimetypes.PYTHON.ETREE).xpath(
                "//ti:edition[@urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2']", namespaces=XPATH_NAMESPACES)), 1,
            "There should be one node in exported format corresponding to lat2"
        )
        self.assertCountEqual(
            [x["@id"] for x in metadata.export(output=Mimetypes.JSON.DTS.Std)["member"]],
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
            "Members of CtsWorkMetadata should be Texts"
        )
        self.assertEqual(
            len(metadata.descendants), 2,
            "There should be as many descendants as there is edition, translation, commentary"
        )
        self.assertEqual(
            len(metadata.readableDescendants), 2,
            "There should be 1 edition + 1 commentary in readableDescendants"
        )
        self.assertEqual(
            len([x for x in metadata.readableDescendants if isinstance(x, TextMetadata)]), 2,
            "There should be 1 edition + 1 commentary in readableDescendants"
        )
        self.assertIsInstance(
            metadata.parent, CtsTextgroupMetadata,
            "First parent should be CtsTextgroupMetadata"
        )
        self.assertIsInstance(
            metadata.ancestors[0], CtsTextgroupMetadata,
            "First parent should be CtsTextgroupMetadata"
        )
        self.assertEqual(
            len(metadata.export(output=Mimetypes.PYTHON.ETREE).xpath(
                "//ti:edition[@urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2']", namespaces=XPATH_NAMESPACES)), 1,
            "There should be one node in exported format corresponding to lat2"
        )
        self.assertCountEqual(
            [x["@id"] for x in metadata.export(output=Mimetypes.JSON.DTS.Std)["member"]],
            ["urn:cts:latinLit:phi1294.phi002.opp-eng3", "urn:cts:latinLit:phi1294.phi002.perseus-lat2"],
            "There should be two members in DTS JSON"
        )

        tr = self.resolver.getMetadata(objectId="urn:cts:greekLit:tlg0003.tlg001.opp-fre1")
        self.assertIsInstance(
            tr, CtsTranslationMetadata, "Metadata should be translation"
        )
        self.assertEqual(
            tr.lang, "fre", "Language is French"
        )
        self.assertIn(
            "Histoire de la Guerre du Péloponnése",
            tr.get_description("eng"),
            "Description should be the right one"
        )

        cm = self.resolver.getMetadata(objectId="urn:cts:latinLit:phi1294.phi002.opp-eng3")
        self.assertIsInstance(
            cm, CtsCommentaryMetadata, "Metadata should be commentary"
        )
        self.assertEqual(
            cm.lang, "eng", "Language is English"
        )
        self.assertIn(
            "Introduction to Martial's Epigrammata",
            cm.get_description("eng"),
            "Description should be the right one"
        )

    def test_getSiblings(self):
        """ Ensure getSiblings works well """
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.1"
        )
        self.assertEqual(
            previous, CtsReference("1.pr"),
            "Previous reference should be well computed"
        )
        self.assertEqual(
            nextious, CtsReference("1.2"),
            "Next reference should be well computed"
        )

    def test_getSiblings_nextOnly(self):
        """ Ensure getSiblings works well when there is only the next passage"""
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="1.pr"
        )
        self.assertEqual(
            previous, None,
            "Previous reference should not exist"
        )
        self.assertEqual(
            nextious, CtsReference("1.1"),
            "Next reference should be well computed"
        )

    def test_getSiblings_prevOnly(self):
        """ Ensure getSiblings works well when there is only the previous passage"""
        previous, nextious = self.resolver.getSiblings(
            textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", subreference="14.223"
        )
        self.assertEqual(
            previous, CtsReference("14.222"),
            "Previous reference should be well computed"
        )
        self.assertEqual(
            nextious, None,
            "Next reference should not exist"
        )

    def test_getReffs_full(self):
        """ Ensure getReffs works well """
        reffs = self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=1)
        self.assertEqual(
            len(reffs), 14,
            "There should be 14 books"
        )
        self.assertEqual(
            reffs[0], CtsReference("1")
        )

        reffs = self.resolver.getReffs(textId="urn:cts:latinLit:phi1294.phi002.perseus-lat2", level=2)
        self.assertEqual(
            len(reffs), 1527,
            "There should be 1527 poems"
        )
        self.assertEqual(
            reffs[0], CtsReference("1.pr")
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
            reffs[0], CtsReference("1.1.1")
        )


class TextXMLFolderResolverDispatcher(TestCase):
    """ Ensure working state of resolver """
    def setUp(self):
        get_graph().remove((None, None, None))

    def test_dispatching_latin_greek(self):
        tic = CtsTextInventoryCollection()
        latin = CtsTextInventoryMetadata("urn:perseus:latinLit", parent=tic)
        latin.set_label("Classical Latin", "eng")
        farsi = CtsTextInventoryMetadata("urn:perseus:farsiLit", parent=tic)
        farsi.set_label("Farsi", "eng")
        gc = CtsTextInventoryMetadata("urn:perseus:greekLit", parent=tic)
        gc.set_label("Ancient Greek", "eng")
        gc.set_label("Grec Ancien", "fre")

        dispatcher = CollectionDispatcher(tic)

        @dispatcher.inventory("urn:perseus:latinLit")
        def dispatchLatinLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:latinLit:"):
                return True
            return False

        @dispatcher.inventory("urn:perseus:farsiLit")
        def dispatchfFarsiLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:farsiLit:"):
                return True
            return False

        @dispatcher.inventory("urn:perseus:greekLit")
        def dispatchGreekLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:greekLit:"):
                return True
            return False

        resolver = CtsCapitainsLocalResolver(
            ["./tests/testing_data/latinLit2"],
            dispatcher=dispatcher
        )
        latin_stuff = resolver.getMetadata("urn:perseus:latinLit")
        greek_stuff = resolver.getMetadata("urn:perseus:greekLit")
        farsi_stuff = resolver.getMetadata("urn:perseus:farsiLit")
        self.assertEqual(
            len(latin_stuff.readableDescendants), 20,
            "There should be 20 readable descendants in Latin"
        )
        self.assertIsInstance(
            latin_stuff, CtsTextInventoryMetadata, "should be textinventory"
        )
        self.assertEqual(
            len(greek_stuff.readableDescendants), 6,
            "There should be 6 readable descendants in Greek [6 only in __cts__.xml]"
        )
        self.assertEqual(
            len(farsi_stuff.descendants), 0,
            "There should be nothing in FarsiLit"
        )
        self.assertEqual(
            str(greek_stuff.get_label("fre")), "Grec Ancien",
            "Label should be correct"
        )

        with self.assertRaises(KeyError):
            _ = latin_stuff["urn:cts:greekLit:tlg0003"]

    def test_dispatching_error(self):
        tic = CtsTextInventoryCollection()
        latin = CtsTextInventoryMetadata("urn:perseus:latinLit", parent=tic)
        latin.set_label("Classical Latin", "eng")
        dispatcher = CollectionDispatcher(tic)
        # We remove default dispatcher
        dispatcher.__methods__ = []

        @dispatcher.inventory("urn:perseus:latinLit")
        def dispatchLatinLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:latinLit:"):
                return True
            return False

        CtsCapitainsLocalResolver.RAISE_ON_UNDISPATCHED = True
        with self.assertRaises(UndispatchedTextError):
            resolver = CtsCapitainsLocalResolver(
                ["./tests/testing_data/latinLit2"],
                dispatcher=dispatcher
            )

        CtsCapitainsLocalResolver.RAISE_ON_UNDISPATCHED = False
        try:
            resolver = CtsCapitainsLocalResolver(
                ["./tests/testing_data/latinLit2"],
                dispatcher=dispatcher
            )
        except UndispatchedTextError as E:
            self.fail("UndispatchedTextError should not have been raised")

    def test_dispatching_output(self):
        tic = CtsTextInventoryCollection()
        latin = CtsTextInventoryMetadata("urn:perseus:latinLit", parent=tic)
        latin.set_label("Classical Latin", "eng")
        farsi = CtsTextInventoryMetadata("urn:perseus:farsiLit", parent=tic)
        farsi.set_label("Farsi", "eng")
        gc = CtsTextInventoryMetadata("urn:perseus:greekLit", parent=tic)
        gc.set_label("Ancient Greek", "eng")
        gc.set_label("Grec Ancien", "fre")

        dispatcher = CollectionDispatcher(tic)

        @dispatcher.inventory("urn:perseus:latinLit")
        def dispatchLatinLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:latinLit:"):
                return True
            return False

        @dispatcher.inventory("urn:perseus:farsiLit")
        def dispatchfFarsiLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:farsiLit:"):
                return True
            return False

        @dispatcher.inventory("urn:perseus:greekLit")
        def dispatchGreekLit(collection, path=None, **kwargs):
            if collection.id.startswith("urn:cts:greekLit:"):
                return True
            return False

        resolver = CtsCapitainsLocalResolver(
            ["./tests/testing_data/latinLit2"],
            dispatcher=dispatcher
        )

        all = resolver.getMetadata().export(Mimetypes.XML.CTS)
        latin_stuff = resolver.getMetadata("urn:perseus:latinLit").export(Mimetypes.XML.CTS)
        greek_stuff = resolver.getMetadata("urn:perseus:greekLit").export(Mimetypes.XML.CTS)
        farsi_stuff = resolver.getMetadata("urn:perseus:farsiLit").export(Mimetypes.XML.CTS)
        get_graph().remove((None, None, None))
        latin_stuff, greek_stuff, farsi_stuff = XmlCtsTextInventoryMetadata.parse(latin_stuff), XmlCtsTextInventoryMetadata.parse(greek_stuff), \
                                                XmlCtsTextInventoryMetadata.parse(farsi_stuff)
        self.assertEqual(
            len(latin_stuff.readableDescendants), 20,
            "There should be 20 readable descendants in Latin"
        )
        self.assertIsInstance(
            latin_stuff, CtsTextInventoryMetadata, "should be textinventory"
        )
        self.assertEqual(
            len(greek_stuff.readableDescendants), 6,
            "There should be 6 readable descendants in Greek [6 only in __cts__.xml]"
        )
        self.assertEqual(
            len(farsi_stuff.descendants), 0,
            "There should be nothing in FarsiLit"
        )
        self.assertEqual(
            greek_stuff.get_label("fre"), None,  # CapitainsCtsText inventory have no label in CTS
            "Label should be correct"
        )
        get_graph().remove((None, None, None))
        all = XmlCtsTextInventoryMetadata.parse(all)
        self.assertEqual(
            len(all.readableDescendants), 26,
            "There should be all 26 readable descendants in the master collection"
        )

    def test_post_work_dispatching_active(self):
        """ Dispatching is working after editions, we dispatch based on citation scheme"""
        tic = CtsTextInventoryCollection()
        poetry = CtsTextInventoryMetadata("urn:perseus:poetry", parent=tic)
        prose = CtsTextInventoryMetadata("urn:perseus:prose", parent=tic)

        dispatcher = CollectionDispatcher(tic, default_inventory_name="urn:perseus:prose")

        @dispatcher.inventory("urn:perseus:poetry")
        def dispatchPoetry(collection, **kwargs):
            for readable in collection.readableDescendants:
                for citation in readable.citation:
                    if citation.name == "line":
                        return True
            return False

        resolver = CtsCapitainsLocalResolver(
            ["./tests/testing_data/latinLit2"],
            dispatcher=dispatcher
        )

        all = resolver.getMetadata().export(Mimetypes.XML.CTS)
        poetry_stuff = resolver.getMetadata("urn:perseus:poetry").export(Mimetypes.XML.CTS)
        prose_stuff = resolver.getMetadata("urn:perseus:prose").export(Mimetypes.XML.CTS)
        get_graph().remove((None, None, None))
        del poetry, prose
        poetry, prose = XmlCtsTextInventoryMetadata.parse(poetry_stuff), XmlCtsTextInventoryMetadata.parse(prose_stuff)
        self.assertEqual(
            len(poetry.textgroups), 3,
            "There should be 3 textgroups in Poetry (Martial, Ovid and Juvenal)"
        )
        self.assertIsInstance(poetry, CtsTextInventoryMetadata, "should be textinventory")
        self.assertEqual(
            len(prose.textgroups), 1,
            "There should be one textgroup in Prose (Greek texts)"
        )
        get_graph().remove((None, None, None))
        del poetry, prose
        all = XmlCtsTextInventoryMetadata.parse(all)
        self.assertEqual(
            len(all.readableDescendants), 26,
            "There should be all 26 readable descendants in the master collection"
        )
