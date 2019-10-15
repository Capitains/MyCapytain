# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml
   :synopsis: XML based CtsTextMetadata and repository

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals

from rdflib import URIRef, Literal
from rdflib.namespace import XSD
from lxml.objectify import IntElement, FloatElement

from MyCapytain.resources.prototypes.cts import inventory as cts
from MyCapytain.common.reference._capitains_cts import Citation as CitationPrototype
from MyCapytain.common.utils import expand_namespace
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.common.constants import XPATH_NAMESPACES, Mimetypes, RDF_NAMESPACES


__all__ = [
    "XmlCtsCitation",
    "XmlCtsWorkMetadata",
    "XmlCtsCommentaryMetadata",
    "XmlCtsTranslationMetadata",
    "XmlCtsEditionMetadata",
    "XmlCtsTextgroupMetadata",
    "XmlCtsTextInventoryMetadata",
    "XmlCtsTextMetadata"
]

_CLASSES_DICT = {}


class XmlCtsCitation(CitationPrototype):
    """ XmlCtsCitation XML implementation for CtsTextInventoryMetadata

    """

    @classmethod
    def ingest(cls, resource, element=None, xpath="ti:citation"):
        """ Ingest xml to create a citation

        :param resource: XML on which to do xpath
        :param element: Element where the citation should be stored
        :param xpath: XPath to use to retrieve citation

        :return: XmlCtsCitation
        """
        # Reuse of of find citation
        results = resource.xpath(xpath, namespaces=XPATH_NAMESPACES)
        if len(results) > 0:
            citation = cls(
                name=results[0].get("label"),
                xpath=results[0].get("xpath"),
                scope=results[0].get("scope")
            )

            if isinstance(element, cls):
                element.child = citation
                cls.ingest(
                    resource=results[0],
                    element=element.child
                )
            else:
                element = citation
                cls.ingest(
                    resource=results[0],
                    element=element
                )

            return citation

        return None


def _xpathDict(xml, xpath, cls, parent, **kwargs):
    """ Returns a default Dict given certain information

    :param xml: An xml tree
    :type xml: etree
    :param xpath: XPath to find children
    :type xpath: str
    :param cls: Class identifying children
    :type cls: inventory.Resource
    :param parent: Parent of object
    :type parent: CtsCollection
    :rtype: collections.defaultdict.<basestring, inventory.Resource>
    :returns: Dictionary of children
    """
    children = []
    for child in xml.xpath(xpath, namespaces=XPATH_NAMESPACES):
        children.append(cls.parse(
            resource=child,
            parent=parent,
            **kwargs
        ))
    return children


def _parse_structured_metadata(obj, xml):
    """ Parse an XML object for structured metadata

    :param obj: Object whose metadata are parsed
    :param xml: XML that needs to be parsed
    """
    for metadata in xml.xpath("cpt:structured-metadata/*", namespaces=XPATH_NAMESPACES):
        tag = metadata.tag
        if "{" in tag:
            ns, tag = tuple(tag.split("}"))
            tag = URIRef(ns[1:]+tag)
            s_m = str(metadata)
            if s_m.startswith("urn:") or s_m.startswith("http:") or s_m.startswith("https:") or s_m.startswith("hdl:"):
                obj.metadata.add(
                    tag,
                    URIRef(metadata)
                )
            elif '{http://www.w3.org/XML/1998/namespace}lang' in metadata.attrib:
                obj.metadata.add(
                    tag,
                    s_m,
                    lang=metadata.attrib['{http://www.w3.org/XML/1998/namespace}lang']
                )
            else:
                if "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype" in metadata.attrib:
                    datatype = metadata.attrib["{http://www.w3.org/1999/02/22-rdf-syntax-ns#}datatype"]
                    if not datatype.startswith("http") and ":" in datatype:
                        datatype = expand_namespace(metadata.nsmap, datatype)
                    obj.metadata.add(tag, Literal(s_m, datatype=URIRef(datatype)))
                elif isinstance(metadata, IntElement):
                    obj.metadata.add(tag, Literal(int(metadata), datatype=XSD.integer))
                elif isinstance(metadata, FloatElement):
                    obj.metadata.add(tag, Literal(float(metadata), datatype=XSD.float))
                else:
                    obj.metadata.add(tag, s_m)


