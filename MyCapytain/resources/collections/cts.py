# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml
   :synopsis: XML based CtsTextMetadata and repository

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals

from MyCapytain.resources.prototypes import text
from MyCapytain.resources.prototypes.cts import inventory as cts
from MyCapytain.common.reference import Citation as CitationPrototype
from MyCapytain.common.utils import xmlparser
from MyCapytain.common.constants import XPath_Namespaces, Mimetypes, RDF_Namespaces


class XmlCtsCitation(CitationPrototype):
    """ XmlCtsCitation XML implementation for CtsTextInventoryMetadata

    """

    @staticmethod
    def ingest(resource, element=None, xpath="ti:citation"):
        """ Ingest xml to create a citation

        :param resource: XML on which to do xpath
        :param element: Element where the citation should be stored
        :param xpath: XPath to use to retrieve citation

        :return: XmlCtsCitation
        """
        # Reuse of of find citation
        results = resource.xpath(xpath, namespaces=XPath_Namespaces)
        if len(results) > 0:
            citation = XmlCtsCitation(
                name=results[0].get("label"),
                xpath=results[0].get("xpath"),
                scope=results[0].get("scope")
            )

            if isinstance(element, XmlCtsCitation):
                element.child = citation
                XmlCtsCitation.ingest(
                    resource=results[0],
                    element=element.child
                )
            else:
                element = citation
                XmlCtsCitation.ingest(
                    resource=results[0],
                    element=element
                )

            return citation

        return None


def xpathDict(xml, xpath, cls, parent, **kwargs):
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
    for child in xml.xpath(xpath, namespaces=XPath_Namespaces):
        cls.parse(
            resource=child,
            parent=parent,
            **kwargs
        )


class XmlCtsTextMetadata(cts.CtsTextMetadata):
    """ Represents a CTS CtsTextMetadata

    """
    DEFAULT_EXPORT = Mimetypes.PYTHON.ETREE

    @staticmethod
    def __findCitations(obj, xml, xpath="ti:citation"):
        """ Find citation in current xml. Used as a loop for xmlparser()

        :param xml: Xml resource to be parsed
        :param xpath: Xpath to use to retrieve the xml node
        """

    @staticmethod
    def parse_metadata(obj, xml):
        """ Parse a resource to feed the object

        :param obj: Obj to set metadata of
        :type obj: XmlCtsTextMetadata
        :param xml: An xml representation object
        :type xml: lxml.etree._Element
        """

        for child in xml.xpath("ti:description", namespaces=XPath_Namespaces):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_cts_property("description", child.text, lg)

        for child in xml.xpath("ti:label", namespaces=XPath_Namespaces):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_cts_property("label", child.text, lg)

        obj.citation = XmlCtsCitation.ingest(xml, obj.citation, "ti:online/ti:citationMapping/ti:citation")

        # Added for commentary
        for child in xml.xpath("ti:about", namespaces=XPath_Namespaces):
            #lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            #if lg is not None:
            obj.set_link(RDF_Namespaces.CTS.term("about"), child.get('urn'))

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


class XmlCtsEditionMetadata(cts.CtsEditionMetadata, XmlCtsTextMetadata):
    """ Create an edition subtyped CtsTextMetadata object
    """
    @staticmethod
    def parse(resource, parent=None):
        xml = xmlparser(resource)
        o = XmlCtsEditionMetadata(urn=xml.get("urn"), parent=parent)
        XmlCtsEditionMetadata.parse_metadata(o, xml)

        return o


class XmlCtsTranslationMetadata(cts.CtsTranslationMetadata, XmlCtsTextMetadata):
    """ Create a translation subtyped CtsTextMetadata object
    """
    @staticmethod
    def parse(resource, parent=None):
        xml = xmlparser(resource)
        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")

        o = XmlCtsTranslationMetadata(urn=xml.get("urn"), parent=parent)
        if lang is not None:
            o.lang = lang
        XmlCtsTranslationMetadata.parse_metadata(o, xml)
        return o

class XmlCtsCommentaryMetadata(cts.CtsCommentaryMetadata, XmlCtsTextMetadata):
    """ Create a commentary subtyped PrototypeText object
    """
    @staticmethod
    def parse(resource, parent=None):
        xml = xmlparser(resource)
        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")

        o = XmlCtsCommentaryMetadata(urn=xml.get("urn"), parent=parent)
        if lang is not None:
            o.lang = lang
        XmlCtsCommentaryMetadata.parse_metadata(o, xml)
        return o

class XmlCtsWorkMetadata(cts.CtsWorkMetadata):
    """ Represents a CTS Textgroup in XML
    """

    @staticmethod
    def parse(resource, parent=None):
        """ Parse a resource

        :param resource: Element rerpresenting a work
        :param type: basestring, etree._Element
        :param parent: Parent of the object
        :type parent: XmlCtsTextgroupMetadata
        """
        xml = xmlparser(resource)
        o = XmlCtsWorkMetadata(urn=xml.get("urn"), parent=parent)

        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
            o.lang = lang

        for child in xml.xpath("ti:title", namespaces=XPath_Namespaces):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_cts_property("title", child.text, lg)

        # Parse children
        xpathDict(xml=xml, xpath='ti:edition', cls=XmlCtsEditionMetadata, parent=o)
        xpathDict(xml=xml, xpath='ti:translation', cls=XmlCtsTranslationMetadata, parent=o)
       # Added for commentary
        xpathDict(xml=xml, xpath='ti:commentary', cls=XmlCtsCommentaryMetadata, parent=o)

        return o


class XmlCtsTextgroupMetadata(cts.CtsTextgroupMetadata):
    """ Represents a CTS Textgroup in XML
    """

    @staticmethod
    def parse(resource, parent=None):
        """ Parse a textgroup resource

        :param resource: Element representing the textgroup
        :param parent: Parent of the textgroup
        """
        xml = xmlparser(resource)
        o = XmlCtsTextgroupMetadata(urn=xml.get("urn"), parent=parent)

        for child in xml.xpath("ti:groupname", namespaces=XPath_Namespaces):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_cts_property("groupname", child.text, lg)

        # Parse Works
        xpathDict(xml=xml, xpath='ti:work', cls=XmlCtsWorkMetadata, parent=o)
        return o


class XmlCtsTextInventoryMetadata(cts.CtsTextInventoryMetadata):
    """ Represents a CTS Inventory file
    """

    @staticmethod
    def parse(resource):
        """ Parse a resource 

        :param resource: Element representing the text inventory
        :param type: basestring, etree._Element
        """
        xml = xmlparser(resource)
        o = XmlCtsTextInventoryMetadata(name=xml.xpath("//ti:TextInventory", namespaces=XPath_Namespaces)[0].get("tiid") or "")
        # Parse textgroups
        xpathDict(xml=xml, xpath='//ti:textgroup', cls=XmlCtsTextgroupMetadata, parent=o)
        return o
