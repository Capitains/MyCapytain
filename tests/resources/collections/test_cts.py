# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from copy import deepcopy
from io import open, StringIO
from operator import attrgetter

import lxml.etree as etree
import six
import xmlunittest

from MyCapytain.common.utils import Mimetypes
from MyCapytain.resources.collections.cts import *


class XML_Compare(object):
    """
    Original https://gist.github.com/dalelane/a0514b2e283a882d9ef3
    """
    @staticmethod
    def sortbyid(elem):
        id = elem.get('urn') or elem.get("xml:lang")
        if id:
            try:
                return str(id)
            except ValueError:
                return ""
        return ""

    @staticmethod
    def sortbytext(elem):
        text = elem.text
        if text:
            return text
        else:
            return ''

    @staticmethod
    def sortAttrs(item, sorteditem):
        attrkeys = sorted(item.keys())
        for key in attrkeys:
            sorteditem.set(key, item.get(key))

    @staticmethod
    def sortElements(items, newroot):
        # The intended sort order is to sort by XML element name
        #  If more than one element has the same name, we want to
        #   sort by their text contents.
        #  If more than one element has the same name and they do
        #   not contain any text contents, we want to sort by the
        #   value of their ID attribute.
        #  If more than one element has the same name, but has
        #   no text contents or ID attribute, their order is left
        #   unmodified.
        #
        # We do this by performing three sorts in the reverse order
        items = sorted(items, key=XML_Compare.sortbyid)
        items = sorted(items, key=XML_Compare.sortbytext)
        items = sorted(items, key=attrgetter('tag'))

        # Once sorted, we sort each of the items
        for item in items:
            # Create a new item to represent the sorted version
            #  of the next item, and copy the tag name and contents
            newitem = etree.Element(item.tag)
            if item.text and item.text.isspace() == False:
                newitem.text = item.text

            # Copy the attributes (sorted by key) to the new item
            XML_Compare.sortAttrs(item, newitem)

            # Copy the children of item (sorted) to the new item
            XML_Compare.sortElements(list(item), newitem)

            # Append this sorted item to the sorted root
            newroot.append(newitem)

    @staticmethod
    def sortString(str_xml):
        # parse the XML file and get a pointer to the top
        xmlroot = etree.parse(StringIO(str_xml)).getroot()

        # create a new XML element that will be the top of
        #  the sorted copy of the XML file
        newxmlroot = etree.Element(xmlroot.tag)

        # create the sorted copy of the XML file
        XML_Compare.sortAttrs(xmlroot, newxmlroot)
        XML_Compare.sortElements(list(xmlroot), newxmlroot)

        # write the sorted XML file to the temp file
        newtree = etree.ElementTree(newxmlroot)

        return etree.tostring(newtree, encoding=str, pretty_print=True)


def compareSTR(one, other):
    return XML_Compare.sortString(one.replace("\n", "")), XML_Compare.sortString(other.replace("\n", ""))


def compareXML(one, other):
    parser = etree.XMLParser(remove_blank_text=True)
    return (
        etree.tostring(etree.fromstring(etree.tostring(one, encoding=str).replace("\n", ""), parser), method="c14n"),
        etree.tostring(etree.fromstring(other.replace("\n", ""), parser), method="c14n")
    )


