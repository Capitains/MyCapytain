import unittest

from six import text_type as str
from MyCapytain.common.utils import xmlparser
from MyCapytain.common.reference import Reference, URN, Citation


class TestReferenceImplementation(unittest.TestCase):

    """ Test how reference reacts """

    def test_str_function(self):
        a = Reference("1-1")
        self.assertEqual(str(a), "1-1")

    def test_len_ref(self):
        a = Reference("1.1@Achilles[0]-1.10@Atreus[3]")
        self.assertEqual(len(a), 2)
        a = Reference("1.1.1")
        self.assertEqual(len(a), 3)

    def test_highest(self):
        self.assertEqual(
            str((Reference("1.1-1.2.8")).highest), "1.1",
            "1.1 is higher"
        )
        self.assertEqual(
            str((Reference("1.1-2")).highest), "2",
            "2 is higher"
        )

    def test_properties(self):
        a = Reference("1.1@Achilles-1.10@Atreus[3]")
        self.assertEqual(a.start, "1.1@Achilles")
        self.assertEqual(Reference(a.start).list, ["1", "1"])
        self.assertEqual(Reference(a.start).subreference[0], "Achilles")
        self.assertEqual(a.end, "1.10@Atreus[3]")
        self.assertEqual(Reference(a.end).list, ["1", "10"])
        self.assertEqual(Reference(a.end).subreference[1], 3)
        self.assertEqual(Reference(a.end).subreference, ("Atreus", 3))

    def test_Unicode_Support(self):
        a = Reference("1.1@καὶ[0]-1.10@Ἀλκιβιάδου[3]")
        self.assertEqual(a.start, "1.1@καὶ[0]")
        self.assertEqual(Reference(a.start).list, ["1", "1"])
        self.assertEqual(Reference(a.start).subreference[0], "καὶ")
        self.assertEqual(a.end, "1.10@Ἀλκιβιάδου[3]")
        self.assertEqual(Reference(a.end).list, ["1", "10"])
        self.assertEqual(Reference(a.end).subreference[1], 3)
        self.assertEqual(Reference(a.end).subreference, ("Ἀλκιβιάδου", 3))

    def test_NoWord_Support(self):
        a = Reference("1.1@[0]-1.10@Ἀλκιβιάδου[3]")
        self.assertEqual(str(a.start), "1.1@[0]")
        self.assertEqual(Reference(a.start).subreference[0], "")
        self.assertEqual(Reference(a.start).subreference[1], 0)

    def test_No_End_Support(self):
        a = Reference("1.1@[0]")
        self.assertEqual(a.end, None)
        self.assertEqual(a.start, "1.1@[0]")
        self.assertEqual(Reference(a.start).subreference[0], "")
        self.assertEqual(Reference(a.start).subreference[1], 0)

    def test_equality(self):
        a = Reference("1.1@[0]")
        b = Reference("1.1@[0]")
        c = Reference("1.1@[1]")
        d = "1.1@[0]"
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)

    def test_get_parent(self):
        a = Reference("1.1")
        b = Reference("1")
        c = Reference("1.1-2.3")
        d = Reference("1.1-1.2")
        e = Reference("1.1@Something[0]-1.2@SomethingElse[2]")
        f = Reference("1-2")

        self.assertEqual(str(a.parent), "1")
        self.assertEqual(b.parent, None)
        self.assertEqual(str(c.parent), "1-2")
        self.assertEqual(str(d.parent), "1")
        self.assertEqual(str(e.parent), "1@Something[0]-1@SomethingElse[2]")
        self.assertEqual(f.parent, None)


