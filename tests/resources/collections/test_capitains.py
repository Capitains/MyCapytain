# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import unittest
from io import open, StringIO
from operator import attrgetter

import lxml.etree as etree
import xmlunittest

from MyCapytain.common import constants
from MyCapytain.resources.collections.capitains import *
from MyCapytain.resources.prototypes.capitains.text import PrototypeCapitainsNode
from MyCapytain.resolvers.capitains.local import XmlCapitainsLocalResolver
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.common.constants import Mimetypes, RDF_NAMESPACES, XPATH_NAMESPACES
from rdflib import URIRef, Literal
import re


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

        self.getCapabilities = open("tests/testing_data/guidelines_v3/getCapabilities.xml", "r")
        self.readable = """<cpt:collection xmlns:cpt="http://purl.org/capitains/ns/1.0#" 
            xmlns:dts="https://w3id.org/dts/api#" 
            xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:dct="http://purl.org/dc/terms/" 
            xmlns:bib="http://bibliotek-o.org/1.0/ontology/" 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.abbas.deu001.xml" readable="true">
            <cpt:identifier>urn:cts:formulae:elexicon.abbas.deu001</cpt:identifier>
            <dc:title xml:lang="deu">Abbas, abbatissa (deu)</dc:title>
            <dc:language>deu</dc:language>
            <dc:format>application/tei+xml</dc:format>
            <dc:type>cts:edition</dc:type>
            <dc:creator>Horst Lößlein</dc:creator>
            <cpt:parent>urn:cts:formulae:elexicon.abbas</cpt:parent>
            <dc:publisher xml:lang="mul">Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg</dc:publisher>
            <cpt:structured-metadata>
            <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
            <dct:created>2019-05-07</dct:created>
            <dct:references></dct:references>
            </cpt:structured-metadata>
            </cpt:collection>""".replace("\n", "")

        self.wk = """<cpt:collection xmlns:cpt="http://purl.org/capitains/ns/1.0#" 
            xmlns:dts="https://w3id.org/dts/api#" 
            xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:dct="http://purl.org/dc/terms/" 
            xmlns:bib="http://bibliotek-o.org/1.0/ontology/" 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/__capitains__.xml">
            <cpt:identifier>urn:cts:formulae:elexicon.abbas</cpt:identifier>
            <cpt:parent>urn:cts:formulae:elexicon</cpt:parent>
            <dc:title xml:lang="lat">Abbas, abbatissa</dc:title>
            <dc:type>cts:work</dc:type>
            <cpt:members>""" + self.readable + """</cpt:members>
            <cpt:structured-metadata>
            <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
            </cpt:structured-metadata>
            </cpt:collection>""".replace("\n", "")

        self.tg = """<cpt:collection xmlns:cpt="http://purl.org/capitains/ns/1.0#" 
            xmlns:dts="https://w3id.org/dts/api#" 
            xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:dct="http://purl.org/dc/terms/" 
            xmlns:bib="http://bibliotek-o.org/1.0/ontology/" 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            path="../tests/testing_data/guidelines_v3/data/elexicon/__capitains__.xml">
            <cpt:identifier>urn:cts:formulae:elexicon</cpt:identifier>
            <cpt:parent>default</cpt:parent>
            <dc:title xml:lang="fre">Lexique</dc:title>
            <dc:title xml:lang="eng">Lexicon</dc:title>
            <dc:title xml:lang="deu">Lexikon</dc:title>
            <dc:type>cts:textgroup</dc:type>
            <cpt:members>""" + self.wk + """</cpt:members>
            <cpt:structured-metadata>
            <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
            <bib:AbbreviatedTitle></bib:AbbreviatedTitle>
            </cpt:structured-metadata>
            </cpt:collection>""".replace("\n", "")

        self.t = """<cpt:collection path="None" xmlns:cpt="http://purl.org/capitains/ns/1.0#" xmlns:dts="https://w3id.org/dts/api#" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dct="http://purl.org/dc/terms/" xmlns:bib="http://bibliotek-o.org/1.0/ontology/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <cpt:identifier>defaultTic</cpt:identifier>
            <cpt:members>
            <cpt:collection path="None">
            <cpt:identifier>default</cpt:identifier>
            <cpt:parent>defaultTic</cpt:parent>
            <cpt:members>""" + self.tg + """</cpt:members>
            <cpt:structured-metadata>
            <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
            </cpt:structured-metadata>
            </cpt:collection>
            </cpt:members>
            <cpt:structured-metadata>
            <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
            </cpt:structured-metadata>
            </cpt:collection>""".replace("\n", "").strip("\n")
        self.maxDiff = None

    def tearDown(self):
        self.getCapabilities.close()

    def test_xml_TextInventoryLength(self):
        """ Tests XmlCapitainsCollectionMetadata parses without errors """
        TI = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities)
        self.assertEqual(len(TI), 0, 'Without children and non-recursive should have a length of 0 (i.e., no texts.')
        self.assertEqual(len(TI.descendants), 0, 'Without children and non-recursive should result in 0 descendants.')

    def test_xml_TextInventoryLength_with_children(self):
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True)
        self.assertEqual(len(TI), 0, 'With children but non-recursive should have a length of 0 (i.e., no texts).')
        self.assertEqual(len(TI.descendants), 1, 'With children but non-recursive should result in 1 descendant.')

    def test_xml_TextInventoryLength_with_children_recursive(self):
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        self.assertEqual(len(TI), 19, 'With children and recursive should have a length of 19 (i.e., 19 texts).')
        self.assertEqual(len(TI.descendants), 37, 'With children and recursive should result in 37 descendants.')

    def test_empty_namespace_doesnot_crash(self):
        """ Test when we have a string to expand in structured metadata but we have an empty Namespace"""
        TG = """<collection 
        xmlns:ti="http://chs.harvard.edu/xmlns/cts"
        xmlns:dct="http://purl.org/dc/terms/"
        xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
        xmlns:dts="http://w3id.org/dts-ontology/"
        xmlns="http://purl.org/capitains/ns/1.0#"
        xmlns:skos="http://www.w3.org/2004/02/skos/core#"
        xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:saws="http://purl.org/saws/ontology#"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:bib="http://bibliotek-o.org/1.0/ontology/"
        path="../tests/testing_data/guidelines_v3/data/elexicon/__capitains__.xml">
        <identifier>urn:cts:formulae:elexicon</identifier>
        <dc:title xml:lang="deu">Lexikon</dc:title>
        <dc:title xml:lang="fre">Lexique</dc:title>
        <dc:title xml:lang="eng">Lexicon</dc:title>
        <dc:type>cts:textgroup</dc:type>
        <parent>default</parent>
        <members>
        <collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/__capitains__.xml">
        <identifier>urn:cts:formulae:elexicon.abbas</identifier>
        <dc:type>cts:work</dc:type>
        <dc:title xml:lang="lat">Abbas, abbatissa</dc:title>
        <parent>urn:cts:formulae:elexicon</parent>
        <members>
        <collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.abbas.deu001.xml">
        <identifier>urn:cts:formulae:elexicon.abbas.deu001</identifier>
        <dc:creator>Horst Lößlein</dc:creator>
        <dc:format>application/tei+xml</dc:format>
        <dc:language>deu</dc:language>
        <dc:publisher xml:lang="mul">Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg</dc:publisher>
        <parent>urn:cts:formulae:elexicon.abbas</parent>
        <dc:title xml:lang="deu">Abbas, abbatissa (deu)</dc:title>
        <dc:type>cts:edition</dc:type>
        <structured-metadata>
        <dct:bibliographicCitation>Lößlein, Horst, "Abbas, abbatissa", in: Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg (2019-05-07), [URL: https://werkstatt.formulae.uni-hamburg.de/texts/urn:cts:formulae:elexicon.abbas.deu001/passage/all]</dct:bibliographicCitation>
        <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
        <dct:isReferencedBy>uir illi &lt;span class='elex-word'&gt;abbate&lt;/span&gt; interpellauerunt hominem%ab ipso &lt;span class='elex-word'&gt;abbate&lt;/span&gt; uel qui</dct:isReferencedBy>
        <dct:isReferencedBy>patri illo &lt;span class='elex-word'&gt;abbati&lt;/span&gt; uel omnis</dct:isReferencedBy>
        <dct:isReferencedBy>patri illo &lt;span class='elex-word'&gt;abbate&lt;/span&gt; ego illi</dct:isReferencedBy>
        <dct:isReferencedBy>uir illo &lt;span class='elex-word'&gt;abbate&lt;/span&gt; uel reliquis%fuit ipsius &lt;span class='elex-word'&gt;abbati&lt;/span&gt; uel quibus</dct:isReferencedBy>
        <dct:isReferencedBy>ante illo &lt;span class='elex-word'&gt;abbate&lt;/span&gt; uel reliquis,%fuit ipsius &lt;span class='elex-word'&gt;abbate&lt;/span&gt;, ut dum</dct:isReferencedBy>
        <dct:isReferencedBy>uir illo &lt;span class='elex-word'&gt;abbati&lt;/span&gt; uel reliquis</dct:isReferencedBy>
        <dct:isReferencedBy>uir illo &lt;span class='elex-word'&gt;abbati&lt;/span&gt;, propria pecunia</dct:isReferencedBy>
        <dct:references></dct:references>
        <dct:created>2019-05-07</dct:created>
        </structured-metadata>
        </collection>
        </members>
        <structured-metadata>
        <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
        </structured-metadata>
        </collection>
        </members>
        <structured-metadata>
        <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
        <bib:AbbreviatedTitle></bib:AbbreviatedTitle>
        </structured-metadata>
        </collection>"""
        TG = XmlCapitainsCollectionMetadata.parse(TG)
        self.assertEqual(TG.id, "urn:cts:formulae:elexicon")

    def test_xml_TextInventoryParsing(self):
        """ Tests XmlCapitainsCollectionMetadata parses without errors when children are included"""
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True)
        self.assertGreater(len(TI.children), 0)

    def test_xml_TextInventory_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        self.assertIsInstance(TI["default"], XmlCapitainsCollectionMetadata)
        self.assertIsInstance(TI["urn:cts:formulae:fulda_dronke"], XmlCapitainsCollectionMetadata)
        self.assertEqual(TI["urn:cts:formulae:fulda_dronke.dronke0041"].urn, "urn:cts:formulae:fulda_dronke.dronke0041")
        self.assertEqual(TI["urn:cts:formulae:fulda_dronke.dronke0041"].lang, None, "Non-readable should not have a language")
        self.assertEqual(TI["urn:cts:formulae:fulda_dronke.dronke0041.lat001"].lang, 'lat', "Readable should have a language")
        self.assertIsInstance(TI["urn:cts:formulae:fulda_dronke.dronke0041.lat001"], XmlCapitainsReadableMetadata)
        self.assertEqual(str(TI["urn:cts:formulae:fulda_dronke.dronke0041.lat001"].get_label()),
                         'Codex diplomaticus Fuldensis (Ed. Dronke) Nr. 41')
        self.assertEqual(str(TI["urn:cts:formulae:fulda_dronke.dronke0041.lat001"].get_property(DC, 'subject')[None][0]),
                         'Medieval Charter')
        self.assertEqual(len(TI['urn:cts:formulae:passau.heuwieser0073'].ancestors), 3)

    def test_xml_Textgroup_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        tg = TI['urn:cts:formulae:passau']
        self.assertIsInstance(tg["urn:cts:formulae:passau.heuwieser0073"], XmlCapitainsCollectionMetadata)
        self.assertEqual(tg["urn:cts:formulae:passau.heuwieser0073"].urn, "urn:cts:formulae:passau.heuwieser0073")
        self.assertFalse(tg['urn:cts:formulae:passau.heuwieser0073'].readable)
        self.assertTrue(tg['urn:cts:formulae:passau.heuwieser0073.lat001'].readable)
        self.assertIsInstance(tg["urn:cts:formulae:passau.heuwieser0073.lat001"], XmlCapitainsReadableMetadata)
        self.assertEqual(tg["urn:cts:formulae:passau.heuwieser0073.lat001"].lang, 'lat', "Readable should have a language")
        self.assertIn('Die Traditionen des Hochstifts Passau (Ed. Heuwieser) Nr. 73',
                      [str(x) for x in tg["urn:cts:formulae:passau.heuwieser0073.lat001"].get_property(DC, 'title', 'deu')],
                      "Readable should have a title")

    def test_xml_Work_GetItem(self):
        """ Test access through getItem obj[urn] """
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        wk = TI["urn:cts:formulae:passau.heuwieser0073"]
        self.assertIsInstance(wk["urn:cts:formulae:passau.heuwieser0073.lat002"], XmlCapitainsReadableMetadata)
        self.assertEqual(len(wk), 5, "There should be 5 texts in the work.")
        self.assertEqual(wk["urn:cts:formulae:passau.heuwieser0073.lat003"].urn, "urn:cts:formulae:passau.heuwieser0073.lat003")
        self.assertTrue(wk["urn:cts:formulae:passau.heuwieser0073.lat004"].readable)
        self.assertEqual(wk['urn:cts:formulae:passau.heuwieser0073.lat005'].lang, 'lat')

    def test_xml_work_getLang(self):
        """ Test access to translation """
        xml = """
        <cpt:collection 
            xmlns:cpt="http://purl.org/capitains/ns/1.0#" 
            xmlns:dct="http://purl.org/dc/terms/" 
            xmlns:bib="http://bibliotek-o.org/1.0/ontology/" 
            xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
            xmlns:dts="https://w3id.org/dts/api#"
            path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/__capitains__.xml">
            <cpt:identifier>urn:cts:formulae:elexicon.abbas</cpt:identifier>
            <dc:title xml:lang="lat">Abbas, abbatissa</dc:title>
            <dc:type>cts:work</dc:type>
            <cpt:members>
                <cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.abbas.deu001.xml" readable="true">
                    <cpt:identifier>urn:cts:formulae:elexicon.abbas.deu001</cpt:identifier>
                    <dc:language>deu</dc:language>
                    <dc:type>cts:edition</dc:type>
                    <dc:title xml:lang="deu">Abbas, abbatissa (deu)</dc:title>
                </cpt:collection>
                <cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.abbas.eng001.xml" readable="true">
                    <cpt:identifier>urn:cts:formulae:elexicon.abbas.eng001</cpt:identifier>
                    <dc:language>eng</dc:language>
                    <dc:type>cts:translation</dc:type>
                    <dc:title xml:lang="deu">Abbas, abbatissa (deu)</dc:title>
                </cpt:collection>
                <cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.abbas.eng002.xml" readable="true">
                    <cpt:identifier>urn:cts:formulae:elexicon.abbas.eng002</cpt:identifier>
                    <dc:language>eng</dc:language>
                    <dc:type>cts:translation</dc:type>
                    <dc:title xml:lang="deu">Abbas, abbatissa (deu)</dc:title>
                </cpt:collection>
                <cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.abbas.fre001.xml" readable="true">
                    <cpt:identifier>urn:cts:formulae:elexicon.abbas.fre001</cpt:identifier>
                    <dc:language>fre</dc:language>
                    <dc:type>cts:translation</dc:type>
                    <dc:title xml:lang="deu">Abbas, abbatissa (deu)</dc:title>
                </cpt:collection>
            </cpt:members>
            <cpt:structured-metadata>
            <rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
            </cpt:structured-metadata>
        </cpt:collection>""".replace("\n", "")
        W, children = XmlCapitainsCollectionMetadata.parse(resource=xml, _with_children=True)
        self.assertEqual(
            W.metadata.export(
                output=Mimetypes.JSON.Std,
                only=["http://purl.org/dc/elements/1.1/", 'http://purl.org/capitains/ns/1.0#']
            ),
            {'http://purl.org/capitains/ns/1.0#identifier': {None: 'Urn:Cts:Formulae:Elexicon.Abbas'},
             'http://purl.org/dc/elements/1.1/title': {'lat': 'Abbas, Abbatissa'},
             'http://purl.org/dc/elements/1.1/type': {None: 'Cts:Work'}},
            "Default export should work well"
        )

    def test_parse_error(self):
        with self.assertRaises(TypeError):
            TI = XmlCapitainsCollectionMetadata.parse(
                resource=5
            )

    def test_Inventory_pickle(self):
        """ Make sure that pickling and unpickling parsed collections does not result in data loss """
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        from pickle import dumps, loads

        dp = dumps(TI)
        # We save to xml and delete graph and instance to make sure things are working out
        xml = TI.export(Mimetypes.XML.GUIDELINES3)
        TI.graph.remove((None, None, None))
        del TI

        self.assertEqual(
            len(list(constants.__MYCAPYTAIN_TRIPLE_GRAPH__.triples((None, None, None)))),
            0,
            "There should be 0 metadata node for the child 1294 because everything is gone"
        )
        # Load back
        ti = loads(dp)
        tixml = ti.export(Mimetypes.XML.GUIDELINES3)
        self.assertEqual(
            len(list(ti["urn:cts:formulae:passau.heuwieser0083"].metadata.get(RDF_NAMESPACES.CAPITAINS.parent))),
            2,
            "There should be 2 parent collections for Passau 83"
        )
        self.assertEqual(
            len(list(ti["urn:cts:formulae:passau"].metadata.get(RDF_NAMESPACES.CAPITAINS.parent))),
            1,
            "There should be 1 parent collections for Passau"
        )
        self.assertEqual(*compareSTR(tixml, xml))

    def test_Inventory_metadata(self):
        """ Make sure that properties can be retrieved from the parsed collection """
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        self.assertIn("default", [str(x) for y in TI["urn:cts:formulae:passau"].get_property(RDF_NAMESPACES.CAPITAINS, "parent").values() for x in y])
        self.assertIn("default", [str(x) for x in TI["urn:cts:formulae:passau"].get_property(RDF_NAMESPACES.CAPITAINS, "parent", 'lat')])
        self.assertIn("default", [str(x) for x in TI["urn:cts:formulae:passau"].get_property(RDF_NAMESPACES.CAPITAINS, "parent", '')])
        self.assertIn("urn:cts:formulae:passau",
                      [str(x) for x in TI["urn:cts:formulae:passau"].get_property(RDF_NAMESPACES.CAPITAINS, "identifier", '')])
        self.assertEqual(len(TI["urn:cts:formulae:passau.heuwieser0083"].get_property(RDF_NAMESPACES.CAPITAINS, "parent", '')), 2,
                         "Passau 83 should have 2 parents.")
        self.assertIn("a:different.identifier",
                      [str(x) for x in TI["urn:cts:formulae:passau.heuwieser0083"].get_property(RDF_NAMESPACES.CAPITAINS, "parent", '')])
        self.assertIn("urn:cts:formulae:passau.heuwieser0083",
                      [str(x) for x in TI["urn:cts:formulae:passau.heuwieser0083"].get_property(RDF_NAMESPACES.CAPITAINS, "identifier", '')])
        self.assertIn('urn:cts:formulae:passau.heuwieser0083.lat001',
                      [str(x) for x in TI["urn:cts:formulae:passau.heuwieser0083.lat001"].get_property(RDF_NAMESPACES.CAPITAINS, "identifier", '')])
        self.assertIn('urn:cts:formulae:passau.heuwieser0083',
                      [str(x) for x in TI["urn:cts:formulae:passau.heuwieser0083.lat001"].get_property(RDF_NAMESPACES.CAPITAINS, "parent", '')])

    def test_export(self):
        """ Test export round-tripping of collections to and from XML """
        # compareSTR
        ti, children = XmlCapitainsCollectionMetadata.parse(resource=self.t, _with_children=True, recursive=True)
        self.assertEqual(*compareSTR(ti.export(Mimetypes.XML.GUIDELINES3, recursion_depth=8), self.t))

        # Test individual :
        self.assertEqual(*compareSTR(ti["urn:cts:formulae:elexicon"].export(Mimetypes.XML.GUIDELINES3, recursion_depth=8),
                                     self.tg))
        self.assertEqual(
            *compareSTR(ti["urn:cts:formulae:elexicon.abbas"].export(Mimetypes.XML.GUIDELINES3, recursion_depth=8),
                        self.wk))
        self.assertEqual(
            *compareSTR(ti["urn:cts:formulae:elexicon.abbas.deu001"].export(Mimetypes.XML.GUIDELINES3, recursion_depth=8),
                        self.readable))

    def test_import_to_text(self):
        """ Test export to CtsTextMetadata object """
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        ti_text = TI["urn:cts:formulae:passau.heuwieser0073.lat003"]

        txt_text = PrototypeCapitainsNode("urn:cts:formulae:passau.heuwieser0073.lat003")
        txt_text.set_metadata_from_collection(ti_text)
        self.assertEqual(str(txt_text.urn), "urn:cts:formulae:passau.heuwieser0073.lat003")
        self.assertEqual(
            str(txt_text.metadata.get_single(DC.term("type"))),
            "cts:edition",
            "Test get_single with no language"
        )
        self.assertEqual(
            re.sub(r'\s+', ' ', str(txt_text.metadata.get_single(DC.term("publisher"), "mul"))),
            "Formulae-Litterae-Chartae Projekt",
            "Test get_single with language."
        )
        self.assertIn('Matthew Munson (Universität Hamburg)',
                      [str(x) for x in txt_text.metadata.get(DC.term("contributor"))],
                      "Check get for a predicate that has multiple objects."
        )
        self.assertEqual('Die Traditionen des Hochstifts Passau (Ed. Heuwieser) Nr. 73',
                         str(list(txt_text.metadata.get(DC.term("title"), 'deu'))[0]),
                         "Check get with language.")
        self.assertEqual({'': [URIRef('urn:cts:formulae:passau.heuwieser0073')]}, txt_text.get_capitains_metadata('parent'),
                         "get_capitatins_metadata should work with no language given")
        self.assertEqual([URIRef('urn:cts:formulae:passau.heuwieser0073')], txt_text.get_capitains_metadata('parent', lang=''),
                         "get_capitatins_metadata should work with empty string for language")
        self.assertEqual([URIRef('urn:cts:formulae:passau.heuwieser0073')], txt_text.get_capitains_metadata('parent', lang='lat'),
                         "get_capitatins_metadata should work a language that does not exist")

    def test_addition_work(self):
        """ Test merging two Works together
        """
        tg = """<cpt:collection 
            xmlns:cpt="http://purl.org/capitains/ns/1.0#" 
            xmlns:dct="http://purl.org/dc/terms/" 
            xmlns:bib="http://bibliotek-o.org/1.0/ontology/" 
            xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
            xmlns:dts="https://w3id.org/dts/api#"
            path="../tests/testing_data/guidelines_v3/data/elexicon/__capitains__.xml">
<cpt:identifier>urn:cts:formulae:elexicon</cpt:identifier>
<dc:title xml:lang="fre">Lexique</dc:title>
<dc:title xml:lang="eng">Lexicon</dc:title>
<dc:title xml:lang="deu">Lexikon</dc:title>
<dc:type>cts:textgroup</dc:type>
<cpt:parent>default</cpt:parent>
<cpt:members>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/__capitains__.xml">
<cpt:identifier>urn:cts:formulae:elexicon.abbas</cpt:identifier>
<cpt:parent>urn:cts:formulae:elexicon</cpt:parent>
<dc:title xml:lang="lat">Abbas, abbatissa</dc:title>
<dc:type>cts:work</dc:type>
<cpt:members>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.abbas.fre001.xml" readable="true">
<cpt:identifier>urn:cts:formulae:elexicon.abbas.fre001</cpt:identifier>
<dc:publisher xml:lang="mul">Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg</dc:publisher>
<dc:language>fre</dc:language>
<cpt:parent>urn:cts:formulae:elexicon.abbas</cpt:parent>
<dc:type>cts:edition</dc:type>
<dc:title xml:lang="deu">Abbas, abbatissa (fre)</dc:title>
<dc:creator>Horst Lößlein</dc:creator>
<dc:format>application/tei+xml</dc:format>
</cpt:collection>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.abbas.eng001.xml" readable="true">
<cpt:identifier>urn:cts:formulae:elexicon.abbas.eng001</cpt:identifier>
<dc:publisher xml:lang="mul">Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg</dc:publisher>
<dc:language>eng</dc:language>
<cpt:parent>urn:cts:formulae:elexicon.abbas</cpt:parent>
<dc:type>cts:edition</dc:type>
<dc:title xml:lang="deu">Abbas, abbatissa (eng)</dc:title>
<dc:creator>Horst Lößlein</dc:creator>
<dc:format>application/tei+xml</dc:format>
</cpt:collection>
</cpt:members>
</cpt:collection>
</cpt:members>
</cpt:collection>""".replace("\n", "")
        resolver = XmlCapitainsLocalResolver('', autoparse=False)
        TG1, children = XmlCapitainsCollectionMetadata.parse(resource=self.tg, _with_children=True, recursive=True, resolver=resolver)
        self.assertEqual(
            len(TG1), 1,
            "There is one edition in TG1"
        )
        TG2, children = XmlCapitainsCollectionMetadata.parse(resource=tg, _with_children=True, recursive=True, resolver=resolver)
        self.assertEqual(
            len(TG2), 3,
            "There are now 3 texts in TTG2"
        )
        TG3 = TG1.update(TG2)
        self.assertEqual(
            len(TG3), 3,
            "There are three texts in merged objects"
        )
        self.assertEqual(str(TG3), str(TG1), "Addition in equal or incremental should have same result")
        self.assertEqual(
            list(TG3["urn:cts:formulae:elexicon.abbas.fre001"].ancestors),
            list(TG1["urn:cts:formulae:elexicon.abbas.deu001"].ancestors),
            "XmlCapitainsReadableMetadata OPP should be added to textgroup and original kept"
        )
        self.assertListEqual(
            sorted(TG3["urn:cts:formulae:elexicon.abbas.deu001"].readable_siblings, key=lambda x: str(x.urn)),
            sorted([
                TG3["urn:cts:formulae:elexicon.abbas.fre001"],
                TG3["urn:cts:formulae:elexicon.abbas.eng001"]
            ], key=lambda x: str(x.urn)),
            "New text gets access to siblings"
        )
        self.assertEqual(
            len(TG3["urn:cts:formulae:elexicon.abbas"]), 3,
            "There should be 3 texts in work"
        )

    def test_addition_textgroup(self):
        """ Test merging two textgroups together """
        tg = """<cpt:collection 
            xmlns:cpt="http://purl.org/capitains/ns/1.0#" 
            xmlns:dct="http://purl.org/dc/terms/" 
            xmlns:bib="http://bibliotek-o.org/1.0/ontology/" 
            xmlns:dc="http://purl.org/dc/elements/1.1/" 
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" 
            xmlns:dts="https://w3id.org/dts/api#"
            path="../tests/testing_data/guidelines_v3/data/elexicon/__capitains__.xml">
<cpt:identifier>urn:cts:formulae:elexicon</cpt:identifier>
<dc:title xml:lang="fre">Lexique</dc:title>
<dc:title xml:lang="eng">Lexicon</dc:title>
<dc:title xml:lang="deu">Lexikon</dc:title>
<dc:type>cts:textgroup</dc:type>
<cpt:parent>default</cpt:parent>
<cpt:members>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/regnum/__capitains__.xml">
<cpt:identifier>urn:cts:formulae:elexicon.regnum</cpt:identifier>
<cpt:parent>urn:cts:formulae:elexicon</cpt:parent>
<dc:title xml:lang="lat">Regnum</dc:title>
<dc:type>cts:work</dc:type>
<cpt:members>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.regnum.fre001.xml" readable="true">
<cpt:identifier>urn:cts:formulae:elexicon.regnum.fre001</cpt:identifier>
<dc:publisher xml:lang="mul">Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg</dc:publisher>
<dc:language>fre</dc:language>
<cpt:parent>urn:cts:formulae:elexicon.regnum</cpt:parent>
<dc:type>cts:edition</dc:type>
<dc:title xml:lang="deu">Regnum (fre)</dc:title>
<dc:creator>Horst Lößlein</dc:creator>
<dc:format>application/tei+xml</dc:format>
</cpt:collection>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/elexicon/abbas/elexicon.regnum.eng001.xml" readable="true">
<cpt:identifier>urn:cts:formulae:elexicon.regnum.eng001</cpt:identifier>
<dc:publisher xml:lang="mul">Formulae-Litterae-Chartae. Neuedition der frühmittelalterlichen Formulae, Hamburg</dc:publisher>
<dc:language>eng</dc:language>
<cpt:parent>urn:cts:formulae:elexicon.regnum</cpt:parent>
<dc:type>cts:edition</dc:type>
<dc:title xml:lang="deu">Regnum (eng)</dc:title>
<dc:creator>Horst Lößlein</dc:creator>
<dc:format>application/tei+xml</dc:format>
</cpt:collection>
</cpt:members>
</cpt:collection>
</cpt:members>
</cpt:collection>""".replace("\n", "")
        resolver = XmlCapitainsLocalResolver('', autoparse=False)
        TG1, children = XmlCapitainsCollectionMetadata.parse(resource=self.tg, _with_children=True, recursive=True, resolver=resolver)
        self.assertEqual(
            len(TG1), 1,
            "There is one edition in TG1"
        )
        TG2, children = XmlCapitainsCollectionMetadata.parse(resource=tg, _with_children=True, recursive=True, resolver=resolver)
        self.assertEqual(
            len(TG2), 3,
            "There are 3 editions in TG2"
        )
        TG3 = TG1.update(TG2)
        self.assertEqual(
            len(TG3), 3,
            "There are two texts in merged objects"
        )
        self.assertEqual(str(TG3), str(TG1), "Addition in equal or incremental should have same result")
        self.assertEqual(
            list(TG3["urn:cts:formulae:elexicon.abbas"].ancestors),
            list(TG3["urn:cts:formulae:elexicon.regnum"].ancestors),
            "XmlCapitainsCollectionMetadata OPP should be added to textgroup and original kept"
        )
        self.assertListEqual(
            sorted(TG3["urn:cts:formulae:elexicon"].members, key=lambda x: str(x.urn)),
            sorted([
                TG3["urn:cts:formulae:elexicon.abbas"],
                TG3["urn:cts:formulae:elexicon.regnum"]
            ], key=lambda x: str(x.urn)),
            "Children of the two matching workgroups should be added together"
        )
        self.assertEqual(
            len(TG3["urn:cts:formulae:elexicon"]), 3,
            "There should be 3 texts in textgroup"
        )

    def test_addition_collection(self):
        """ Test merging two collections together"""
        ti = """<cpt:collection path="None" xmlns:cpt="http://purl.org/capitains/ns/1.0#" xmlns:dct="http://purl.org/dc/terms/" xmlns:bib="http://bibliotek-o.org/1.0/ontology/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dts="https://w3id.org/dts/api#">
<cpt:identifier>defaultTic</cpt:identifier>
<cpt:members>
<cpt:collection path="None">
<cpt:identifier>default</cpt:identifier>
<cpt:parent>defaultTic</cpt:parent>
<cpt:members>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/salzburg/__capitains__.xml">
<cpt:identifier>urn:cts:formulae:salzburg</cpt:identifier>
<dc:type>cts:textgroup</dc:type>
<dc:title xml:lang="deu">&lt;span class="collection-origin"&gt;Salzburger&lt;/span&gt; Urkundenbuch</dc:title>
<cpt:parent>default</cpt:parent>
<cpt:members>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/salzburg/hauthaler-a0100/__capitains__.xml">
<cpt:identifier>urn:cts:formulae:salzburg.hauthaler-a0100</cpt:identifier>
<dc:title xml:lang="deu">Salzburger Urkundenbuch (Ed. Hauthaler); Codex A Nummer 100</dc:title>
<cpt:parent>urn:cts:formulae:salzburg</cpt:parent>
<dc:type>cts:work</dc:type>
<cpt:members>
<cpt:collection path="../tests/testing_data/guidelines_v3/data/salzburg/hauthaler-a0100/salzburg.hauthaler-a0100.lat001.xml" readable="true">
<cpt:identifier>urn:cts:formulae:salzburg.hauthaler-a0100.lat001</cpt:identifier>
<dc:language>lat</dc:language>
<dc:contributor>Prof. Dr. Philippe Depreux (Universität Hamburg)</dc:contributor>
<dc:contributor>Matthew Munson (Universität Hamburg)</dc:contributor>
<dc:contributor>Franziska Quaas (Universität Hamburg)</dc:contributor>
<dc:contributor>Morgane Pica (Praktikantin, Ecole nationale des Chartes, Paris, Frankreich)</dc:contributor>
<dc:contributor>Magdalena Hermann-Kowalczyk (Studentische Hilfskraft, Universität Hamburg)</dc:contributor>
<dc:description xml:lang="deu">a) Der Edle Vodalhard (Odalhard) übergibt dem Erzbischof 7 Huben am Ergoltsbach (Zufluss der kleinen Laber n. Landshut) mit Vorbehalt von 3 Joch in jeder Zelch und einer Hofstatt auf der Westseite als Hantgemâl (Stammgut), wofür er zu ewigem Eigenthum für sich und seine Nachkommen erhält, was er bisher zu Weidenbach (w. Ampfing) als Eigen innegehabt hat, nur ausgenommen die Kirche, den Kirchhof und eine Baustätte. b) Altorf übergibt dem Erzbischof am gleichen Tage 5 Hubcn zu Ergoltsbach und erhält dafür Volagangesperch (seit 13. Jahrh. Neumarkt a/Rott), wieder ausgenommen die Kirche, den Kirchhof und eine Baustätte.</dc:description>
<dc:title xml:lang="deu">Salzburger Urkundenbuch (Ed. Hauthaler); Codex A Nummer 100</dc:title>
<cpt:parent>urn:cts:formulae:salzburg.hauthaler-a0100</cpt:parent>
<dc:publisher xml:lang="mul">Formulae-Litterae-Chartae Projekt</dc:publisher>
<dc:source>Salzburger Urkundenbuch; Codex A Nummer 100, in: Willibald Hauthaler, Salzburger Urkundenbuch Bd. 2, Salzburg 1910, S. 162-163.</dc:source>
<dc:format>application/tei+xml</dc:format>
<dc:type>cts:edition</dc:type>
<cpt:structured-metadata>
<dct:created></dct:created>
<rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
<bib:editor>Hauthaler, Willibald</bib:editor>
<dct:dateCopyrighted>1910</dct:dateCopyrighted>
<dct:abstract xml:lang="deu"></dct:abstract>
<dct:bibliographicCitation>Salzburger Urkundenbuch; Codex A Nummer 100, in: Willibald Hauthaler, Salzburger Urkundenbuch Bd. 2, Salzburg 1910, S. 162-163.</dct:bibliographicCitation>
</cpt:structured-metadata>
</cpt:collection>
</cpt:members>
<cpt:structured-metadata>
<rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
</cpt:structured-metadata>
</cpt:collection>
</cpt:members>
<cpt:structured-metadata>
<bib:AbbreviatedTitle>Salzburger Urkundenbuch</bib:AbbreviatedTitle>
<rdf:type>http://purl.org/capitains/ns/1.0#collection</rdf:type>
</cpt:structured-metadata>
</cpt:collection>
</cpt:members>
</cpt:collection>
</cpt:members>
</cpt:collection>
        """
        resolver = XmlCapitainsLocalResolver('', autoparse=False)
        TI1, children = XmlCapitainsCollectionMetadata.parse(resource=self.t, _with_children=True, recursive=True, resolver=resolver)
        self.assertEqual(
            len(TI1), 1,
            "There is one edition in TI1"
        )
        self.assertEqual(len(TI1['default'].children), 1,
                         'The default collection should have one child.')
        TI2, children = XmlCapitainsCollectionMetadata.parse(resource=ti, _with_children=True, recursive=True, resolver=resolver)
        # If the collections are given the same resolver, they should be automatically merged with each other.
        self.assertEqual(len(TI1['default'].children), 2,
                         'Now the default collection should have 2 children.')
        self.assertEqual(TI1['default'].children, TI2['default'].children,
                         'The collections that are shared between the two collections should have the same children.')
        self.assertEqual(
            len(TI2), 2,
            "There should be 2 editions in TI2"
        )
        TI3 = TI1.update(TI2)
        self.assertEqual(
            len(TI3), 2,
            "There are two texts in merged objects"
        )
        self.assertEqual(str(TI3), str(TI1), "Addition in equal or incremental should have same result")
        self.assertEqual(
            list(TI3["urn:cts:formulae:elexicon"].ancestors),
            list(TI3["urn:cts:formulae:salzburg"].ancestors),
            "XmlCapitainsCollectionMetadata OPP should be added to inventory and original kept"
        )
        self.assertListEqual(
            sorted(TI3["default"].members, key=lambda x: str(x.urn)),
            sorted([
                TI3["urn:cts:formulae:elexicon"],
                TI3["urn:cts:formulae:salzburg"]
            ], key=lambda x: str(x.urn)),
            "Children of the two matching collections should be added together"
        )
        self.assertEqual(
            len(TI3["default"]), 2,
            "There should be 2 texts in inventory"
        )

    def test_additions_inventory(self):
        """ Test merging two partially overlapping inventories"""
        wrapper = """<cpt:collection path="None" xmlns:cpt="http://purl.org/capitains/ns/1.0#"
xmlns:dct="http://purl.org/dc/terms/" xmlns:bib="http://bibliotek-o.org/1.0/ontology/"
xmlns:dc="http://purl.org/dc/elements/1.1/"
xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:dts="https://w3id.org/dts/api#">
<cpt:identifier>defaultTic</cpt:identifier>
<cpt:members>{tg}</cpt:members>
</cpt:collection>"""
        coll1 = """<cpt:collection path="None">
            <cpt:identifier>default</cpt:identifier>
            <cpt:parent>defaultTic</cpt:parent>
            <cpt:members>
            <cpt:collection
                    path="../tests/testing_data/guidelines_v3/data/salzburg/__capitains__.xml">
                    <cpt:identifier>urn:cts:formulae:salzburg</cpt:identifier>
                    <dc:type>cts:textgroup</dc:type>
                    <dc:title xml:lang="deu">&lt;span
                        class="collection-origin"&gt;Salzburger&lt;/span&gt; Urkundenbuch</dc:title>
                    <cpt:parent>default</cpt:parent>
                    <cpt:members>
                        <cpt:collection
                            path="../tests/testing_data/guidelines_v3/data/salzburg/hauthaler-a0100/__capitains__.xml">
                            <cpt:identifier>urn:cts:formulae:salzburg.hauthaler-a0100</cpt:identifier>
                            <dc:title xml:lang="deu">Salzburger Urkundenbuch (Ed. Hauthaler); Codex
                                A Nummer 100</dc:title>
                            <cpt:parent>urn:cts:formulae:salzburg</cpt:parent>
                            <dc:type>cts:work</dc:type>
                            <cpt:members>
                                <cpt:collection
                                    path="../tests/testing_data/guidelines_v3/data/salzburg/hauthaler-a0100/salzburg.hauthaler-a0100.lat001.xml"
                                    readable="true">
                                    <cpt:identifier>urn:cts:formulae:salzburg.hauthaler-a0100.lat001</cpt:identifier>
                                    <dc:language>lat</dc:language>
                                    <dc:title xml:lang="deu">Salzburger Urkundenbuch (Ed.
                                        Hauthaler); Codex A Nummer 100</dc:title>
                                    <cpt:parent>urn:cts:formulae:salzburg.hauthaler-a0100</cpt:parent>
                                    <dc:format>application/tei+xml</dc:format>
                                    <dc:type>cts:edition</dc:type>
                                </cpt:collection>
                            </cpt:members>
                        </cpt:collection>
                    </cpt:members>
                </cpt:collection>
            </cpt:members>
        </cpt:collection>"""
        coll2 = """<cpt:collection path="None">
            <cpt:identifier>default2</cpt:identifier>
            <cpt:parent>defaultTic</cpt:parent>
            <cpt:members>
            <cpt:collection
                    path="../tests/testing_data/guidelines_v3/data/salzburg/__capitains__.xml">
                    <cpt:identifier>urn:cts:formulae:salzburg</cpt:identifier>
                    <dc:type>cts:textgroup</dc:type>
                    <dc:title xml:lang="deu">&lt;span
                        class="collection-origin"&gt;Salzburger&lt;/span&gt; Urkundenbuch</dc:title>
                    <cpt:parent>default2</cpt:parent>
                    <cpt:members>
                        <cpt:collection
                            path="../tests/testing_data/guidelines_v3/data/salzburg/hauthaler-a0100/__capitains__.xml">
                            <cpt:identifier>urn:cts:formulae:salzburg.hauthaler-a0100</cpt:identifier>
                            <dc:title xml:lang="deu">Salzburger Urkundenbuch (Ed. Hauthaler); Codex
                                A Nummer 100</dc:title>
                            <cpt:parent>urn:cts:formulae:salzburg</cpt:parent>
                            <dc:type>cts:work</dc:type>
                            <cpt:members>
                                <cpt:collection
                                    path="../tests/testing_data/guidelines_v3/data/salzburg/hauthaler-a0100/salzburg.hauthaler-a0100.lat001.xml"
                                    readable="true">
                                    <cpt:identifier>urn:cts:formulae:salzburg.hauthaler-a0100.lat001</cpt:identifier>
                                    <dc:language>lat</dc:language>
                                    <dc:title xml:lang="deu">Salzburger Urkundenbuch (Ed.
                                        Hauthaler); Codex A Nummer 100</dc:title>
                                    <cpt:parent>urn:cts:formulae:salzburg.hauthaler-a0100</cpt:parent>
                                    <dc:format>application/tei+xml</dc:format>
                                    <dc:type>cts:edition</dc:type>
                                </cpt:collection>
                            </cpt:members>
                        </cpt:collection>
                    </cpt:members>
                </cpt:collection>
            </cpt:members>
        </cpt:collection>"""
        resolver = XmlCapitainsLocalResolver('', autoparse=False)
        TI1, children = XmlCapitainsCollectionMetadata.parse(resource=wrapper.format(tg=coll1),
                                                             _with_children=True, recursive=True, resolver=resolver)
        TI2, children = XmlCapitainsCollectionMetadata.parse(resource=wrapper.format(tg=coll2),
                                                             _with_children=True, recursive=True, resolver=resolver)
        TI3 = TI1.update(TI2)
        self.assertEqual(TI1, TI1, "Make sure that the same collection is equal to itself.")
        self.assertEqual(
            len(TI3), 1,
            "There is only one text in merged objects"
        )
        self.assertCountEqual(
            [x for x in TI3["urn:cts:formulae:salzburg"].parent],
            ['default', 'default2'],
            "The single textgroup should have both collections as parents."
        )
        self.assertCountEqual(
            [x for x in TI3["urn:cts:formulae:salzburg"].ancestors],
            ['default', 'default2', 'defaultTic'],
            "Make sure that the first two elements of parents are the direct parents."
        )
        self.assertListEqual(
            sorted(TI3["defaultTic"].members, key=lambda x: str(x.urn)),
            sorted([
                TI3["default"],
                TI3["default2"]
            ], key=lambda x: str(x.urn)),
            "Children of the two matching inventories should be added together"
        )
        self.assertCountEqual(
            TI3["default"].texts, TI3["default2"].texts,
            "The repeated text in both collections should be the same object."
        )


    def test_wrong_urn_addition_work_textgroup(self):
        """ Checks that we cannot add work or textgroup with different URN"""
        from MyCapytain.errors import InvalidURN
        self.assertRaises(
            TypeError,
            lambda x: XmlCapitainsCollectionMetadata(urn="urn:cts:latinLit:phi1294.phi002").update(XmlCapitainsReadableMetadata(urn="urn:cts:latinLit:phi1297.phi002")),
            "Addition of different work with different URN should fail"
        )
        self.assertRaises(
            InvalidURN,
            lambda x: XmlCapitainsCollectionMetadata(urn="urn:cts:latinLit:phi1294").update(
                XmlCapitainsCollectionMetadata(urn="urn:cts:latinLit:phi1297")),
            "Addition of different work with different URN should fail"
        )

    def test_structured_metadata_parse(self):
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        self.assertEqual(
            list(
                TI["urn:cts:formulae:salzburg.hauthaler-a0100.lat001"].metadata.
                    get(URIRef("http://bibliotek-o.org/1.0/ontology/editor"))
            ),
            [Literal("Hauthaler, Willibald")]
        )
        self.assertEqual(
            list(
                TI["urn:cts:formulae:salzburg.hauthaler-a0100.lat001"].metadata.
                    get(URIRef("http://purl.org/dc/terms/dateCopyrighted"))
            ),
            [Literal(1910)]
        )
        self.assertEqual(
            list(
                TI["urn:cts:formulae:salzburg.hauthaler-a0100.lat001"].metadata.get(URIRef("http://purl.org/dc/terms/bibliographicCitation"))
            ),
            [Literal("Salzburger Urkundenbuch; Codex A Nummer 100, in: Willibald Hauthaler, Salzburger Urkundenbuch Bd. 2, Salzburg 1910, S. 162-163.")]
        )

    def test_export_structured_metadata(self):
        TI, children = XmlCapitainsCollectionMetadata.parse(resource=self.getCapabilities, _with_children=True, recursive=True)
        out = xmlparser(TI['urn:cts:formulae:passau'].export(Mimetypes.XML.GUIDELINES3, recursion_depth=8))

        self.assertCountEqual(
            out.xpath("./cpt:structured-metadata/bib:AbbreviatedTitle", namespaces=XPATH_NAMESPACES),
            ['Traditionen Passau']
        )
        edition = out.xpath("./cpt:members/cpt:collection/cpt:members/cpt:collection[cpt:identifier= 'urn:cts:formulae:passau.heuwieser0083.lat002']", namespaces=XPATH_NAMESPACES)[0]
        self.assertEqual(edition.get('readable'), "true", 'Attributes should be retained.')
        self.assertCountEqual(
            edition.xpath("./cpt:structured-metadata/dct:dateCopyrighted", namespaces=XPATH_NAMESPACES),
            [1930, 1969]
        )
        self.assertCountEqual(
            edition.xpath("./cpt:structured-metadata/bib:editor", namespaces=XPATH_NAMESPACES),
            ["Heuwieser, Max"]
        )
        self.assertCountEqual(
            edition.xpath("./cpt:structured-metadata/dct:abstract[@xml:lang = 'deu']/text()", namespaces=XPATH_NAMESPACES),
            ["A great charter!"]
        )