class TestXMLImplementation(unittest.TestCase, xmlunittest.XmlTestMixin):

    """ Test XML Implementation of resources Endpoint request making """

    def setUp(self):
        self.getCapabilities = open("tests/testing_data/cts/getCapabilities.xml", "r")
        self.ed = """<ti:edition urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:label xml:lang='eng'>Epigrammata Label</ti:label>
<ti:label xml:lang='fre'>Epigrammes Label</ti:label>
<ti:description xml:lang='eng'>W. Heraeus</ti:description>
<ti:description xml:lang='fre'>G. Heraeus</ti:description>
<ti:online></ti:online>
</ti:edition>""".replace("\n", "")

        self.tr = """<ti:translation xml:lang='eng' urn='urn:cts:latinLit:phi1294.phi002.perseus-eng2' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:label xml:lang='eng'>Epigrammata</ti:label>
<ti:description xml:lang='eng'>M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus</ti:description>
<ti:online></ti:online>
</ti:translation>""".replace("\n", "")

        self.wk = """<ti:work xml:lang='lat' urn='urn:cts:latinLit:phi1294.phi002' groupUrn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:title xml:lang='eng'>Epigrammata</ti:title>
<ti:title xml:lang='fre'>Epigrammes</ti:title>""" + self.tr + self.ed + """</ti:work>""".replace("\n", "")

        self.tg = """<ti:textgroup urn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:groupname xml:lang='eng'>Martial</ti:groupname>
<ti:groupname xml:lang='lat'>Martialis</ti:groupname>""" + self.wk + """</ti:textgroup>""".replace("\n", "")

        self.t = """<ti:TextInventory tiid='annotsrc' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>""" + self.tg + """</ti:TextInventory>""".replace("\n", "").strip("\n")
        self.maxDiff = None

    def tearDown(self):
        self.getCapabilities.close()

    def test_xml_TextInventoryLength(self):
        """ Tests TextInventory parses without errors """
        TI = TextInventory(resource=self.getCapabilities, name="TestInv")
        self.assertEqual(len(TI), 15)

    def test_xml_TextInventoryParsing(self):
        """ Tests TextInventory parses without errors """
        TI = TextInventory(resource=self.getCapabilities, name="TestInv")
        self.assertGreater(len(TI.textgroups), 0)

    def test_xml_TextInventory_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI = TextInventory(resource=self.getCapabilities, name="TestInv")
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294"], TextGroup)
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294.phi002"], Work)
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002"].urn), "urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"], Text)
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002"].lang, "lat")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].lang, "lat")

    def test_xml_Work_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI = TextInventory(resource=self.getCapabilities, name="TestInv")
        tg = TI["urn:cts:latinLit:phi1294"]
        self.assertIsInstance(tg["urn:cts:latinLit:phi1294.phi002"], Work)
        self.assertEqual(str(tg["urn:cts:latinLit:phi1294.phi002"].urn), "urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(tg["urn:cts:latinLit:phi1294.phi002.perseus-lat2"], Text)
        self.assertEqual(str(tg["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")

    def test_xml_work_getLang(self):
        """ Test access to translation """
        xml = """
            <ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts" urn="urn:cts:latinLit:phi1294.phi002" xml:lang="lat">
                <ti:title xml:lang="eng">Epigrammata</ti:title>
                <ti:edition workUrn="urn:cts:latinLit:phi1294.phi002" urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2">
                </ti:edition>
                <ti:translation workUrn="urn:cts:latinLit:phi1294.phi002" urn="urn:cts:latinLit:phi1294.phi002.perseus-eng2" xml:lang="eng">
                </ti:translation>
                <ti:translation workUrn="urn:cts:latinLit:phi1294.phi002" urn="urn:cts:latinLit:phi1294.phi002.perseus-eng3" xml:lang="eng">
                </ti:translation>
                <ti:translation workUrn="urn:cts:latinLit:phi1294.phi002" urn="urn:cts:latinLit:phi1294.phi002.perseus-fre1" xml:lang="fre">
                </ti:translation>
            </ti:work>
        """
        W = Work(resource=xml, urn="urn:cts:latinLit:phi1294.phi002")
        self.assertEqual(len(W.getLang("eng")), 2)
        self.assertEqual(len(W.getLang()), 3)
        self.assertEqual(
            W.metadata.export(output=Mimetypes.JSON.DTS.Std),
            [{'http://chs.harvard.edu/xmlns/cts/title': 'Epigrammata', '@language': 'eng'}],
            "Default export should work well"
        )

    def test_xml_Text_others(self):
        """ Test access to translation """
        xml = """
            <ti:work xmlns:ti="http://chs.harvard.edu/xmlns/cts" urn="urn:cts:latinLit:phi1294.phi002" xml:lang="lat">
                <ti:title xml:lang="eng">Epigrammata</ti:title>
                <ti:edition workUrn="urn:cts:latinLit:phi1294.phi002" urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2">
                </ti:edition>
                <ti:translation workUrn="urn:cts:latinLit:phi1294.phi002" urn="urn:cts:latinLit:phi1294.phi002.perseus-eng2" xml:lang="eng">
                </ti:translation>
                <ti:translation workUrn="urn:cts:latinLit:phi1294.phi002" urn="urn:cts:latinLit:phi1294.phi002.perseus-eng3" xml:lang="eng">
                </ti:translation>
                <ti:translation workUrn="urn:cts:latinLit:phi1294.phi002" urn="urn:cts:latinLit:phi1294.phi002.perseus-fre1" xml:lang="fre">
                </ti:translation>
            </ti:work>
        """
        W = Work(resource=xml, urn="urn:cts:latinLit:phi1294.phi002")
        E = W["urn:cts:latinLit:phi1294.phi002.perseus-lat2"]
        T = W["urn:cts:latinLit:phi1294.phi002.perseus-fre1"]

        self.assertEqual(E.lang, "lat")
        self.assertEqual(E.translations("fre"), [T])
        self.assertEqual(T.editions(), [E])

    def test_get_parent(self):
        TI = TextInventory(resource=self.getCapabilities, name="TestInv")
        tg = TI["urn:cts:latinLit:phi1294"]
        wk = TI["urn:cts:latinLit:phi1294.phi002"]
        tx = TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"]
        self.assertEqual(tg[1], TI)
        self.assertEqual(wk[1], tg)
        self.assertEqual(wk[2], TI)
        self.assertEqual(tx[1], wk)
        self.assertEqual(tx[2], tg)
        self.assertEqual(tx[3], TI)

    def test_translation(self):
        TI = TextInventory(resource=self.getCapabilities, name="TestInv")
        tr = TI["urn:cts:latinLit:phi1294.phi002.perseus-eng2"]
        self.assertIsInstance(tr, Text)
        self.assertEqual(tr.subtype, "Translation")

    def test_parse_string(self):
        TI = TextInventory(
            name="TestInv",
            resource="""
<ti:TextInventory xmlns:ti="http://chs.harvard.edu/xmlns/cts" tiid="thibault3">
    <ti:textgroup urn="urn:cts:greekLit:tlg0003">
        <ti:groupname xml:lang="en">Thucydides</ti:groupname>
        <ti:groupname xml:lang="eng">Thucydides</ti:groupname>
        <ti:groupname>Thucydides</ti:groupname>
        <ti:work urn="urn:cts:greekLit:tlg0003.tlg001" xml:lang="grc">
            <ti:title xml:lang="en">The Peloponnesian War</ti:title>
            <ti:title xml:lang="eng">The Peloponnesian War</ti:title>
        </ti:work>
    </ti:textgroup>
</ti:TextInventory>
            """
        )
        self.assertEqual(str(TI["urn:cts:greekLit:tlg0003.tlg001"].urn), "urn:cts:greekLit:tlg0003.tlg001")

    def test_parse_error(self):
        with self.assertRaises(TypeError):
            TI = TextInventory(
                name="TestInv",
                resource=5
            )

    def test_Inventory_pickle(self):
        """ Tests TextInventory parses without errors """
        TI = TextInventory(resource=self.getCapabilities, name="annotsrc")
        from pickle import dumps, loads

        dp = dumps(TI)
        ti = str(loads(dp))

        self.assertEqual(
            *compareSTR(
                ti,
                str(TI)
            )
        )

    def test_Inventory_metadata(self):
        """ Tests TextInventory parses without errors """
        TI = TextInventory(resource=self.getCapabilities, name="annotsrc")
        self.assertEqual(TI["urn:cts:latinLit:phi1294"].metadata["groupname"]["eng"], "Martial")
        self.assertEqual(TI["urn:cts:latinLit:phi1294"].metadata["groupname"]["lat"], "Martialis")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002"].metadata["title"]["eng"], "Epigrammata")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002"].metadata["title"]["fre"], "Epigrammes")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].metadata["label"]["eng"], "Epigrammata Label")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].metadata["label"]["fre"], "Epigrammes Label")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].metadata["description"]["fre"], "G. Heraeus")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].metadata["description"]["eng"], "W. Heraeus")

    def test_export(self):
        ed = """<ti:edition urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:label xml:lang='eng'>Epigrammata Label</ti:label>
<ti:label xml:lang='fre'>Epigrammes Label</ti:label>
<ti:description xml:lang='eng'>W. Heraeus</ti:description>
<ti:description xml:lang='fre'>G. Heraeus</ti:description>
<ti:online docname='/db/apps/canonical-latinLit/data/phi1294/phi002/phi1294.phi002.perseus-lat2.xml'>
<ti:validate schema='tei-epidoc.rng'/>
<ti:namespaceMapping abbreviation='tei' nsURI='http://www.tei-c.org/ns/1.0'/>
<ti:citationMapping>
<ti:citation label='book' xpath="/tei:div[@n='?']" scope='/tei:TEI/tei:text/tei:body/tei:div'>
<ti:citation label='poem' xpath="/tei:div[@n='?']"  scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']">
<ti:citation label='line' xpath="/tei:l[@n='?']"  scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']/tei:div[@n='?']"></ti:citation>
</ti:citation>
</ti:citation>
</ti:citationMapping>
</ti:online
></ti:edition>""".replace("\n", "")

        tr = """<ti:translation xml:lang='eng' urn='urn:cts:latinLit:phi1294.phi002.perseus-eng2' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:label xml:lang='eng'>Epigrammata</ti:label>
<ti:description xml:lang='eng'>M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus</ti:description>
<ti:online></ti:online>
</ti:translation>""".replace("\n", "")

        wk = """<ti:work urn='urn:cts:latinLit:phi1294.phi002' groupUrn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts' xml:lang='lat'>
<ti:title xml:lang='eng'>Epigrammata</ti:title>
<ti:title xml:lang='fre'>Epigrammes</ti:title>""" + tr + ed + """</ti:work>""".replace("\n", "")

        tg = """<ti:textgroup urn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:groupname xml:lang='eng'>Martial</ti:groupname>
<ti:groupname xml:lang='lat'>Martialis</ti:groupname>""" + wk + """</ti:textgroup>""".replace("\n", "")

        t = """<ti:TextInventory tiid='annotsrc' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>""" + tg + """</ti:TextInventory>""".replace("\n", "").strip("\n")

        ti = TextInventory(resource=t, name="annotsrc")
        self.assertXmlEquivalentOutputs(*compareSTR(str(ti), t))

        # Test individual :
        self.assertXmlEquivalentOutputs(*compareSTR(str(ti["urn='urn:cts:latinLit:phi1294"]), tg))
        self.assertXmlEquivalentOutputs(*compareSTR(str(ti["urn='urn:cts:latinLit:phi1294.phi002"]), wk))
        self.assertXmlEquivalentOutputs(*compareSTR(str(ti["urn='urn:cts:latinLit:phi1294.phi002.perseus-eng2"]), tr))
        self.assertXmlEquivalentOutputs(*compareSTR(str(ti["urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2"]), ed))

        # Test export :
        self.assertXmlEquivalentOutputs(*compareXML(ti.export(), t))
        self.assertXmlEquivalentOutputs(*compareXML(ti["urn='urn:cts:latinLit:phi1294"].export(), tg))
        self.assertXmlEquivalentOutputs(*compareXML(ti["urn='urn:cts:latinLit:phi1294.phi002"].export(), wk))
        self.assertXmlEquivalentOutputs(*compareXML(ti["urn='urn:cts:latinLit:phi1294.phi002.perseus-eng2"].export(), tr))
        self.assertXmlEquivalentOutputs(*compareXML(ti["urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2"].export(), ed))
        self.assertEqual(ti["urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2"].lang, "lat")
        self.assertEqual(ti["urn='urn:cts:latinLit:phi1294.phi002.perseus-eng2"].lang, "eng")

    def test_export_to_text(self):
        """ Test export to Text object """
        TI = TextInventory(resource=self.getCapabilities, name="annotsrc")
        ti_text = TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"]

        txt_text = ti_text.export(output=Mimetypes.PYTHON.MyCapytain.ReadableText)
        self.assertEqual(str(txt_text.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(txt_text.metadata["groupname"]["eng"], "Martial")  # Check inheritance of textgroup metadata
        self.assertEqual(txt_text.metadata["title"]["eng"], "Epigrammata")  # Check inheritance of work metadata
        self.assertEqual(txt_text.metadata["title"]["fre"], "Epigrammes")  # Check inheritance of work metadata
        self.assertEqual(txt_text.metadata["description"]["fre"], "G. Heraeus")  # Check inheritance of work metadata
        self.assertEqual(txt_text.citation, ti_text.citation)
        self.assertEqual(txt_text.citation.scope, "/tei:TEI/tei:text/tei:body/tei:div")

    def test_partial_str(self):
        ti = TextInventory(resource=self.t, name="annotsrc")

        e = deepcopy(ti["urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2"])
        e.urn = None
        self.assertXmlEquivalentOutputs(
            *compareSTR(
                str(e),
                self.ed.replace("urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2' ", "")
            )
        )
        e.parents = ()
        self.assertXmlEquivalentOutputs(
            *compareSTR(
                str(e),
                self.ed.replace(
                    "urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2' ", ""
                ).replace(
                    "workUrn='urn:cts:latinLit:phi1294.phi002' ", ""
                )
            )
        )

        wk = deepcopy(ti["urn='urn:cts:latinLit:phi1294.phi002"])
        wk.urn = None
        self.assertXmlEquivalentOutputs(
            *compareSTR(
                str(wk),
                self.wk.replace("urn='urn:cts:latinLit:phi1294.phi002' ", "")
            )
        )
        wk.parents = ()
        self.assertXmlEquivalentOutputs(
            *compareSTR(
                str(wk),
                self.wk.replace(
                    "urn='urn:cts:latinLit:phi1294.phi002' ", ""
                ).replace(
                    "groupUrn='urn:cts:latinLit:phi1294' ", ""
                )
            )
        )

        tg = deepcopy(ti["urn='urn:cts:latinLit:phi1294"])
        tg.urn = None
        self.assertXmlEquivalentOutputs(
            *compareSTR(
                str(tg),
                self.tg.replace("urn='urn:cts:latinLit:phi1294' ", "")
            )
        )

        ti = deepcopy(ti)
        ti.id = None
        self.assertXmlEquivalentOutputs(
            *compareSTR(
                str(ti),
                self.t.replace("tiid='annotsrc' ", "")
            )
        )

    def test_addition_work(self):
        """ Test merging two Works together
        """
        tg = """<ti:textgroup urn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:groupname xml:lang='eng'>Martial</ti:groupname>
<ti:groupname xml:lang='lat'>Martialis</ti:groupname>
<ti:work xml:lang='lat' urn='urn:cts:latinLit:phi1294.phi002' groupUrn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:title xml:lang='eng'>Epigrammata</ti:title>
<ti:title xml:lang='ger'>Epigrammen</ti:title>
<ti:edition urn='urn:cts:latinLit:phi1294.phi002.opp-lat2' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:label xml:lang='eng'>Epigrammata Label</ti:label>
<ti:label xml:lang='fre'>Epigrammes Label</ti:label>
<ti:description xml:lang='eng'>W. Heraeus</ti:description>
<ti:description xml:lang='fre'>G. Heraeus</ti:description>
<ti:online></ti:online>
</ti:edition>
</ti:work>
<ti:work xml:lang='lat' urn='urn:cts:latinLit:phi1294.phi001' groupUrn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:title xml:lang='eng'>On the Spectacles</ti:title>
<ti:title xml:lang='ger'>De spectaculis</ti:title>
</ti:work>
</ti:textgroup>""".replace("\n", "")
        TG1 = TextGroup(resource=self.tg)
        TG2 = TextGroup(resource=tg)
        self.assertEqual(
            len(TG1), 2,
            "There is two edition/translations in TG1"
        )
        self.assertEqual(
            len(TG2), 1,
            "There is one edition in TG1"
        )
        TG3 = TG1.update(TG2)
        self.assertEqual(
            len(TG3), 3,
            "There is three texts in merged objects"
        )
        self.assertEqual(str(TG3), str(TG1), "Addition in equal or incremental should have same result")
        self.assertEqual(
            TG3["urn:cts:latinLit:phi1294.phi002.opp-lat2"].parents,
            TG1["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].parents,
            "Edition OPP should be added to textgroup and original kept"
        )
        self.assertListEqual(
            sorted(TG3["urn:cts:latinLit:phi1294.phi002.opp-lat2"].editions(), key=lambda x: str(x.urn)),
            sorted([
                TG3["urn:cts:latinLit:phi1294.phi002.perseus-lat2"],
                TG3["urn:cts:latinLit:phi1294.phi002.opp-lat2"]
            ], key=lambda x: str(x.urn)),
            "New text gets access to siblings"
        )
        self.assertEqual(
            (
                TG3["urn:cts:latinLit:phi1294.phi002"].metadata["title"]["ger"],
                TG3["urn:cts:latinLit:phi1294.phi002"].metadata["title"]["eng"],
                TG3["urn:cts:latinLit:phi1294.phi002"].metadata["title"]["fre"]
            ),
            ("Epigrammen", "Epigrammata", "Epigrammes"),
            "Metadata are shared"
        )
        self.assertEqual(
            len(TG3["urn:cts:latinLit:phi1294.phi002"]), 3,
            "There should be 3 texts in work"
        )
        self.assertEqual(
            len(TG3["urn:cts:latinLit:phi1294.phi001"]), 0,
            "There should be no text in empty textgroup"
        )
        self.assertEqual(
            (
                TG3["urn:cts:latinLit:phi1294.phi001"].metadata["title"]["ger"],
                TG3["urn:cts:latinLit:phi1294.phi001"].metadata["title"]["eng"]
            ),
            ("De spectaculis", "On the Spectacles"),
            "Metadata are shared"
        )

    def test_wrong_urn_addition_work_textgroup(self):
        """ Checks that we cannot add work or textgroup with different URN"""
        from MyCapytain.errors import InvalidURN
        self.assertRaises(
            InvalidURN,
            lambda x: Work(urn="urn:cts:latinLit:phi1294.phi002").update(Work(urn="urn:cts:latinLit:phi1297.phi002")),
            "Addition of different work with different URN should fail"
        )
        self.assertRaises(
            InvalidURN,
            lambda x: TextGroup(urn="urn:cts:latinLit:phi1294").update(TextGroup(urn="urn:cts:latinLit:phi1297")),
            "Addition of different work with different URN should fail"
        )

    def test_wrong_type_addition_work_textgroup(self):
        """ Checks that we cannot add work or textgroup with different URN"""
        self.assertRaises(
            TypeError,
            lambda x: Work(urn="urn:cts:latinLit:phi1294.phi002").update(TextGroup(urn="urn:cts:latinLit:phi1297")),
            "Addition of different type should fail for Work"
        )
        self.assertRaises(
            TypeError,
            lambda x: TextGroup(urn="urn:cts:latinLit:phi1294").update(Work(urn="urn:cts:latinLit:phi1297.phi002")),
            "Addition of different type should fail for TextGroup"
        )

    def test_export_jsonld(self):
        tg = """<ti:textgroup urn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
        <ti:groupname xml:lang='eng'>Martial</ti:groupname>
        <ti:groupname xml:lang='lat'>Martialis</ti:groupname>
        <ti:work xml:lang='lat' urn='urn:cts:latinLit:phi1294.phi002' groupUrn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
        <ti:title xml:lang='eng'>Epigrammata</ti:title>
        <ti:title xml:lang='ger'>Epigrammen</ti:title>
        <ti:edition urn='urn:cts:latinLit:phi1294.phi002.opp-lat2' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
        <ti:label xml:lang='eng'>Epigrammata Label</ti:label>
        <ti:label xml:lang='fre'>Epigrammes Label</ti:label>
        <ti:description xml:lang='eng'>W. Heraeus</ti:description>
        <ti:description xml:lang='fre'>G. Heraeus</ti:description>
        <ti:online></ti:online>
        </ti:edition>
        </ti:work>
        <ti:work xml:lang='lat' urn='urn:cts:latinLit:phi1294.phi001' groupUrn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
        <ti:title xml:lang='eng'>On the Spectacles</ti:title>
        <ti:title xml:lang='ger'>De spectaculis</ti:title>
        </ti:work>
        </ti:textgroup>"""
        tg = TextGroup(urn="urn:cts:latinLit:phi1294", resource=tg)

        six.assertCountEqual(
            self,
            {
                '@id': 'http://capitain.github.io/domain/urn:cts:latinLit:phi1294',
                'http://w3id.org/dts-ontology/capabilities': {
                    'http://w3id.org/dts-ontology/navigation': {
                        'http://w3id.org/dts-ontology/parents': [

                        ],
                        'http://w3id.org/dts-ontology/siblings': {

                        }
                    },
                    'http://w3id.org/dts-ontology/ordered': False,
                    'http://w3id.org/dts-ontology/static': True,
                    'http://w3id.org/dts-ontology/supportsRole': False
                },
                'http://w3id.org/dts-ontology/description': None,
                'http://w3id.org/dts-ontology/members': [
                    {
                        '@id': 'http://capitain.github.io/domain/urn:cts:latinLit:phi1294.phi002',
                        'http://w3id.org/dts-ontology/capabilities': {
                            'http://w3id.org/dts-ontology/navigation': {
                                'http://w3id.org/dts-ontology/parents': [

                                ],
                                'http://w3id.org/dts-ontology/siblings': {

                                }
                            },
                            'http://w3id.org/dts-ontology/ordered': False,
                            'http://w3id.org/dts-ontology/static': True,
                            'http://w3id.org/dts-ontology/supportsRole': False
                        },
                        'http://w3id.org/dts-ontology/description': None,
                        'http://w3id.org/dts-ontology/members': [
                            {
                                '@id': 'http://capitain.github.io/domain/urn:cts:latinLit:phi1294.phi002.opp-lat2',
                                'http://w3id.org/dts-ontology/capabilities': {
                                    'http://w3id.org/dts-ontology/navigation': {
                                        'http://w3id.org/dts-ontology/parents': [

                                        ],
                                        'http://w3id.org/dts-ontology/siblings': {

                                        }
                                    },
                                    'http://w3id.org/dts-ontology/ordered': False,
                                    'http://w3id.org/dts-ontology/static': True,
                                    'http://w3id.org/dts-ontology/supportsRole': False
                                },
                                'http://w3id.org/dts-ontology/description': None,
                                'http://w3id.org/dts-ontology/properties': {
                                    'http://w3id.org/dts-ontology/model': 'http://w3id.org/dts-ontology/collection',
                                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://w3id.org/dts-ontology/collection'
                                }
                            }
                        ],
                        'http://w3id.org/dts-ontology/properties': {
                            'http://w3id.org/dts-ontology/model': 'http://w3id.org/dts-ontology/collection',
                            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://chs.harvard.edu/xmlns/cts/Work'
                        }
                    },
                    {
                        '@id': 'http://capitain.github.io/domain/urn:cts:latinLit:phi1294.phi001',
                        'http://w3id.org/dts-ontology/capabilities': {
                            'http://w3id.org/dts-ontology/navigation': {
                                'http://w3id.org/dts-ontology/parents': [

                                ],
                                'http://w3id.org/dts-ontology/siblings': {

                                }
                            },
                            'http://w3id.org/dts-ontology/ordered': False,
                            'http://w3id.org/dts-ontology/static': True,
                            'http://w3id.org/dts-ontology/supportsRole': False
                        },
                        'http://w3id.org/dts-ontology/description': None,
                        'http://w3id.org/dts-ontology/properties': {
                            'http://w3id.org/dts-ontology/model': 'http://w3id.org/dts-ontology/collection',
                            'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://chs.harvard.edu/xmlns/cts/Work'
                        }
                    }
                ],
                'http://w3id.org/dts-ontology/properties': {
                    'http://w3id.org/dts-ontology/model': 'http://w3id.org/dts-ontology/collection',
                    'http://www.w3.org/1999/02/22-rdf-syntax-ns#type': 'http://chs.harvard.edu/xmlns/cts/TextGroup'
                }
            },
            tg.export(Mimetypes.JSON.DTS.Std, domain="http://capitain.github.io/domain/"),
            "JSON DTS export should be stable"
        )


class TestCitation(unittest.TestCase):
    def test_empty(self):
        a = Citation(name="none")
        self.assertEqual(str(a), "")