class TestURNImplementation(unittest.TestCase):

    """ Test how reference reacts """

    def test_str_function(self):
        a = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(str(a), "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")

    def test_properties(self):
        a = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a.urn_namespace, "cts")
        a.urn_namespace = "dts"
        self.assertEqual(a.urn_namespace, "dts")
        self.assertEqual(a.namespace, "greekLit")
        self.assertEqual(a.textgroup, "tlg0012")
        self.assertEqual(a.work, "tlg001")
        self.assertEqual(a.version, "mth-01")
        self.assertEqual(a.reference, Reference("1.1@Achilles-1.10@the[2]"))

    def test_upTo(self):
        a = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a.upTo(URN.COMPLETE), "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a.upTo(URN.NAMESPACE), "urn:cts:greekLit")
        self.assertEqual(a.upTo(URN.TEXTGROUP), "urn:cts:greekLit:tlg0012")
        self.assertEqual(a.upTo(URN.WORK), "urn:cts:greekLit:tlg0012.tlg001")
        self.assertEqual(a.upTo(URN.VERSION), "urn:cts:greekLit:tlg0012.tlg001.mth-01")
        self.assertEqual(a.upTo(URN.PASSAGE), "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        self.assertEqual(a.upTo(URN.PASSAGE_START), "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles")
        self.assertEqual(a.upTo(URN.PASSAGE_END), "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.10@the[2]")

    def test_equality(self):
        a = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        b = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]")
        c = URN("urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[3]")
        d = "urn:cts:greekLit:tlg0012.tlg001.mth-01:1.1@Achilles-1.10@the[2]"
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)

    def test_full_emptiness(self):
        a = URN("urn:cts:greekLit")
        self.assertEqual(str(a), "urn:cts:greekLit")
        self.assertEqual(a.upTo(URN.COMPLETE), "urn:cts:greekLit")
        self.assertEqual(a.upTo(URN.NAMESPACE), "urn:cts:greekLit")
        self.assertIsNone(a.textgroup)
        self.assertIsNone(a.work)
        self.assertIsNone(a.version)
        self.assertIsNone(a.reference)

    def test_from_textgroup_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup")
        self.assertEqual(a.upTo(URN.COMPLETE), "urn:cts:greekLit:textgroup")
        self.assertEqual(str(a), "urn:cts:greekLit:textgroup")
        self.assertEqual(a.upTo(URN.NAMESPACE), "urn:cts:greekLit")
        self.assertEqual(a.upTo(URN.TEXTGROUP), "urn:cts:greekLit:textgroup")
        self.assertIsNone(a.work)
        self.assertIsNone(a.version)
        self.assertIsNone(a.reference)

    def test_set(self):
        a = URN("urn:cts:greekLit:textgroup")
        a.textgroup = "tg"
        self.assertEqual(a.textgroup, "tg")
        self.assertEqual(str(a), "urn:cts:greekLit:tg")
        a.namespace = "ns"
        self.assertEqual(a.namespace, "ns")
        self.assertEqual(str(a), "urn:cts:ns:tg")
        a.work = "wk"
        self.assertEqual(a.work, "wk")
        self.assertEqual(str(a), "urn:cts:ns:tg.wk")
        a.reference = "1-2"
        self.assertEqual(a.reference, Reference("1-2"))
        self.assertEqual(str(a), "urn:cts:ns:tg.wk:1-2")
        a.version = "vs"
        self.assertEqual(a.version, "vs")
        self.assertEqual(str(a), "urn:cts:ns:tg.wk.vs:1-2")

    def test_from_work_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup.work")
        self.assertEqual(str(a), "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a.upTo(URN.COMPLETE), "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a.upTo(URN.NAMESPACE), "urn:cts:greekLit")
        self.assertEqual(a.upTo(URN.TEXTGROUP), "urn:cts:greekLit:textgroup")
        self.assertEqual(a.upTo(URN.WORK), "urn:cts:greekLit:textgroup.work")
        self.assertIsNone(a.version)
        self.assertIsNone(a.reference)

    def test_from_text_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup.work.text")
        self.assertEqual(str(a), "urn:cts:greekLit:textgroup.work.text")
        self.assertEqual(a.upTo(URN.COMPLETE), "urn:cts:greekLit:textgroup.work.text")
        self.assertEqual(a.upTo(URN.NAMESPACE), "urn:cts:greekLit")
        self.assertEqual(a.upTo(URN.TEXTGROUP), "urn:cts:greekLit:textgroup")
        self.assertEqual(a.upTo(URN.WORK), "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a.upTo(URN.VERSION), "urn:cts:greekLit:textgroup.work.text")
        self.assertIsNone(a.reference)

    def test_no_end_text_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup.work.text:1")
        self.assertEqual(str(a), "urn:cts:greekLit:textgroup.work.text:1")
        self.assertEqual(a.upTo(URN.COMPLETE), "urn:cts:greekLit:textgroup.work.text:1")
        self.assertEqual(a.upTo(URN.NAMESPACE), "urn:cts:greekLit")
        self.assertEqual(a.upTo(URN.TEXTGROUP), "urn:cts:greekLit:textgroup")
        self.assertEqual(a.upTo(URN.WORK), "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a.upTo(URN.VERSION), "urn:cts:greekLit:textgroup.work.text")
        self.assertEqual(a.upTo(URN.PASSAGE), "urn:cts:greekLit:textgroup.work.text:1")
        self.assertEqual(a.upTo(URN.NO_PASSAGE), "urn:cts:greekLit:textgroup.work.text")
        self.assertEqual(a.reference, Reference("1"))
        self.assertIsNone(a.reference.end)

    def test_missing_text_in_passage_emptiness(self):
        a = URN("urn:cts:greekLit:textgroup.work:1-2")
        self.assertEqual(str(a), "urn:cts:greekLit:textgroup.work:1-2")
        self.assertEqual(a.upTo(URN.COMPLETE), "urn:cts:greekLit:textgroup.work:1-2")
        self.assertEqual(a.upTo(URN.NAMESPACE), "urn:cts:greekLit")
        self.assertEqual(a.upTo(URN.TEXTGROUP), "urn:cts:greekLit:textgroup")
        self.assertEqual(a.upTo(URN.WORK), "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a.upTo(URN.NO_PASSAGE), "urn:cts:greekLit:textgroup.work")
        self.assertEqual(a.upTo(URN.PASSAGE), "urn:cts:greekLit:textgroup.work:1-2")
        self.assertEqual(a.upTo(URN.PASSAGE_START), "urn:cts:greekLit:textgroup.work:1")
        self.assertEqual(a.upTo(URN.PASSAGE_END), "urn:cts:greekLit:textgroup.work:2")
        self.assertEqual(a.reference, Reference("1-2"))
        self.assertEqual(a.reference.start, "1")
        self.assertEqual(a.reference.end, "2")
        self.assertIsNone(a.version)

    def test_warning_on_empty(self):
        with self.assertRaises(ValueError):
            a = URN("urn:cts")
        with self.assertRaises(KeyError):
            a = URN("urn:cts:ns:tg.work:1")
            a.upTo(URN.VERSION)

    def test_len(self):
        a = URN("urn:cts:greekLit")
        self.assertEqual(len(a), 2)

    def test_greater(self):
        a = URN("urn:cts:greekLit")
        b = URN("urn:cts:greekLit:textgroup")
        self.assertGreater(b, a)

    def test_lower(self):
        a = URN("urn:cts:greekLit")
        b = URN("urn:cts:greekLit:textgroup")
        self.assertEqual(a < b, True)

    def test_set(self):
        a = URN("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        a.reference = Reference("1.1")
        self.assertEqual(str(a), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:1.1")
        a.reference = "2.2"
        self.assertEqual(str(a), "urn:cts:latinLit:phi1294.phi002.perseus-lat2:2.2")
        a.version = "perseus-eng2"
        self.assertEqual(str(a), "urn:cts:latinLit:phi1294.phi002.perseus-eng2:2.2")
        a.work = "phi001"
        self.assertEqual(str(a), "urn:cts:latinLit:phi1294.phi001.perseus-eng2:2.2")
        a.textgroup = "phi1293"
        self.assertEqual(str(a), "urn:cts:latinLit:phi1293.phi001.perseus-eng2:2.2")
        a.namespace = "greekLit"
        self.assertEqual(str(a), "urn:cts:greekLit:phi1293.phi001.perseus-eng2:2.2")


class TestCitation(unittest.TestCase):
    """ Test the citation object """
    def test_updateRefsdecl(self):
        c = Citation(
            name="line",
            scope="/TEI/text/body/div/div[@n=\"?\"]",
            xpath="//l[@n=\"?\"]"
        )
        self.assertEqual(c.refsDecl, "/TEI/text/body/div/div[@n=\"$1\"]//l[@n=\"$2\"]")

    def test_updateRefsdecl_and(self):
        c = Citation(
            name="line",
            refsDecl="/TEI/text/body/div/div[@n=\"?\" and @subtype='edition']/l[@n=\"?\"]"
        )
        self.assertEqual(c.refsDecl, "/TEI/text/body/div/div[@n=\"?\" and @subtype='edition']/l[@n=\"?\"]")

    def test_updateScopeXpath(self):
        c = Citation(
            name="line",
            refsDecl="/TEI/text/body/div/div[@n=\"$1\"]//l[@n=\"$2\"]"
        )
        self.assertEqual(c.scope, "/TEI/text/body/div/div[@n=\"?\"]")
        self.assertEqual(c.xpath, "//l[@n=\"?\"]")

    def test_or_in_xpath(self):
        """ Test that the xpath and scope generation accepts or xpath expression in form of "|" or " or "
        """
        a = Citation(
            name="line",
            refsDecl="/TEI/text/body/div/div[@n=\"$1\"]/*[self::tei:l or self::tei:p][@n=\"$2\"]"
        )
        b = Citation(
            name="line",
            refsDecl="/TEI/text/body/div/div[@n=\"$1\"]/*[self::tei:l or self::tei:p][@n=\"$2\"]"
        )
        c = Citation(
            name="line",
            refsDecl="/TEI/text/body/div/*[self::tei:l or self::tei:p][@n=\"$1\"]"
        )
        self.assertEqual(a.scope, "/TEI/text/body/div/div[@n=\"?\"]")
        self.assertEqual(a.xpath, "/*[self::tei:l or self::tei:p][@n=\"?\"]")
        self.assertEqual(a.fill(["1", "2"], xpath=False), "/TEI/text/body/div/div[@n='1']/*[self::tei:l or self::tei:p][@n='2']")

        self.assertEqual(b.scope, "/TEI/text/body/div/div[@n=\"?\"]")
        self.assertEqual(b.xpath, "/*[self::tei:l or self::tei:p][@n=\"?\"]")

        self.assertEqual(c.scope, "/TEI/text/body/div")
        self.assertEqual(c.xpath, "/*[self::tei:l or self::tei:p][@n=\"?\"]")

    def test_name(self):
        c = Citation(
            name="line"
        )
        self.assertEqual(c.name, "line")

    def test_child(self):
        c = Citation(
            name="line"
        )
        b = Citation(
            name="poem",
            child=c
        )
        self.assertEqual(b.child, c)

    def test_iter(self):
        c = Citation(
            name="line"
        )
        b = Citation(
            name="poem",
            child=c
        )
        a = Citation(
            name="book",
            child=b
        )
        self.assertEqual([e for e in a], [a, b, c])

    def test_len(self):
        c = Citation(
            name="line"
        )
        b = Citation(
            name="poem",
            child=c
        )
        a = Citation(
            name="book",
            child=b
        )
        self.assertEqual(len(a), 3)

    def test_get_item(self):
        c = Citation(
            name="line"
        )
        b = Citation(
            name="poem",
            child=c
        )
        a = Citation(
            name="book",
            child=b
        )
        self.assertEqual(a[-1], c, "Last citation is C")
        self.assertEqual(a[2], c, "Third citation is C")
        self.assertEqual(a[0], a, "First citation is A")
        self.assertEqual(a[1], b, "Second citation is B")
        with self.assertRaises(KeyError, msg="XmlCtsCitation is out of bound"):
            a[8]

    def test_fill(self):
        c = Citation(
            name="line",
            scope="/TEI/text/body/div/div[@n=\"?\"]",
            xpath="//l[@n=\"?\"]"
        )
        self.assertEqual(c.fill(Reference("1.2")), "/TEI/text/body/div/div[@n='1']//l[@n='2']")
        self.assertEqual(c.fill(Reference("1.1")), "/TEI/text/body/div/div[@n='1']//l[@n='1']")
        self.assertEqual(c.fill(None), "/TEI/text/body/div/div[@n]//l[@n]")
        self.assertEqual(c.fill("1", xpath=True), "//l[@n='1']")
        self.assertEqual(c.fill("2", xpath=True), "//l[@n='2']")
        self.assertEqual(c.fill(None, xpath=True), "//l[@n]")
        self.assertEqual(c.fill([None, None]), "/TEI/text/body/div/div[@n]//l[@n]")
        self.assertEqual(c.fill(["1", None]), "/TEI/text/body/div/div[@n='1']//l[@n]")

    def test_ingest_and_match(self):
        """ Ensure matching and parsing XML works correctly """
        xml = xmlparser("""<TEI xmlns="http://www.tei-c.org/ns/1.0">
         <refsDecl n="CTS">
            <cRefPattern n="line"
                         matchPattern="(\w+).(\w+).(\w+)"
                         replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']/tei:div[@n='$2']/tei:l[@n='$3'])">
                <p>This pointer pattern extracts book and poem and line</p>
            </cRefPattern>
            <cRefPattern n="poem"
                         matchPattern="(\w+).(\w+)"
                         replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']/tei:div[@n='$2'])">
                <p>This pointer pattern extracts book and poem</p>
            </cRefPattern>
            <cRefPattern n="book"
                         matchPattern="(\w+)"
                         replacementPattern="#xpath(/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1'])">
                <p>This pointer pattern extracts book</p>
            </cRefPattern>
        </refsDecl>
        </TEI>""")
        citation = Citation.ingest(xml)
        # The citation that should be returned is the root
        self.assertEqual(citation.name, "book", "Name should have been parsed")
        self.assertEqual(citation.child.name, "poem", "Name of child should have been parsed")
        self.assertEqual(citation.child.child.name, "line", "Name of descendants should have been parsed")

        self.assertEqual(citation.is_root, True, "Root should be true on root")
        self.assertEqual(citation.match("1.2"), citation.child, "Matching should make use of root matching")
        self.assertEqual(citation.match("1.2.4"), citation.child.child, "Matching should make use of root matching")
        self.assertEqual(citation.match("1"), citation, "Matching should make use of root matching")

        self.assertEqual(citation.child.match("1.2").name, "poem", "Matching should retrieve poem at 2nd level")
        self.assertEqual(citation.child.match("1.2.4").name, "line", "Matching should retrieve line at 3rd level")
        self.assertEqual(citation.child.match("1").name, "book", "Matching retrieve book at 1st level")

        citation = citation.child
        self.assertEqual(citation.child.match("1.2").name, "poem", "Matching should retrieve poem at 2nd level")
        self.assertEqual(citation.child.match("1.2.4").name, "line", "Matching should retrieve line at 3rd level")
        self.assertEqual(citation.child.match("1").name, "book", "Matching retrieve book at 1st level")
