# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml
   :synopsis: XML based PrototypeText and repository

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals

from MyCapytain.resources.prototypes import text
from MyCapytain.resources.prototypes.cts import inventory as cts
from MyCapytain.common.reference import Citation as CitationPrototype
from MyCapytain.common.utils import xmlparser
from MyCapytain.common.constants import NS, Mimetypes


class Citation(CitationPrototype):
    """ Citation XML implementation for PrototypeTextInventory

    """

    @staticmethod
    def ingest(resource, element=None, xpath="ti:citation"):
        """ Ingest xml to create a citation

        :param resource: XML on which to do xpath
        :param element: Element where the citation should be stored
        :param xpath: XPath to use to retrieve citation

        :return: Citation
        """
        # Reuse of of find citation
        results = resource.xpath(xpath, namespaces=NS)
        if len(results) > 0:
            citation = Citation(
                name=results[0].get("label"),
                xpath=results[0].get("xpath"),
                scope=results[0].get("scope")
            )

            if isinstance(element, Citation):
                element.child = citation
                Citation.ingest(
                    resource=results[0],
                    element=element.child
                )
            else:
                element = citation
                Citation.ingest(
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
    :type parent: CTSCollection
    :rtype: collections.defaultdict.<basestring, inventory.Resource>
    :returns: Dictionary of children
    """
    for child in xml.xpath(xpath, namespaces=NS):
        cls.parse(
            resource=child,
            parent=parent,
            **kwargs
        )


class Text(cts.PrototypeText):
    """ Represents a CTS PrototypeText

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
        :type obj: Text
        :param xml: An xml representation object
        :type xml: lxml.etree._Element
        """

        for child in xml.xpath("ti:description", namespaces=NS):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_cts_property("description", child.text, lg)

        for child in xml.xpath("ti:label", namespaces=NS):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_cts_property("label", child.text, lg)

        obj.citation = Citation.ingest(xml, obj.citation, "ti:online/ti:citationMapping/ti:citation")

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


class Edition(cts.PrototypeEdition, Text):
    """ Create an edition subtyped PrototypeText object
    """
    @staticmethod
    def parse(resource, parent=None):
        xml = xmlparser(resource)
        o = Edition(urn=xml.get("urn"), parent=parent)
        Edition.parse_metadata(o, xml)

        return o


class Translation(cts.PrototypeTranslation, Text):
    """ Create a translation subtyped PrototypeText object
    """
    @staticmethod
    def parse(resource, parent=None):
        xml = xmlparser(resource)
        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")

        o = Translation(urn=xml.get("urn"), parent=parent)
        if lang is not None:
            o.lang = lang
        Translation.parse_metadata(o, xml)
        return o


class Work(cts.PrototypeWork):
    """ Represents a CTS Textgroup in XML
    """

    @staticmethod
    def parse(resource, parent=None):
        """ Parse a resource

        :param resource: Element rerpresenting a work
        :param type: basestring, etree._Element
        :param parent: Parent of the object
        :type parent: TextGroup
        """
        xml = xmlparser(resource)
        o = Work(urn=xml.get("urn"), parent=parent)

        lang = xml.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
            o.lang = lang

        for child in xml.xpath("ti:title", namespaces=NS):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_cts_property("title", child.text, lg)

        # Parse children
        xpathDict(xml=xml, xpath='ti:edition', cls=Edition, parent=o)
        xpathDict(xml=xml, xpath='ti:translation', cls=Translation, parent=o)

        return o


class TextGroup(cts.PrototypeTextGroup):
    """ Represents a CTS Textgroup in XML
    """

    @staticmethod
    def parse(resource, parent=None):
        """ Parse a textgroup resource

        :param resource: Element representing the textgroup
        :param parent: Parent of the textgroup
        """
        xml = xmlparser(resource)
        o = TextGroup(urn=xml.get("urn"), parent=parent)

        for child in xml.xpath("ti:groupname", namespaces=NS):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_cts_property("groupname", child.text, lg)

        # Parse Works
        xpathDict(xml=xml, xpath='ti:work', cls=Work, parent=o)
        return o


class TextInventory(cts.PrototypeTextInventory):
    """ Represents a CTS Inventory file
    """

    @staticmethod
    def parse(resource):
        """ Parse a resource 

        :param resource: Element representing the text inventory
        :param type: basestring, etree._Element
        """
        xml = xmlparser(resource)
        o = TextInventory(name=xml.xpath("//ti:TextInventory", namespaces=NS)[0].get("tiid") or "")
        # Parse textgroups
        xpathDict(xml=xml, xpath='//ti:textgroup', cls=TextGroup, parent=o)
        return o
