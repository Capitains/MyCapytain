# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from io import open, StringIO
from operator import attrgetter

import lxml.etree as etree
import xmlunittest

from MyCapytain.common import constants
from MyCapytain.resources.collections.cts import *
from MyCapytain.resources.prototypes.cts.text import PrototypeCtsNode
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.common.constants import Mimetypes, RDF_NAMESPACES, XPATH_NAMESPACES
from rdflib import URIRef, Literal, XSD


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
    def sortbyattr(elem):
        attrkeys = sorted(elem.keys())
        if len(attrkeys):
            return elem.get(attrkeys[0])
        else:
            return ""

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
        items = sorted(items, key=XML_Compare.sortbyattr)
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
        constants.__MYCAPYTAIN_TRIPLE_GRAPH__.remove((None, None, None))

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

        self.cm = """<ti:commentary xml:lang='eng' urn='urn:cts:latinLit:phi1294.phi002.perseus-eng3' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
  <ti:label xml:lang='eng'>Introduction to Epigrammata</ti:label>
  <ti:description xml:lang='eng'>Introduction to Epigrammata by Someone, 1866, Oxford</ti:description>
  <ti:about urn="urn:cts:latinLit:phi1294.phi002.perseus-eng2"/>
  <ti:about urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"/>
</ti:commentary>""".replace('\n', '')

        self.wk = """<ti:work xml:lang='lat' urn='urn:cts:latinLit:phi1294.phi002' groupUrn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:title xml:lang='eng'>Epigrammata</ti:title>
<ti:title xml:lang='fre'>Epigrammes</ti:title>""" + self.tr + self.ed + self.tr + """</ti:work>""".replace("\n", "")

        self.tg = """<ti:textgroup urn='urn:cts:latinLit:phi1294' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>
<ti:groupname xml:lang='eng'>Martial</ti:groupname>
<ti:groupname xml:lang='lat'>Martialis</ti:groupname>""" + self.wk + """</ti:textgroup>""".replace("\n", "")

        self.t = """<ti:TextInventory tiid='annotsrc' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>""" + self.tg + """</ti:TextInventory>""".replace(
            "\n", "").strip("\n")
        self.maxDiff = None

    def tearDown(self):
        self.getCapabilities.close()

    def test_xml_TextInventoryLength(self):
        """ Tests CtsTextInventoryMetadata parses without errors """
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        self.assertEqual(len(TI), 16)

    def test_empty_namespace_doesnot_crash(self):
        """ Test when we have a string to expand in structured metadata but we have an empty Namespace"""
        TG = """<textgroup
        xmlns="http://chs.harvard.edu/xmlns/cts"
        xmlns:dct="http://purl.org/dc/terms/"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:dts="http://w3id.org/dts-ontology/"
        xmlns:cpt="http://purl.org/capitains/ns/1.0#"
        xmlns:skos="http://www.w3.org/2004/02/skos/core#"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:saws="http://purl.org/saws/ontology#"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        urn="urn:cts:pompei:cil004-00000">
    <groupname xml:lang="lat">Corpus Inscriptionum Latinarum IV 0-100</groupname>
    <cpt:structured-metadata>
        <dc:identifier>http://arachne.uni-koeln.de/item/buch/2688</dc:identifier>
        <dc:identifier>CIL IV</dc:identifier>
        <dc:identifier>CIL 4</dc:identifier>
        <dc:title xml:lang="lat">Corpus Inscriptionum Latinarum IV</dc:title>

        <dc:contributor>Manfred Clauss</dc:contributor>
        <dc:contributor>Anne Kolb</dc:contributor>
        <dc:contributor>Wolfgang A. Slaby </dc:contributor>

        <dc:author>Mau, August. Zangemeister</dc:author>
        <dc:author>Karl Friedrich Wilhelm</dc:author>

        <dc:publisher xml:lang="eng">Oxford University Press</dc:publisher>
        <dct:dateCopyrighted rdf:datatype="xsd:gYear">1837</dct:dateCopyrighted>
    </cpt:structured-metadata>
</textgroup>"""
        TG = XmlCtsTextgroupMetadata.parse(TG)
        self.assertEqual(TG.id, "urn:cts:pompei:cil004-00000")

    def test_xml_TextInventoryParsing(self):
        """ Tests CtsTextInventoryMetadata parses without errors """
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        self.assertGreater(len(TI.textgroups), 0)

    def test_xml_TextInventory_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294"], XmlCtsTextgroupMetadata)
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294.phi002"], XmlCtsWorkMetadata)
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002"].urn), "urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"], XmlCtsTextMetadata)
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn),
                         "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002"].lang, "lat")
        self.assertEqual(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].lang, "lat")

    def test_xml_Work_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        tg = TI["urn:cts:latinLit:phi1294"]
        self.assertIsInstance(tg["urn:cts:latinLit:phi1294.phi002"], XmlCtsWorkMetadata)
        self.assertEqual(str(tg["urn:cts:latinLit:phi1294.phi002"].urn), "urn:cts:latinLit:phi1294.phi002")
        self.assertIsInstance(tg["urn:cts:latinLit:phi1294.phi002.perseus-lat2"], XmlCtsTextMetadata)
        self.assertEqual(str(tg["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].urn),
                         "urn:cts:latinLit:phi1294.phi002.perseus-lat2")

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
        W = XmlCtsWorkMetadata.parse(resource=xml)
        self.assertEqual(
            W.metadata.export(
                output=Mimetypes.JSON.Std,
                only=["http://www.w3.org/2004/02/skos/core#", 'http://chs.harvard.edu/xmlns/cts/']
            ),
            {
                'http://www.w3.org/2004/02/skos/core#prefLabel': {'eng': 'Epigrammata'},
                'http://chs.harvard.edu/xmlns/cts/title': {'eng': 'Epigrammata'}
            },
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
        W = XmlCtsWorkMetadata.parse(resource=xml)
        E = W["urn:cts:latinLit:phi1294.phi002.perseus-lat2"]
        T = W["urn:cts:latinLit:phi1294.phi002.perseus-fre1"]

        self.assertEqual(E.lang, "lat")
        self.assertEqual(E.translations("fre"), [T])
        self.assertEqual(T.editions(), [E])

    def test_get_parent(self):
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        tg = TI["urn:cts:latinLit:phi1294"]
        wk = TI["urn:cts:latinLit:phi1294.phi002"]
        tx = TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"]
        self.assertEqual(tg.ancestors[0], TI)
        self.assertEqual(wk.ancestors[0], tg)
        self.assertEqual(wk.ancestors[1], TI)
        self.assertEqual(tx.ancestors[0], wk)
        self.assertEqual(tx.ancestors[1], tg)
        self.assertEqual(tx.ancestors[2], TI)

    def test_translation(self):
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        tr = TI["urn:cts:latinLit:phi1294.phi002.perseus-eng2"]
        self.assertIsInstance(tr, XmlCtsTranslationMetadata)
        self.assertEqual(tr.subtype, "translation")

    def test_commentary(self):
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        tr = TI["urn:cts:latinLit:phi1294.phi002.perseus-eng3"]
        self.assertIsInstance(tr, XmlCtsCommentaryMetadata)
        self.assertEqual(tr.subtype, "commentary")
        self.assertEqual(tr.citation.name, 'commentary')
        self.assertEqual(tr.citation.child.name, 'paragraph')
        self.assertEqual(tr.citation.refsDecl, "/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']")
        self.assertEqual(tr.citation.child.refsDecl,
                         "/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='$1']/tei:div[@n='$2']")

    def test_parse_string(self):
        TI = XmlCtsTextInventoryMetadata.parse(
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
            TI = XmlCtsTextInventoryMetadata.parse(
                resource=5
            )

    def test_Inventory_pickle(self):
        """ Tests CtsTextInventoryMetadata parses without errors """
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        from pickle import dumps, loads

        dp = dumps(TI)
        # We save to xml and delete graph and instance to make sure things are working out
        xml = TI.export(Mimetypes.XML.CTS)
        TI.graph.remove((None, None, None))
        del TI

        self.assertEqual(
            len(list(constants.__MYCAPYTAIN_TRIPLE_GRAPH__.triples((None, None, None)))),
            0,
            "There should be 0 metadata node for the child 1294 because everything is gone"
        )
        # Load back
        ti = loads(dp)
        tixml = ti.export(Mimetypes.XML.CTS)
        self.assertEqual(
            len(list(ti["urn:cts:latinLit:phi1294"].metadata.get(RDF_NAMESPACES.CTS.groupname))),
            2,
            "There should be 2 groupname node for the child 1294"
        )
        self.assertEqual(*compareSTR(tixml, xml))

    def test_Inventory_metadata(self):
        """ Tests CtsTextInventoryMetadata parses without errors """
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294"].get_cts_property("groupname", "eng")), "Martial")
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294"].get_cts_property("groupname", "lat")), "Martialis")
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002"].get_cts_property("title", "eng")), "Epigrammata")
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002"].get_cts_property("title", "fre")), "Epigrammes")
        self.assertRegex(str(TI["urn:cts:latinLit:phi1294.phi002"].get_cts_property("title", "per")),
                         "Epigrammata|Epigrammes",
                         "Requesting a CTS title with a language that does not exist should return one of the existing properties.")
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].get_cts_property("label", "eng")),
                         "Epigrammata Label")
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].get_cts_property("label", "fre")),
                         "Epigrammes Label")
        self.assertRegex(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].get_cts_property("label", "per")),
                         "Epigrammes Label|Epigrammata Label",
                         "Requesting a CTS label with a language that does not exist should return one of the existing properties.")
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].get_cts_property("description", "fre")),
                         "G. Heraeus")
        self.assertEqual(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].get_cts_property("description", "eng")),
                         "W. Heraeus")
        self.assertRegex(str(TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].get_cts_property("description", "per")),
                         "W. Heraeus|G. Heraeus",
                         "Requesting a CTS description with a language that does not exist should return one of the existing properties.")
        self.assertCountEqual(
            list([str(o) for o in TI["urn:cts:latinLit:phi1294.phi002.perseus-eng3"].get_link(constants.RDF_NAMESPACES.CTS.term("about"))]),
                         ["urn:cts:latinLit:phi1294.phi002.perseus-eng2", "urn:cts:latinLit:phi1294.phi002.perseus-lat2"])
        # Test that the citation scheme of the commentary is being returned

    def test_export(self):
        # <ns0:validate schema='tei-epidoc.rng'/>
        ed = """<ns0:edition urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2' workUrn='urn:cts:latinLit:phi1294.phi002' xml:lang="lat" xmlns:ns0='http://chs.harvard.edu/xmlns/cts'>
        <ns0:label xml:lang='eng'>Epigrammata Label</ns0:label>
        <ns0:label xml:lang='fre'>Epigrammes Label</ns0:label>
        <ns0:description xml:lang='eng'>W. Heraeus</ns0:description>
        <ns0:description xml:lang='fre'>G. Heraeus</ns0:description>
        <ns0:online>
        <ns0:citationMapping>
        <ns0:citation label='book' xpath="/tei:div[@n='?']" scope='/tei:TEI/tei:text/tei:body/tei:div'>
        <ns0:citation label='poem' xpath="/tei:div[@n='?']"  scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']">
        <ns0:citation label='line' xpath="/tei:l[@n='?']"  scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']/tei:div[@n='?']"></ns0:citation>
        </ns0:citation>
        </ns0:citation>
        </ns0:citationMapping>
        </ns0:online>
        </ns0:edition>""".replace("\n", "")

        tr = """<ns0:translation xml:lang='eng' urn='urn:cts:latinLit:phi1294.phi002.perseus-eng2' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ns0='http://chs.harvard.edu/xmlns/cts'>
        <ns0:label xml:lang='eng'>Epigrammata</ns0:label>
        <ns0:description xml:lang='eng'>M. Valerii Martialis Epigrammaton libri / recognovit W. Heraeus</ns0:description>
        </ns0:translation>""".replace("\n", "")

        cm = """<ns0:commentary xml:lang='eng' urn='urn:cts:latinLit:phi1294.phi002.perseus-eng3' workUrn='urn:cts:latinLit:phi1294.phi002' xmlns:ns0='http://chs.harvard.edu/xmlns/cts'>
          <ns0:label xml:lang='eng'>Introduction to Epigrammata</ns0:label>
          <ns0:description xml:lang='eng'>Introduction to Epigrammata by Someone, 1866, Oxford</ns0:description>
          <ns0:about urn="urn:cts:latinLit:phi1294.phi002.perseus-eng2"/>
          <ns0:about urn="urn:cts:latinLit:phi1294.phi002.perseus-lat2"/>
        </ns0:commentary>""".replace('\n', '')

        wk = """<ns0:work urn='urn:cts:latinLit:phi1294.phi002' groupUrn='urn:cts:latinLit:phi1294' xmlns:ns0='http://chs.harvard.edu/xmlns/cts' xml:lang='lat'>
        <ns0:title xml:lang='eng'>Epigrammata</ns0:title>
        <ns0:title xml:lang='fre'>Epigrammes</ns0:title>""" + tr + ed + cm + """</ns0:work>""".replace("\n", "")

        tg = """<ns0:textgroup urn='urn:cts:latinLit:phi1294' xmlns:ns0='http://chs.harvard.edu/xmlns/cts'>
        <ns0:groupname xml:lang='eng'>Martial</ns0:groupname>
        <ns0:groupname xml:lang='lat'>Martialis</ns0:groupname>""" + wk + """</ns0:textgroup>""".replace("\n", "")

        t = """<ns0:TextInventory tiid='annotsrc' xmlns:ns0='http://chs.harvard.edu/xmlns/cts'>""" + tg + """</ns0:TextInventory>""".replace(
            "\n", "").strip("\n")
        # compareSTR
        ti = XmlCtsTextInventoryMetadata.parse(resource=t)
        self.assertEqual(*compareSTR(ti.export(Mimetypes.XML.CTS), t))

        # Test individual :
        self.assertEqual(*compareSTR(ti["urn:cts:latinLit:phi1294"].export(Mimetypes.XML.CTS), tg))
        self.assertEqual(
            *compareSTR(ti["urn:cts:latinLit:phi1294.phi002"].export(Mimetypes.XML.CTS), wk))
        self.assertEqual(
            *compareSTR(ti["urn:cts:latinLit:phi1294.phi002.perseus-eng2"].export(Mimetypes.XML.CTS), tr))
        self.assertEqual(
            *compareSTR(ti["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].export(Mimetypes.XML.CTS), ed))
        self.assertEqual(
            *compareSTR(ti["urn:cts:latinLit:phi1294.phi002.perseus-eng3"].export(Mimetypes.XML.CTS), cm))

        # Test export :
        self.assertEqual(*compareSTR(ti.export(Mimetypes.XML.CTS), t))
        self.assertEqual(*compareSTR(ti["urn:cts:latinLit:phi1294"].export(Mimetypes.XML.CTS), tg))
        self.assertEqual(*compareSTR(ti["urn:cts:latinLit:phi1294.phi002"].export(Mimetypes.XML.CTS), wk))
        self.assertEqual(*compareSTR(ti["urn:cts:latinLit:phi1294.phi002.perseus-eng2"].export(Mimetypes.XML.CTS), tr))
        self.assertEqual(*compareSTR(ti["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].export(Mimetypes.XML.CTS), ed))
        self.assertEqual(*compareSTR(ti["urn:cts:latinLit:phi1294.phi002.perseus-eng3"].export(Mimetypes.XML.CTS), cm))
        self.assertEqual(ti["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].lang, "lat")
        self.assertEqual(ti["urn:cts:latinLit:phi1294.phi002.perseus-eng2"].lang, "eng")
        self.assertEqual(ti["urn:cts:latinLit:phi1294.phi002.perseus-eng3"].lang, "eng")

    def test_import_to_text(self):
        """ Test export to CtsTextMetadata object """
        TI = XmlCtsTextInventoryMetadata.parse(resource=self.getCapabilities)
        ti_text = TI["urn:cts:latinLit:phi1294.phi002.perseus-lat2"]

        txt_text = PrototypeCtsNode("urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        txt_text.set_metadata_from_collection(ti_text)
        self.assertEqual(str(txt_text.urn), "urn:cts:latinLit:phi1294.phi002.perseus-lat2")
        self.assertEqual(
            str(txt_text.metadata.get_single(constants.RDF_NAMESPACES.CTS.term("groupname"), "eng")),
            "Martial",
            "Check inheritance of textgroup metadata"
        )
        self.assertEqual(
            str(txt_text.metadata.get_single(constants.RDF_NAMESPACES.CTS.term("title"), "eng")),
            "Epigrammata",
            "Check inheritance of work metadata"
        )
        self.assertEqual(
            str(txt_text.metadata.get_single(constants.RDF_NAMESPACES.CTS.term("title"), "fre")),
            "Epigrammes",
            "Check inheritance of work metadata"
        )
        for i in range(0, 100):
            self.assertEqual(
                str(txt_text.metadata.get_single(constants.RDF_NAMESPACES.CTS.term("description"), "fre")),
                "G. Heraeus",
                "Check inheritance of work metadata"
            )
        self.assertEqual(txt_text.citation, ti_text.citation)
        self.assertEqual(txt_text.citation.scope, "/tei:TEI/tei:text/tei:body/tei:div")

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
        TG1 = XmlCtsTextgroupMetadata.parse(resource=self.tg)
        TG2 = XmlCtsTextgroupMetadata.parse(resource=tg)
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
            list(TG3["urn:cts:latinLit:phi1294.phi002.opp-lat2"].ancestors),
            list(TG1["urn:cts:latinLit:phi1294.phi002.perseus-lat2"].ancestors),
            "XmlCtsEditionMetadata OPP should be added to textgroup and original kept"
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
                str(TG3["urn:cts:latinLit:phi1294.phi002"].get_cts_property("title", "ger")),
                str(TG3["urn:cts:latinLit:phi1294.phi002"].get_cts_property("title", "eng")),
                str(TG3["urn:cts:latinLit:phi1294.phi002"].get_cts_property("title", "fre"))
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
                str(TG3["urn:cts:latinLit:phi1294.phi001"].get_cts_property("title", "ger")),
                str(TG3["urn:cts:latinLit:phi1294.phi001"].get_cts_property("title", "eng"))
            ),
            ("De spectaculis", "On the Spectacles"),
            "Metadata are shared"
        )

    def test_wrong_urn_addition_work_textgroup(self):
        """ Checks that we cannot add work or textgroup with different URN"""
        from MyCapytain.errors import InvalidURN
        self.assertRaises(
            InvalidURN,
            lambda x: XmlCtsWorkMetadata(urn="urn:cts:latinLit:phi1294.phi002").update(XmlCtsWorkMetadata(urn="urn:cts:latinLit:phi1297.phi002")),
            "Addition of different work with different URN should fail"
        )
        self.assertRaises(
            InvalidURN,
            lambda x: XmlCtsTextgroupMetadata(urn="urn:cts:latinLit:phi1294").update(
                XmlCtsTextgroupMetadata(urn="urn:cts:latinLit:phi1297")),
            "Addition of different work with different URN should fail"
        )

    def test_wrong_type_addition_work_textgroup(self):
        """ Checks that we cannot add work or textgroup with different URN"""
        self.assertRaises(
            TypeError,
            lambda x: XmlCtsWorkMetadata(urn="urn:cts:latinLit:phi1294.phi002").update(
                XmlCtsTextgroupMetadata.parse(urn="urn:cts:latinLit:phi1297")),
            "Addition of different type should fail for CtsWorkMetadata"
        )
        self.assertRaises(
            TypeError,
            lambda x: XmlCtsTextgroupMetadata.parse(urn="urn:cts:latinLit:phi1294").update(
                XmlCtsWorkMetadata(urn="urn:cts:latinLit:phi1297.phi002")),
            "Addition of different type should fail for CtsTextgroupMetadata"
        )

    def test_structured_metadata_parse(self):
        with open("./tests/testing_data/capitains/work_with_structured.xml") as f:
            work = XmlCtsWorkMetadata.parse(f)
        self.assertEqual(
            list(
                work["urn:cts:greekLit:stoa0033a.tlg028.1st1K-grc1"].metadata.
                    get(URIRef("http://purl.org/dc/terms/dateCopyrighted"))
            ),
            [Literal("1837", datatype=XSD.gYear)]
        )
        self.assertEqual(
            list(
                work["urn:cts:greekLit:stoa0033a.tlg028.1st1K-grc1"].metadata.
                    get(URIRef("http://purl.org/dc/elements/1.1/contributor"))
            ),
            [Literal("Immanuel Bekker", lang="eng")]
        )
        self.assertEqual(
            list(
                work.metadata.get(URIRef("http://purl.org/saws/ontology#isAttributedToAuthor"))
            ),
            [Literal("Aristote", lang="eng")]
        )
        with open("./tests/testing_data/capitains/textgroup_with_structured.xml") as f:
            tg = XmlCtsTextgroupMetadata.parse(f)
        self.assertCountEqual(
            list(
                tg.metadata.get(URIRef("http://schema.org/birthDate"))
            ),
            [Literal("-384", datatype=XSD.integer), Literal("457BCE")]
        )
        self.assertEqual(
            list(
                tg.members[0].metadata.get(URIRef("http://purl.org/saws/ontology#cost"))
            ),
            [Literal("1.5", datatype=XSD.float)]
        )
        self.assertCountEqual(
            list(
                tg.metadata.get(URIRef("http://schema.org/birthPlace"))
            ),
            [Literal("Stagire", lang="fre"), URIRef('https://pleiades.stoa.org/places/501625')]
        )

    def test_export_structured_metadata(self):
        with open("./tests/testing_data/capitains/textgroup_with_structured.xml") as f:
            tg = XmlCtsTextgroupMetadata.parse(f)
        out = xmlparser(tg.export(Mimetypes.XML.CapiTainS.CTS))

        ns = {k: v for k, v in XPATH_NAMESPACES.items()}
        ns["scm"] = "http://schema.org/"
        ns["saws"] = "http://purl.org/saws/ontology#"
        ns["dct"] = "http://purl.org/dc/terms/"
        self.assertCountEqual(
            out.xpath("./cpt:structured-metadata//scm:birthDate", namespaces=ns),
            ['457BCE', -384]
        )
        self.assertCountEqual(
            out.xpath("./cpt:structured-metadata//scm:birthPlace", namespaces=ns),
            ['Stagire', "https://pleiades.stoa.org/places/501625"]
        )
        self.assertCountEqual(
            out.xpath("./ti:work/cpt:structured-metadata/saws:cost", namespaces=ns),
            [1.5]
        )
        self.assertCountEqual(
            out.xpath(".//ti:translation/cpt:structured-metadata/dct:dateCopyrighted", namespaces=ns),
            [1837]
        )
        #
        # print(out)


class TestCitation(unittest.TestCase):
    def test_empty(self):
        a = XmlCtsCitation(name="none")
        self.assertEqual(a.export(), "")

    def test_ingest_and_match(self):
        """ Ensure matching and parsing XML works correctly """
        xml = xmlparser("""<ns0:edition urn='urn:cts:latinLit:phi1294.phi002.perseus-lat2' workUrn='urn:cts:latinLit:phi1294.phi002' xml:lang="lat" xmlns:ns0='http://chs.harvard.edu/xmlns/cts'>
    <ns0:label xml:lang='eng'>Epigrammata Label</ns0:label>
    <ns0:label xml:lang='fre'>Epigrammes Label</ns0:label>
    <ns0:description xml:lang='eng'>W. Heraeus</ns0:description>
    <ns0:description xml:lang='fre'>G. Heraeus</ns0:description>
    <ns0:online>
    <ns0:citationMapping>
    <ns0:citation label='book' xpath="/tei:div[@n='?']" scope='/tei:TEI/tei:text/tei:body/tei:div'>
    <ns0:citation label='poem' xpath="/tei:div[@n='?']"  scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']">
    <ns0:citation label='line' xpath="/tei:l[@n='?']"  scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']/tei:div[@n='?']"></ns0:citation>
    </ns0:citation>
    </ns0:citation>
    </ns0:citationMapping>
    </ns0:online>
    </ns0:edition>""".replace("\n", ""))
        citation = (XmlCtsEditionMetadata.parse(xml)).citation
        # The citation that should be returned is the root
        self.assertEqual(citation.name, "book", "Name should have been parsed")
        self.assertEqual(citation.child.name, "poem", "Name of child should have been parsed")
        self.assertEqual(citation.child.child.name, "line", "Name of descendants should have been parsed")
        self.assertEqual(citation.is_root(), True, "Root should be true on root")
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