class TestCitation(unittest.TestCase):
    def test_empty(self):
        a = XmlCtsCitation(name="none")
        self.assertEqual(a.export(), "")

    def test_ingest_and_match(self):
        """ Ensure matching and parsing XML works correctly """
        xml = xmlparser("""<collection xmlns:ti="http://chs.harvard.edu/xmlns/cts"
            xmlns:dct="http://purl.org/dc/terms/"
            xmlns:dc="http://purl.org/dc/elements/1.1/"
            xmlns="http://purl.org/capitains/ns/1.0#"
            xmlns:owl="http://www.w3.org/2002/07/owl#"
            xmlns:bib="http://bibliotek-o.org/1.0/ontology/"
            readable="true" path="./salzburg.hauthaler-a0100.lat001.xml">
             <identifier>urn:cts:formulae:salzburg.hauthaler-a0100.lat001</identifier>
             <parent>urn:cts:formulae:salzburg.hauthaler-a0100</parent>
             <dc:title xml:lang="deu">Salzburger Urkundenbuch (Ed. Hauthaler); Codex A Nummer 100</dc:title>
             <dc:description xml:lang="deu">a) Der Edle Vodalhard (Odalhard) übergibt dem Erzbischof 7 Huben am Ergoltsbach (Zufluss der kleinen Laber n. Landshut) mit Vorbehalt von 3 Joch in jeder Zelch und einer Hofstatt auf der Westseite als Hantgemâl (Stammgut), wofür er zu ewigem Eigenthum für sich und seine Nachkommen erhält, was er bisher zu Weidenbach (w. Ampfing) als Eigen innegehabt hat, nur ausgenommen die Kirche, den Kirchhof und eine Baustätte. b) Altorf übergibt dem Erzbischof am gleichen Tage 5 Hubcn zu Ergoltsbach und erhält dafür Volagangesperch (seit 13. Jahrh. Neumarkt a/Rott), wieder ausgenommen die Kirche, den Kirchhof und eine Baustätte.</dc:description>
             <dc:language>lat</dc:language>
             <dc:type>cts:edition</dc:type>
             <dc:contributor>Prof. Dr. Philippe Depreux (Universität Hamburg)</dc:contributor>
             <dc:contributor>Franziska Quaas (Universität Hamburg)</dc:contributor>
             <dc:contributor>Magdalena Hermann-Kowalczyk (Studentische Hilfskraft, Universität Hamburg)</dc:contributor>
             <dc:contributor>Matthew Munson (Universität Hamburg)</dc:contributor>
             <dc:contributor>Morgane Pica (Praktikantin, Ecole nationale des Chartes, Paris, Frankreich)</dc:contributor>
             <dc:publisher xml:lang="mul">Formulae-Litterae-Chartae Projekt</dc:publisher>
             <dc:format>application/tei+xml</dc:format>
             <dc:source>Salzburger Urkundenbuch; Codex A Nummer 100, in: Willibald Hauthaler, Salzburger Urkundenbuch Bd. 2, Salzburg 1910, S. 162-163.</dc:source>
             <structured-metadata>
                <dct:abstract xml:lang="deu"/>
                <bib:editor>Hauthaler, Willibald</bib:editor>
                <dct:dateCopyrighted>1910</dct:dateCopyrighted>
                <dct:created/>
                <dct:bibliographicCitation>Salzburger Urkundenbuch; Codex A Nummer 100, in: Willibald Hauthaler, Salzburger Urkundenbuch Bd. 2, Salzburg 1910, S. 162-163.</dct:bibliographicCitation>
                <ti:online>
                    <ti:citationMapping>
                        <ti:citation label='book' xpath="/tei:div[@n='?']" scope='/tei:TEI/tei:text/tei:body/tei:div'>
                            <ti:citation label='poem' xpath="/tei:div[@n='?']"  scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']">
                                <ti:citation label='line' xpath="/tei:l[@n='?']"  scope="/tei:TEI/tei:text/tei:body/tei:div/tei:div[@n='?']/tei:div[@n='?']"></ti:citation>
                            </ti:citation>
                        </ti:citation>
                    </ti:citationMapping>
                </ti:online>
             </structured-metadata>
          </collection>""".replace("\n", ""))
        citation = (XmlCapitainsReadableMetadata.parse(xml)).citation
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
