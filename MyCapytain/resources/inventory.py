# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml
   :synopsis: XML based Text and repository

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals

from MyCapytain.resources.proto import inventory, text
from MyCapytain.common.reference import Citation as CitationPrototype
from MyCapytain.common.utils import xmlparser, NS

from six import text_type as str
import collections


class Citation(CitationPrototype):
    """ Citation XML implementation for TextInventory

    """
    def __str__(self):
        """ Returns a string text inventory version of the object 

        :Example:
            >>>    a = Citation(name="book", xpath="/tei:TEI/tei:body/tei:text/tei:div", scope="/tei:div[@n=\"1\"]")
            >>>    str(a) == <ti:citation label='book' xpath='/tei:TEI/tei:body/tei:text/tei:div' scope='/tei:div[@n=\"1\"]'>...</ti:citation>
        """
        if self.xpath is None and self.scope is None and self.refsDecl is None:
            return ""

        child = ""
        if isinstance(self.child, Citation):
            child = str(self.child)

        label = ""
        if self.name is not None:
            label = self.name

        return "<ti:citation label='{label}' xpath='{xpath}' scope='{scope}'>{child}</ti:citation>".format(
            child=child,
            xpath=self.xpath,
            scope=self.scope,
            label=label
        )

    @staticmethod
    def ingest(resource, element=None, xpath="ti:citation"):
        """ Ingest xml to create a citation

        :param xml: XML on which to do xpath
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

def xpathDict(xml, xpath, children, parents, **kwargs):
    """ Returns a default Dict given certain informations
        

    :param xml: An xml tree
    :type xml: etree
    :param xpath: XPath to find children
    :type basestring:
    :param children: Object identifying children
    :type children: inventory.Resource
    :param parents: Tuple of parents
    :type parents: tuple.<inventory.Resource>
    :rtype: collections.defaultdict.<basestring, inventory.Resource>
    :returns: Dictionary of children
    """
    return collections.defaultdict(children, **dict(
        (
            child.get("urn"),
            children(
                resource=child,
                urn=child.get("urn"),
                parents=parents,
                **kwargs
            )
        ) for child in xml.xpath(xpath, namespaces=NS))
    )


class Text(inventory.Text):
    """ Represents a CTS Text
        
        ..automethod:: __str__
    """
    def __init__(self, **kwargs):
        super(Text, self).__init__(**kwargs)

    def __str__(self):
        """ Print the xml of the text
        
        :rtype: basestring
        :returns: XML representation of the text
        """
        strings = []
        tag_start = "edition"
        tag_end = tag_start
        if self.subtype == "Translation":
            tag_start = "translation"
            tag_end = "translation"
            if self.lang:
                tag_start = tag_start + " xml:lang='" + self.lang + "'"

        if self.urn is not None:
            strings.append(
                "<ti:{0} urn='{1}' workUrn='{2}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(
                    tag_start,
                    self.urn,
                    self.urn["work"]
                )
            )
        else:
            if len(self.parents) > 0 and hasattr(self.parents[0], "urn") is True:
                strings.append(
                    "<ti:{0} workUrn='{1}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(
                        tag_start,
                        self.parents[0].urn
                    )
                )
            else:
                strings.append(
                    "<ti:{0} xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(
                        tag_start
                    )
                )

        namespaces = []
        for tag, metadatum in self.metadata:
            if tag == "namespaceMapping":
                for abbr, ns in metadatum:
                    namespaces.append(
                        '<ti:namespaceMapping abbreviation=\'{0}\' nsURI=\'{1}\'/>'.format(
                            abbr,
                            ns
                        )
                    )
            else:
                for lang, value in metadatum:
                    strings.append(
                        "<ti:{tag} xml:lang='{lang}'>{value}</ti:{tag}>".format(
                            tag=tag,
                            lang=lang,
                            value=value
                        )
                    )

        # Maybe should have an online object...
        docname = ""
        if self.docname is not None:
            docname = ' docname=\'{0}\''.format(self.docname)

        strings.append("<ti:online{0}>".format(docname))

        if self.validate is not None:
            strings.append('<ti:validate schema=\'{0}\'/>'.format(self.validate))

        if len(namespaces) > 0:
            strings.append("".join(namespaces))

        if self.citation is not None:
            strings.append("<ti:citationMapping>")
            strings.append(str(self.citation))
            strings.append("</ti:citationMapping>")

        strings.append("</ti:online>")

        strings.append("</ti:{0}>".format(tag_end))
        return "".join(strings)

    def export(self, output="xml", **kwargs):
        """ Create a {format} version of the Work
        
        :param output: Format to be chosen (Only XML for now)
        :type output: basestring, citation
        :rtype: lxml.etree._Element
        :returns: XML representation of the object
        """
        if output == "xml":
            return xmlparser(str(self))
        elif issubclass(output, text.Text):
            complete_metadata = self.metadata
            for parent in self.parents:
                if isinstance(parent, inventory.Resource):
                    complete_metadata = complete_metadata + parent.metadata
            return output(urn=self.urn, citation=self.citation, metadata=complete_metadata, **kwargs)

    def __findCitations(self, xml, xpath="ti:citation"):
        """ Find citation in current xml. Used as a loop for self.xmlparser()
        
        :param xml: Xml resource to be parsed
        :param xpath: Xpath to use to retrieve the xml node
        """
        self.citation = Citation.ingest(xml, self.citation, xpath)


    def parse(self, resource):
        """ Parse a resource to feed the object
        
        :param resource: An xml representation object
        :type resource: basestring or lxml.etree._Element
        :returns: None
        """
        self.xml = xmlparser(resource)

        if self.subtype == "Translation":
            lang = self.xml.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang is not None:
                self.lang = lang

        for child in self.xml.xpath("ti:description", namespaces=NS):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                self.metadata["description"][lg] = child.text

        for child in self.xml.xpath("ti:label", namespaces=NS):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                self.metadata["label"][lg] = child.text

        self.__findCitations(
            xml=self.xml,
            xpath="ti:online/ti:citationMapping/ti:citation"
        )

        online = self.xml.xpath("ti:online", namespaces=NS)
        if len(online) > 0:
            online = online[0]
            self.docname = online.get("docname")
            for validate in online.xpath("ti:validate", namespaces=NS):
                self.validate = validate.get("schema")
            for namespaceMapping in online.xpath("ti:namespaceMapping", namespaces=NS):
                self.metadata["namespaceMapping"][namespaceMapping.get("abbreviation")] = namespaceMapping.get("nsURI")

        return None


def Edition(resource=None, urn=None, parents=None):
    """ Create an edition subtyped Text object 
    """
    return Text(resource=resource, urn=urn, parents=parents, subtype="Edition")


def Translation(resource=None, urn=None, parents=None):
    """ Create a translation subtyped Text object 
    """
    return Text(resource=resource, urn=urn, parents=parents, subtype="Translation")


class Work(inventory.Work):

    """ Represents a CTS Textgroup in XML

        ..automethod:: __str__
    """

    def __init__(self, **kwargs):

        super(Work, self).__init__(**kwargs)

    def __str__(self):
        """ Print the xml of the work
        
        :rtype: basestring
        :returns: XML representation of the work
        """
        strings = []
        if self.urn is not None:
            strings.append(
                "<ti:work urn='{0}' groupUrn='{1}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(
                    self.urn, self.urn["textgroup"])
            )
        else:
            if len(self.parents) > 0 and hasattr(self.parents[0], "urn") is True:
                strings.append("<ti:work groupUrn='{0}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(
                    self.parents[0].urn)
                )
            else:
                strings.append("<ti:work xmlns:ti='http://chs.harvard.edu/xmlns/cts'>")

        for tag, metadatum in self.metadata:
            for lang, value in metadatum:
                strings.append("<ti:{tag} xml:lang='{lang}'>{value}</ti:{tag}>".format(tag=tag, lang=lang, value=value))

        # Dev trick : For tests, we need to have always the same order....
        keys = sorted([urn for urn in self.texts])
        for urn in keys:
            strings.append(str(self.texts[urn]))

        strings.append("</ti:work>")
        return "".join(strings)

    def export(self, output="xml"):
        """ Create a {format} version of the Work
        
        :param output: Format to be chosen (Only XML for now)
        :type output: basestring
        :rtype: lxml.etree._Element
        :returns: XML representation of the object
        """
        return xmlparser(str(self))

    def parse(self, resource):
        """ Parse a resource 

        :param resource: Element rerpresenting a work
        :param type: basestring, etree._Element
        """
        self.xml = xmlparser(resource)

        lang = self.xml.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
            self.lang = lang

        for child in self.xml.xpath("ti:title", namespaces=NS):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                self.metadata["title"][lg] = child.text

        self.__editions = xpathDict(
            xml=self.xml,
            xpath='ti:edition',
            children=Edition,
            parents=tuple([self]) + self.parents
        )
        self.__translations = xpathDict(
            xml=self.xml,
            xpath='ti:translation',
            children=Translation,
            parents=tuple([self]) + self.parents
        )

        self.texts = collections.defaultdict(Text)
        for urn in self.__editions:
            self.texts[urn] = self.__editions[urn]
        for urn in self.__translations:
            self.texts[urn] = self.__translations[urn]

        return self.texts


class TextGroup(inventory.TextGroup):

    """ Represents a CTS Textgroup in XML
        
        .. automethod:: __str__
    """

    def __init__(self, **kwargs):
        super(TextGroup, self).__init__(**kwargs)

    def __str__(self):
        """ Print the xml of the text group
        
        :rtype: basestring
        :returns: XML representation of the textgroup
        """
        strings = []
        if self.urn is not None:
            strings.append("<ti:textgroup urn='{0}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(self.urn))
        else:
            strings.append("<ti:textgroup xmlns:ti='http://chs.harvard.edu/xmlns/cts'>")

        for tag, metadatum in self.metadata:
            for lang, value in metadatum:
                strings.append("<ti:{tag} xml:lang='{lang}'>{value}</ti:{tag}>".format(tag=tag, lang=lang, value=value))

        for urn in self.works:
            strings.append(str(self.works[urn]))

        strings.append("</ti:textgroup>")
        return "".join(strings)

    def export(self, output="xml"):
        """ Create a {format} version of the TextInventory
        
        :param output: Format to be chosen (Only XML for now)
        :type output: basestring
        :rtype: lxml.etree._Element
        :returns: XML representation of the object
        """
        return xmlparser(str(self))

    def parse(self, resource):
        """ Parse a resource 

        :param resource: Element rerpresenting the textgroup
        :param type: basestring, etree._Element
        """
        self.xml = xmlparser(resource)

        for child in self.xml.xpath("ti:groupname", namespaces=NS):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                self.metadata["groupname"][lg] = child.text

        self.works = xpathDict(
            xml=self.xml,
            xpath='ti:work',
            children=Work,
            parents=(self, self.parents)
        )
        return self.works


class TextInventory(inventory.TextInventory):

    """ Represents a CTS Inventory file
        
    .. automethod:: __str__
    """

    def __init__(self, **kwargs):
        super(TextInventory, self).__init__(**kwargs)

    def __str__(self):
        """ Print the xml of the textinventory
        
        :rtype: basestring
        :returns: XML representation of the textinventory
        """
        strings = []
        if self.id is not None:
            strings.append("<ti:TextInventory tiid='{0}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(self.id))
        else:
            strings.append("<ti:TextInventory xmlns:ti='http://chs.harvard.edu/xmlns/cts'>")

        for urn in self.textgroups:
            strings.append(str(self.textgroups[urn]))
        strings.append("</ti:TextInventory>")
        return "".join(strings)

    def export(self, output="xml"):
        """ Create a {output} version of the TextInventory
        
        :param output: output to be chosen (Only XML for now)
        :type output: basestring
        :rtype: lxml.etree._Element
        :returns: XML representation of the object
        """
        return xmlparser(str(self))

    def parse(self, resource):
        """ Parse a resource 

        :param resource: Element representing the text inventory
        :param type: basestring, etree._Element
        """
        self.xml = xmlparser(resource)

        self.textgroups = xpathDict(
            xml=self.xml,
            xpath='//ti:textgroup',
            children=TextGroup,
            parents=self
        )
        return self.textgroups
