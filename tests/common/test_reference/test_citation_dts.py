from MyCapytain.common.reference import DtsCitationSet, DtsCitation
from MyCapytain.common.constants import RDF_NAMESPACES
from unittest import TestCase
from pyld import jsonld


_dts = RDF_NAMESPACES.DTS

_ex_1 = [
    {
        "dts:citeType": "front"
    },
    {
        "dts:citeType": "poem",
        "dts:citeStructure": [
            {
                "dts:citeType": "line"
            }
        ]
    }
]
_ex_2 = [
    {
        "dts:citeType": "poem",
        "dts:citeStructure": {
            "dts:citeType": "line"
        }
    }
]

_ex_3 = [
    {
        "dts:citeType": "front",
        "dts:citeStructure": [
            {
                "dts:citeType": "paragraph"
            }
        ]
    },
    {
        "dts:citeType": "poem",
        "dts:citeStructure": [
            {
                "dts:citeType": "line",
                "dts:citeStructure": [
                    {
                        "dts:citeType": "word"
                    }
                ]
            }
        ]
    }
]


def _context(ex):
    return jsonld.expand({
        "@context": {
            "dts": "https://w3id.org/dts/api#"
        },
        "dts:citeStructure": ex
    })[0][str(_dts.term("citeStructure"))]


class TestDtsCitation(TestCase):
    def test_ingest_multiple(self):
        """ Test a simple ingest """
        cite = DtsCitationSet.ingest(_context(_ex_1))
        children = {c.name: c for c in cite}

        self.assertEqual(2, cite.depth, "There should be 2 levels of citation")
        self.assertEqual(3, len(cite), "There should be 3 children")

        self.assertEqual(list(cite[-1]), [children["line"]], "Last level should contain line only")

        self.assertCountEqual(list(cite[-2]), [children["poem"], children["front"]], "-2 level  == level 0")
        self.assertCountEqual(list(cite[-2]), list(cite[0]), "-2 level  == level 0")

        self.assertEqual(cite.is_empty(), False, "The BaseCitationSet is not empty")
        self.assertEqual(cite.is_root(), True, "The BaseCitationSet is the root")

        self.assertEqual(children["line"].is_root(), False)
        self.assertEqual(children["line"].is_set(), True, "The Citation is set")
        self.assertEqual(children["line"].is_empty(), True, "The citation has no more levels")
        self.assertIs(children["line"].root, cite, "The root is tied to its children")

    def test_ingest_multiple_deeper(self):
        """ Test a simple ingest """
        cite = DtsCitationSet.ingest(_context(_ex_3))
        children = {c.name: c for c in cite}

        self.assertEqual(3, cite.depth, "There should be 3 levels of citation")
        self.assertEqual(5, len(cite), "There should be 5 children")

        self.assertEqual(list(cite[-1]), [children["word"]], "Last level should contain word only")
        self.assertEqual(list(cite[-1]), list(cite[2]), "-1 level == level 2")

        self.assertCountEqual(list(cite[-2]), [children["paragraph"], children["line"]], "-2 level  == level 1")
        self.assertCountEqual(list(cite[-2]), list(cite[1]), "-2 level  == level 1")

        self.assertCountEqual(list(cite[-3]), [children["front"], children["poem"]], "-3 level  == level 0")
        self.assertCountEqual(list(cite[-3]), list(cite[0]), "-3 level  == level 0")

        self.assertEqual(cite.is_empty(), False, "The BaseCitationSet is not empty")
        self.assertEqual(cite.is_root(), True, "The BaseCitationSet is the root")

        self.assertEqual(children["word"].is_root(), False)
        self.assertIs(children["word"].root, cite, "The root is tied to its children")

    def test_ingest_simple_line(self):
        """ Test a simple ingest """
        cite = DtsCitationSet.ingest(_context(_ex_2))
        children = {c.name: c for c in cite}

        self.assertEqual(2, cite.depth, "There should be 2 levels of citation")
        self.assertEqual(2, len(cite), "There should be 2 children")

        self.assertEqual(list(cite[-1]), [children["line"]], "Last level should contain line only")
        self.assertEqual(list(cite[-1]), list(cite[1]), "-1 level == level 1")

        self.assertCountEqual(list(cite[-2]), [children["poem"]], "-2 level  == level 0")
        self.assertCountEqual(list(cite[-2]), list(cite[0]), "-2 level  == level 0")

        self.assertIsInstance(cite, DtsCitationSet, "Root should be a DtsCitationSet")
        self.assertEqual([type(child) for child in cite.children], [DtsCitation], "Children should be DtsCitation")

        self.assertEqual(cite.is_empty(), False, "The BaseCitationSet is not empty")
        self.assertEqual(cite.is_root(), True, "The BaseCitationSet is the root")

        self.assertEqual(children["poem"].is_root(), False)
        self.assertIs(children["poem"].root, cite, "The root is tied to its children")