class XmlCtsTextMetadata(cts.CtsTextMetadata):
    """ Represents a CTS CtsTextMetadata

    """
    DEFAULT_EXPORT = Mimetypes.PYTHON.ETREE
    CLASS_CITATION = XmlCtsCitation

    @staticmethod
    def __findCitations(obj, xml, xpath="ti:citation"):
        """ Find citation in current xml. Used as a loop for xmlparser()

        :param xml: Xml resource to be parsed
        :param xpath: Xpath to use to retrieve the xml node
        """

    @classmethod
    def parse_metadata(cls, obj, xml):
        """ Parse a resource to feed the object

        :param obj: Obj to set metadata of
        :type obj: XmlCtsTextMetadata
        :param xml: An xml representation object
        :type xml: lxml.etree._Element
        """

        for child in xml.xpath("ti:description", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_cts_property("description", child.text, lg)

        for child in xml.xpath("ti:label", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_cts_property("label", child.text, lg)

        obj.citation = cls.CLASS_CITATION.ingest(xml, obj.citation, "ti:online/ti:citationMapping/ti:citation")

        # Added for commentary
        for child in xml.xpath("ti:about", namespaces=XPATH_NAMESPACES):
            obj.set_link(RDF_NAMESPACES.CTS.term("about"), child.get('urn'))

        _parse_structured_metadata(obj, xml)

        """
        online = xml.xpath("ti:online", namespaces=NS)
        if len(online) > 0:
            online = online[0]
            obj.docname = online.get("docname")
            for validate in online.xpath("ti:validate", namespaces=NS):
                obj.validate = validate.get("schema")
            for namespaceMapping in online.xpath("ti:namespaceMapping", namespaces=NS):
                obj.metadata["namespaceMapping"][namespaceMapping.get("abbreviation")] = namespaceMapping.get("nsURI")
        """

    def __init__(self, *args, **kwargs):
        super(XmlCtsTextMetadata, self).__init__(*args, **kwargs)
        self._path = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value


class XmlCtsEditionMetadata(cts.CtsEditionMetadata, XmlCtsTextMetadata):
    """ Create an edition subtyped CtsTextMetadata object
    """
    @classmethod
    def parse(cls, resource, parent=None):
        xml = xmlparser(resource)
        o = cls(urn=xml.get("urn"), parent=parent)
        cls.parse_metadata(o, xml)
        return o


class XmlCtsTranslationMetadata(cts.CtsTranslationMetadata, XmlCtsTextMetadata):
    """ Create a translation subtyped CtsTextMetadata object
    """
    @classmethod
    def parse(cls, resource, parent=None):
        xml = xmlparser(resource)
        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")

        o = cls(urn=xml.get("urn"), parent=parent)
        if lang is not None:
            o.lang = lang
        cls.parse_metadata(o, xml)
        return o


class XmlCtsCommentaryMetadata(cts.CtsCommentaryMetadata, XmlCtsTextMetadata):
    """ Create a commentary subtyped PrototypeText object
    """
    @classmethod
    def parse(cls, resource, parent=None):
        xml = xmlparser(resource)
        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")

        o = cls(urn=xml.get("urn"), parent=parent)
        if lang is not None:
            o.lang = lang
        cls.parse_metadata(o, xml)
        return o


class XmlCtsWorkMetadata(cts.CtsWorkMetadata):
    """ Represents a CTS Textgroup in XML
    """
    CLASS_EDITION = XmlCtsEditionMetadata
    CLASS_TRANSLATION = XmlCtsTranslationMetadata
    CLASS_COMMENTARY = XmlCtsCommentaryMetadata

    @classmethod
    def parse(cls, resource, parent=None, _with_children=False):
        """ Parse a resource

        :param resource: Element rerpresenting a work
        :param parent: Parent of the object
        :type parent: XmlCtsTextgroupMetadata
        """
        xml = xmlparser(resource)
        o = cls(urn=xml.get("urn"), parent=parent)

        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
            o.lang = lang

        for child in xml.xpath("ti:title", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_cts_property("title", child.text, lg)

        # Parse children
        children = []
        children.extend(_xpathDict(
            xml=xml, xpath='ti:edition',
            cls=cls.CLASS_EDITION, parent=o
        ))
        children.extend(_xpathDict(
            xml=xml, xpath='ti:translation',
            cls=cls.CLASS_TRANSLATION, parent=o
        ))
        children.extend(_xpathDict(
            xml=xml, xpath='ti:commentary',
            cls=cls.CLASS_COMMENTARY, parent=o
        ))

        _parse_structured_metadata(o, xml)

        if _with_children:
            return o, children
        return o


class XmlCtsTextgroupMetadata(cts.CtsTextgroupMetadata):
    """ Represents a CTS Textgroup in XML
    """
    CLASS_WORK = XmlCtsWorkMetadata

    @classmethod
    def parse(cls, resource, parent=None):
        """ Parse a textgroup resource

        :param resource: Element representing the textgroup
        :param parent: Parent of the textgroup
        """
        xml = xmlparser(resource)
        o = cls(urn=xml.get("urn"), parent=parent)

        for child in xml.xpath("ti:groupname", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_cts_property("groupname", child.text, lg)

        # Parse Works
        _xpathDict(xml=xml, xpath='ti:work', cls=cls.CLASS_WORK, parent=o)

        _parse_structured_metadata(o, xml)
        return o


class XmlCtsTextInventoryMetadata(cts.CtsTextInventoryMetadata):
    """ Represents a CTS Inventory file
    """
    CLASS_TEXTGROUP = XmlCtsTextgroupMetadata

    @classmethod
    def parse(cls, resource):
        """ Parse a resource

        :param resource: Element representing the text inventory
        """
        xml = xmlparser(resource)
        o = cls(name=xml.xpath("//ti:TextInventory", namespaces=XPATH_NAMESPACES)[0].get("tiid") or "")
        # Parse textgroups
        _xpathDict(xml=xml, xpath='//ti:textgroup', cls=cls.CLASS_TEXTGROUP, parent=o)
        return o
