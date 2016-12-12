# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from MyCapytain.resolvers.cts.local import CTSCapitainsLocalResolver
from MyCapytain.common.utils import Mimetypes
from MyCapytain.common.reference import URN, Reference
from unittest import TestCase


class TestXMLFolderResolver(TestCase):
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
            text.getPassage(Reference("1.1.1.1")).export(output=Mimetypes.PLAINTEXT),
            "Ho ! Saki, pass around and offer the bowl (of love for God) : ### ",
            "It should be possible to retrieve text"
        )

    def test_get_capabilities(self):
        """ Check Get Capabilities """
        Repository = CTSCapitainsLocalResolver(
            ["./tests/testing_data/farsiLit"]
        )
        self.assertEqual(
            len(Repository.__getCapabilities__()[0]), 4,
            "General no filter works"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(category="edition")[0]), 2,
            "Type filter works"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(lang="ger")[0]), 1,
            "Filtering on language works"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(category="edition", lang="ger")[0]), 0,
            "Type filter + lang works"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(category="translation", lang="ger")[0]), 1,
            "Type filter + lang works"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(page=1, limit=2, pagination=True)[0]), 2,
            "Pagination works without other filters"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(page=2, limit=2, pagination=True)[0]), 2,
            "Pagination works without other filters at list end"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(urn="urn:cts:farsiLit")[0]), 3,
            "URN Filtering works"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(urn="urn:cts:latinLit")[0]), 1,
            "URN Filtering works"
        )
        self.assertEqual(
            len(Repository.__getCapabilities__(urn="urn:cts:farsiLit:hafez.divan.perseus-eng1")[0]), 1,
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
            len(Repository.__getCapabilities__(urn="urn:cts:latinLit:stoa0045.stoa008.perseus-lat2")[0]), 0,
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
