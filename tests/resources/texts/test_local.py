# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest
from six import text_type as str
from io import open
import xmlunittest
import warnings
from lxml import etree
from copy import copy
import MyCapytain.resources.texts.local
import MyCapytain.resources.texts.encodings
import MyCapytain.common.reference
import MyCapytain.common.utils
import MyCapytain.errors


class TestLocalXMLTextImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test XML Implementation of resources found in local file """

    def setUp(self):
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.Text(
            resource=self.text,
            urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
        )
        self.treeroot = etree._ElementTree()

        with open("tests/testing_data/texts/text_or_xpath.xml") as f:
            self.text_complex = MyCapytain.resources.texts.local.Text(
                resource=f,
                urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            )

        with open("tests/testing_data/texts/seneca.xml") as f:
            self.seneca = MyCapytain.resources.texts.local.Text(
                resource=f
            )

    def tearDown(self):
        self.text.close()

    def testURN(self):
        """ Check that urn is set"""
        TEI = MyCapytain.resources.texts.local.Text(resource=self.TEI.xml,
                                                    urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(str(TEI.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")

    def testFindCitation(self):
        self.assertEqual(
            str(self.TEI.citation),
            '<tei:cRefPattern n="book" matchPattern="(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\\\'$1\\\'])"><tei:p>This pointer pattern extracts book</tei:p></tei:cRefPattern>'
        )
        self.assertEqual(
            str(self.TEI.citation.child),
            '<tei:cRefPattern n="poem" matchPattern="(\\w+)\.(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\\\'$1\\\']/tei:div[@n=\\\'$2\\\'])"><tei:p>This pointer pattern extracts poem</tei:p></tei:cRefPattern>'
        )
        self.assertEqual(
            str(self.TEI.citation.child.child),
            '<tei:cRefPattern n="line" matchPattern="(\\w+)\.(\\w+)\.(\\w+)" replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n=\\\'$1\\\']/tei:div[@n=\\\'$2\\\']/tei:l[@n=\\\'$3\\\'])"><tei:p>This pointer pattern extracts line</tei:p></tei:cRefPattern>'
        )

        self.assertEqual(len(self.TEI.citation), 3)

    def testFindComplexCitation(self):
        self.assertEqual(len(self.text_complex.citation), 2)

    def testCitationSetters(self):
        d = MyCapytain.common.reference.Citation()
        c = MyCapytain.common.reference.Citation(name="ahah",
                                                 refsDecl="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']",
                                                 child=None)
        b = MyCapytain.common.reference.Citation()
        a = MyCapytain.resources.texts.local.Text(citation=b)
        """ Test original setting """
        self.assertIs(a.citation, b)
        """ Test simple replacement """
        a.citation = d
        self.assertIs(a.citation, d)
        """ Test conversion """
        a.citation = c
        self.assertEqual(a.citation.name, "ahah")
        self.assertEqual(a.citation.child, None)
        self.assertEqual(a.citation.refsDecl, "/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']")
        self.assertEqual(a.citation.scope, "/tei:TEI/tei:text/tei:body/tei:div")
        self.assertEqual(a.citation.xpath, "/tei:div[@n='?']")

    def testValidReffs(self):
        # Test level 1
        self.assertEqual(list(map(lambda x: str(x), self.TEI.getValidReff())), ["1", "2"])
        # Test level 2
        self.assertEqual(list(map(lambda x: str(x), self.TEI.getValidReff(level=2)))[0], "1.pr")
        # Test level 3
        self.assertEqual(list(map(lambda x: str(x), self.TEI.getValidReff(level=3)))[0], "1.pr.1")
        self.assertEqual(list(map(lambda x: str(x), self.TEI.getValidReff(level=3)))[-1], "2.40.8")

        # Test with reference and level
        self.assertEqual(
            str(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1"), level=3)[1]),
            "2.1.2"
        )
        self.assertEqual(
            str(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1"), level=3)[-1]),
            "2.1.12"
        )
        self.assertEqual(
            self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.38-2.39"), level=3),
            ["2.38.1", "2.38.2", "2.39.1", "2.39.2"]
        )

        # Test with reference and level autocorrected because too small
        self.assertEqual(
            str(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1"), level=0)[-1]),
            "2.1.12",
            "Level should be autocorrected to len(citation) + 1"
        )
        self.assertEqual(
            str(self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1"), level=2)[-1]),
            "2.1.12",
            "Level should be autocorrected to len(citation) + 1 even if level == len(citation)"
        )

        self.assertEqual(
            self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1-2.2")),
            [
                '2.1.1', '2.1.2', '2.1.3', '2.1.4', '2.1.5', '2.1.6', '2.1.7', '2.1.8', '2.1.9', '2.1.10', '2.1.11',
                '2.1.12', '2.2.1', '2.2.2', '2.2.3', '2.2.4', '2.2.5', '2.2.6'
             ],
            "It could be possible to ask for range reffs children")

        self.assertEqual(
            self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1-2.2"), level=2),
            ['2.1', '2.2'],
            "It could be possible to ask for range References reference at the same level in between milestone")

        self.assertEqual(
            self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("1.38-2.2"), level=2),
            ['1.38', '1.39', '2.pr', '2.1', '2.2'],
            "It could be possible to ask for range References reference at the same level in between milestone across higher levels")

        self.assertEqual(
            self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("1.1.1-1.1.4"), level=3),
            ['1.1.1', '1.1.2', '1.1.3', '1.1.4'],
            "It could be possible to ask for range reffs in between at the same level cross higher level")

        # Test when already too deep
        self.assertEqual(
            self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.1.1"), level=3),
            [],
            "Asking for a level too deep should return nothing"
        )

        # Test wrong citation
        with self.assertRaises(KeyError):
            self.TEI.getValidReff(reference=MyCapytain.common.reference.Reference("2.hellno"), level=3)

    def test_nested_dict(self):
        """ Check the nested dict export of a local.Text object """
        nested = self.TEI.nested_dict(exclude=["tei:note"])
        self.assertEqual(nested["1"]["pr"]["1"], "Spero me secutum in libellis meis tale temperamen-",
                         "Check that dictionary path is well done")
        self.assertEqual(nested["1"]["12"]["1"], "Itur ad Herculeas gelidi qua Tiburis arces ",
                         "Check that dictionary path works on more than one passage")
        self.assertEqual(nested["2"]["pr"]["1"], "'Quid nobis' inquis 'cum epistula? parum enim tibi ",
                         "Check that different fist level works as well")
        self.assertEqual(nested["1"]["3"]["8"], "Ibis ab excusso missus in astra sago. ",
                         "Check that notes are removed ")
        self.assertEqual(
            [list(nested.keys()), list(nested["1"].keys())[:3], list(nested["2"]["pr"].keys())[:3]],
            [["1", "2"], ["pr", "1", "2"], ["sa", "1", "2"]],
            "Ensure that text keeps its order")

    def test_warning(self):
        with open("tests/testing_data/texts/duplicate_references.xml") as xml:
            text = MyCapytain.resources.texts.local.Text(resource=xml)
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            for i in [1, 2, 3]:
                text.getValidReff(level=i, _debug=True)

        self.assertEqual(len(w), 3, "There should be warning on each level")
        self.assertEqual(issubclass(w[-1].category, MyCapytain.errors.DuplicateReference), True,
                         "Warning should be DuplicateReference")
        self.assertEqual(str(w[0].message), "1", "Warning message should be list of duplicate")

    def test_wrong_main_scope(self):
        with open("tests/testing_data/texts/sample2.xml", "rb") as file:
            with self.assertRaises(MyCapytain.resources.texts.local.RefsDeclError):
                text = MyCapytain.resources.texts.local.Text(resource=file, autoreffs=True)

    def test_reffs(self):
        """ Check that every level is returned trough reffs property """
        self.assertEqual(("1" in list(map(lambda x: str(x), self.TEI.reffs))), True)
        self.assertEqual(("1.pr" in list(map(lambda x: str(x), self.TEI.reffs))), True)
        self.assertEqual(("2.40.8" in list(map(lambda x: str(x), self.TEI.reffs))), True)

    def test_complex_reffs(self):
        """ Test when there is a (something|something) xpath
        """
        self.assertEqual(("pr.1" in list(map(lambda x: str(x), self.text_complex.reffs))), True)

    def test_urn(self):
        """ Test setters and getters for urn """

        # Should work with string
        self.TEI.urn = "urn:cts:latinLit:tg.wk.v"
        self.assertEqual(isinstance(self.TEI.urn, MyCapytain.common.reference.URN), True)
        self.assertEqual(str(self.TEI.urn), "urn:cts:latinLit:tg.wk.v")

        # Test for URN
        self.TEI.urn = MyCapytain.common.reference.URN("urn:cts:latinLit:tg.wk.v2")
        self.assertEqual(isinstance(self.TEI.urn, MyCapytain.common.reference.URN), True)
        self.assertEqual(str(self.TEI.urn), "urn:cts:latinLit:tg.wk.v2")

        # Test it fails if not basestring or URN
        with self.assertRaises(TypeError):
            self.TEI.urn = 2

    def test_get_passage(self):
        self.TEI.parse()
        a = self.TEI.getPassage(["1", "pr", "2"], hypercontext=False)
        self.assertEqual(a.text(), "tum, ut de illis queri non possit quisquis de se bene ")
        # With reference
        a = self.TEI.getPassage(MyCapytain.common.reference.Reference("2.5.5"), hypercontext=False)
        self.assertEqual(a.text(), "Saepe domi non es, cum sis quoque, saepe negaris: ")

    def test_get_passage_autoparse(self):
        self.assertEqual(self.TEI._passages.resource, None)
        a = self.TEI.getPassage(MyCapytain.common.reference.Reference("2.5.5"), hypercontext=False)
        self.assertNotEqual(self.TEI._passages.resource, None)
        self.assertEqual(
            a.text(), "Saepe domi non es, cum sis quoque, saepe negaris: ",
            "Text are automatically parsed in GetPassage hypercontext = False"
        )

    def test_get_Passage_context_no_double_slash(self):
        """ Check that get Passage contexts return right information """
        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2"))
        str_simple = simple.tostring(encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.TEI.citation,
            autoreffs=True
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.2"), hypercontext=False).text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (One reference Passage)"
        )

        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.pr.7"))
        str_simple = simple.tostring(encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.TEI.citation,
            autoreffs=True
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.2"), hypercontext=False).text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level same parent range Passage)"
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.3"), hypercontext=False).text().strip(),
            "senserit, cum salva infimarum quoque personarum re-",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level same parent range Passage)"
        )
        self.assertEqual(
            list(map(lambda x: str(x), text.getValidReff(level=3))),
            ["1.pr.2", "1.pr.3", "1.pr.4", "1.pr.5", "1.pr.6", "1.pr.7"],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level same parent range Passage)"
        )

        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.1.6"))
        str_simple = simple.tostring(encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.TEI.citation,
            autoreffs=True
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.2"), hypercontext=False).text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level range Passage)"
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.1.6"), hypercontext=False).text().strip(),
            "Rari post cineres habent poetae.",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level range Passage)"
        )
        self.assertEqual(
            list(map(lambda x: str(x), text.getValidReff(level=3))),
            [
                "1.pr.2", "1.pr.3", "1.pr.4", "1.pr.5", "1.pr.6", "1.pr.7",
                "1.pr.8", "1.pr.9", "1.pr.10", "1.pr.11", "1.pr.12", "1.pr.13",
                "1.pr.14", "1.pr.15", "1.pr.16", "1.pr.17", "1.pr.18", "1.pr.19",
                "1.pr.20", "1.pr.21", "1.pr.22",
                "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.1.6",
            ],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Same level range Passage)"
        )

        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.2"))
        str_simple = simple.tostring(encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.TEI.citation,
            autoreffs=True
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.pr.2"), hypercontext=False).text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.1.6"), hypercontext=False).text().strip(),
            "Rari post cineres habent poetae.",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            list(map(lambda x: str(x), text.getValidReff(level=3))),
            [
                "1.pr.2", "1.pr.3", "1.pr.4", "1.pr.5", "1.pr.6", "1.pr.7",
                "1.pr.8", "1.pr.9", "1.pr.10", "1.pr.11", "1.pr.12", "1.pr.13",
                "1.pr.14", "1.pr.15", "1.pr.16", "1.pr.17", "1.pr.18", "1.pr.19",
                "1.pr.20", "1.pr.21", "1.pr.22",
                "1.1.1", "1.1.2", "1.1.3", "1.1.4", "1.1.5", "1.1.6",
                '1.2.1', '1.2.2', '1.2.3', '1.2.4', '1.2.5', '1.2.6', '1.2.7', '1.2.8'
            ],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )

    def test_get_passage_with_list(self):
        """ In range, passage in between could be removed from the original text by error
        """
        simple = self.TEI.getPassage(["1", "pr", "2"])
        self.assertEqual(
            simple.text().strip(),
            "tum, ut de illis queri non possit quisquis de se bene",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )

    def test_type_accepted_reference_validreff(self):
        """ In range, passage in between could be removed from the original text by error
        """
        with self.assertRaises(TypeError):
            self.TEI.getValidReff(reference=["1", "pr", "2", "5"])

    def test_citation_length_error(self):
        """ In range, passage in between could be removed from the original text by error
        """
        with self.assertRaises(ReferenceError):
            self.TEI.getPassage(["1", "pr", "2", "5"])

    def test_ensure_passage_is_not_removed(self):
        """ In range, passage in between could be removed from the original text by error
        """
        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr.1-1.2.5"))
        orig_refs = self.TEI.getValidReff(level=3)
        self.assertIn("1.pr.1", orig_refs)
        self.assertIn("1.1.1", orig_refs)
        self.assertIn("1.2.4", orig_refs)
        self.assertIn("1.2.5", orig_refs)

        simple = self.TEI.getPassage(MyCapytain.common.reference.Reference("1.pr-1.2"))
        orig_refs = self.TEI.getValidReff(level=3)
        self.assertIn("1.pr.1", orig_refs)
        self.assertIn("1.1.1", orig_refs)
        self.assertIn("1.2.4", orig_refs)
        self.assertIn("1.2.5", orig_refs)

    def test_get_passage_hypercontext_complex_xpath(self):
        simple = self.text_complex.getPassage(MyCapytain.common.reference.Reference("pr.1-1.2"))
        str_simple = simple.tostring(encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.text_complex.citation,
            autoreffs=True
        )
        self.assertIn(
            "Pervincis tandem",
            text.getPassage(MyCapytain.common.reference.Reference("pr.1"), hypercontext=False).text(
                exclude=["tei:note"]).strip(),
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1.2"), hypercontext=False).text().strip(),
            "lusimus quos in Suebae gratiam virgunculae,",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            list(map(lambda x: str(x), text.getValidReff(level=2))),
            [
                "pr.1", "1.1", "1.2"
            ],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )

    def test_Text_text_function(self):
        simple = self.seneca.getPassage(MyCapytain.common.reference.Reference("1"))
        str_simple = simple.tostring(encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.seneca.citation,
            autoreffs=True
        )
        self.assertEqual(
            text.text(exclude=["tei:note"]).strip(),
            "Di coniugales tuque genialis tori,",
            "Ensure text methods works on Text object"
        )

    def test_get_passage_hypercontext_double_slash_xpath(self):
        simple = self.seneca.getPassage(MyCapytain.common.reference.Reference("1-10"))
        str_simple = simple.tostring(encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.seneca.citation,
            autoreffs=True
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1"), hypercontext=False).text(
                exclude=["tei:note"]).strip(),
            "Di coniugales tuque genialis tori,",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("10"), hypercontext=False).text().strip(),
            "aversa superis regna manesque impios",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            list(map(lambda x: str(x), text.getValidReff(level=1))),
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )

        simple = self.seneca.getPassage(MyCapytain.common.reference.Reference("1"))
        str_simple = simple.tostring(encoding=str)
        text = MyCapytain.resources.texts.local.Text(
            resource=str_simple,
            citation=self.seneca.citation,
            autoreffs=True
        )
        self.assertEqual(
            text.getPassage(MyCapytain.common.reference.Reference("1"), hypercontext=False).text(
                exclude=["tei:note"]).strip(),
            "Di coniugales tuque genialis tori,",
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )
        self.assertEqual(
            list(map(lambda x: str(x), text.getValidReff(level=1))),
            ["1"],
            "Ensure passage finding with context is fully TEI / Capitains compliant (Different level range Passage)"
        )


class TestLocalXMLPassageImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):
    """ Test passage implementation """

    def setUp(self):
        self.URN = MyCapytain.common.reference.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.URN_2 = MyCapytain.common.reference.URN("urn:cts:latinLit:phi1294.phi002.perseus-lat3")
        self.text = open("tests/testing_data/texts/sample.xml", "rb")
        self.TEI = MyCapytain.resources.texts.local.Text(resource=self.text)

    def tearDown(self):
        self.text.close()

    def test_urn(self):
        """ Test URN and ids getters/setters """

        a = MyCapytain.resources.texts.local.Passage()

        # ~Test simple set up
        a.urn = self.URN
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        # Test update on ID update
        a.reference = "1.pr.1"
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        # Should keep the ID if URN changes
        a.urn = self.URN_2
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat3:1.pr.1")
        # Test init
        a = MyCapytain.resources.texts.local.Passage(urn=self.URN)
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        # Test init with id and URN
        a = MyCapytain.resources.texts.local.Passage(urn=self.URN, reference=["1", "pr", "1"])
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        # Should raise error if not URN for consistency
        with self.assertRaises(TypeError):
            a.urn = 1
        # Should work with plain text
        a = MyCapytain.resources.texts.local.Passage()
        a.urn = "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1"
        self.assertEqual(str(a.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.pr.1")
        self.assertEqual(str(a.reference), "1.pr.1")
        # This should affect id !
        # Test Id value on init
        a = MyCapytain.resources.texts.local.Passage(reference=["1", "pr", "1"])
        self.assertEqual(str(a.reference), "1.pr.1")

    def test_next(self):
        """ Test next property """
        # Normal passage checking
        self.TEI.parse()
        p = self.TEI.getPassage(["1", "pr", "1"], hypercontext=False)
        self.assertEqual(str(p.next.reference), "1.pr.2")

        # End of lowest level passage checking but not end of parent level
        p = self.TEI.getPassage(["1", "pr", "22"], hypercontext=False)
        self.assertEqual(str(p.next.reference), "1.1.1")

        # End of lowest level passage and end of parent level
        p = self.TEI.getPassage(["1", "39", "8"], hypercontext=False)
        self.assertEqual(str(p.next.reference), "2.pr.sa")

        # Last line should always be None
        p = self.TEI.getPassage(["2", "40", "8"], hypercontext=False)
        self.assertIsNone(p.next)
        p = self.TEI.getPassage(["2", "40"], hypercontext=False)
        self.assertIsNone(p.next)
        p = self.TEI.getPassage(["2"], hypercontext=False)
        self.assertIsNone(p.next)

    def test_children(self):
        """ Test children property """
        # Normal children checking
        with open("tests/testing_data/texts/sample.xml", "rb") as text:
            self.TEI = MyCapytain.resources.texts.local.Text(resource=text, autoreffs=True)

            p = self.TEI.getPassage(["1", "pr"], hypercontext=False)
            self.assertEqual(str(p.children["1.pr.1"].reference), "1.pr.1")

            p = self.TEI.getPassage(["1", "pr", "1"], hypercontext=False)
            self.assertEqual(len(p.children), 0)

    def test_first(self):
        """ Test first property """
        # Test when there is one
        self.TEI.parse()
        p = self.TEI.getPassage(["1", "pr"], hypercontext=False)
        self.assertEqual(str(p.first.reference), "1.pr.1")
        # #And failing when no first
        p = self.TEI.getPassage(["1", "pr", "1"], hypercontext=False)
        self.assertEqual(p.first, None)

    def test_last(self):
        """ Test last property """
        self.TEI.parse()
        # Test when there is one
        p = self.TEI.getPassage(["1", "pr"], hypercontext=False)
        self.assertEqual(str(p.last.reference), "1.pr.22")
        # #And failing when no last
        p = self.TEI.getPassage(["1", "pr", "1"], hypercontext=False)
        self.assertEqual(p.last, None)

    def test_prev(self):
        """ Test prev property """
        self.TEI.parse()
        # Normal passage checking
        p = self.TEI.getPassage(["2", "40", "8"], hypercontext=False)
        self.assertEqual(str(p.prev.reference), "2.40.7")
        p = self.TEI.getPassage(["2", "40"], hypercontext=False)
        self.assertEqual(str(p.prev.reference), "2.39")
        p = self.TEI.getPassage(["2"], hypercontext=False)
        self.assertEqual(str(p.prev.reference), "1")

        # test failing passage
        p = self.TEI.getPassage(["1", "pr", "1"], hypercontext=False)
        self.assertEqual(p.prev, None)
        p = self.TEI.getPassage(["1", "pr"], hypercontext=False)
        self.assertEqual(p.prev, None)
        p = self.TEI.getPassage(["1"], hypercontext=False)
        self.assertEqual(p.prev, None)

        # First child should get to parent's prev last child
        p = self.TEI.getPassage(["1", "1", "1"], hypercontext=False)
        self.assertEqual(str(p.prev.reference), "1.pr.22")

        # Beginning of lowest level passage and beginning of parent level
        p = self.TEI.getPassage(["2", "pr", "sa"], hypercontext=False)
        self.assertEqual(str(p.prev.reference), "1.39.8")


class TestPassageRange(unittest.TestCase):
    def setUp(self):
        with open("tests/testing_data/texts/sample.xml", "rb") as text:
            self.text = MyCapytain.resources.texts.local.Text(
                resource=text, urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"
            )
        self.passage = self.text.getPassage(MyCapytain.common.reference.Reference("1.pr.2-1.pr.7"))

    def test_errors(self):
        """ Ensure that some results throws errors according to some standards """
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.2-1.2")
        )
        with self.assertRaises(MyCapytain.errors.InvalidSiblingRequest, msg="Different range passage have no siblings"):
            a = DifferentRangePassage.nextId

        with self.assertRaises(MyCapytain.errors.InvalidSiblingRequest, msg="Different range passage have no siblings"):
            a = DifferentRangePassage.prevId

    def test_prevnext_on_first_passage(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.1-1.2.1")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.2.2-1.5.2",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            DifferentRangePassage.prevId, None,
            "Prev reff should be none if we are on the first passage of the text"
        )

    def test_prevnext_on_close_to_first_passage(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.10-1.2.1")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.2.2-1.4.1",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "1.pr.1-1.pr.9",
            "Prev reff should start at the beginning of the text, no matter the length of the reference"
        )

    def test_prevnext_on_last_passage(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.39.2-2.40.8")
        )
        self.assertEqual(
            DifferentRangePassage.nextId, None,
            "Next reff should be none if we are on the last passage of the text"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "2.37.6-2.39.1",
            "Prev reff should be the same length as sibling"
        )

    def test_prevnext_on_close_to_last_passage(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.39.2-2.40.5")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "2.40.6-2.40.8",
            "Next reff should finish at the end of the text, no matter the length of the reference"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "2.37.9-2.39.1",
            "Prev reff should be the same length as sibling"
        )

    def test_prevnext(self):
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.5-1.pr.6")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.pr.7-1.pr.8",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "1.pr.3-1.pr.4",
            "Prev reff should be the same length as sibling"
        )
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr.5")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.pr.6",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "1.pr.4",
            "Prev reff should be the same length as sibling"
        )

        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("1.pr")
        )
        self.assertEqual(
            str(DifferentRangePassage.nextId), "1.1",
            "Next reff should be the same length as sibling"
        )
        self.assertEqual(
            DifferentRangePassage.prevId, None,
            "Prev reff should be None when at the start"
        )
        
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.40")
        )
        self.assertEqual(
            str(DifferentRangePassage.prevId), "2.39",
            "Prev reff should be the same length as sibling"
        )
        self.assertEqual(
            DifferentRangePassage.nextId, None,
            "Next reff should be None when at the start"
        )

    def test_first_list(self):
        """ Check that Passage can give information about first and end"""
        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.39")
        )
        self.assertEqual(
            str(DifferentRangePassage.firstId), "2.39.1",
            "First reff should be the first"
        )
        self.assertEqual(
            str(DifferentRangePassage.lastId), "2.39.2",
            "Last reff should be the last"
        )

        DifferentRangePassage = self.text.getPassage(
            MyCapytain.common.reference.Reference("2.39-2.40")
        )
        self.assertEqual(
            str(DifferentRangePassage.firstId), "2.39.1",
            "First reff should be the first"
        )
        self.assertEqual(
            str(DifferentRangePassage.lastId), "2.40.8",
            "Last reff should be the last"
        )