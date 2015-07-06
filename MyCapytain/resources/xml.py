from .proto import inventory
from lxml import etree
from io import IOBase, StringIO
from past.builtins import basestring
import collections


ns = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "ahab": "http://localhost.local",
    "ti": "http://chs.harvard.edu/xmlns/cts",
    "xml": "http://www.w3.org/XML/1998/namespace"
}


def parse(xml):
    doclose = None
    if isinstance(xml, etree._Element):
        return xml
    elif isinstance(xml, IOBase):
        pass
    elif isinstance(xml, (basestring)):
        xml = StringIO(xml)
        doclose = True
    else:
        raise TypeError("Unsupported type of resource")
    parsed = etree.parse(xml).getroot()
    if doclose:
        xml.close()
    return parsed


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
        ) for child in xml.xpath(xpath, namespaces=ns))
    )


class Text(inventory.Text):
    """ Represents a CTS Text
    """
    def __init__(self, **kwargs):
        super(Text, self).__init__(**kwargs)

    def parse(self, resource):
        self.xml = parse(resource)

        if self.subtype == "Translation":
            lang = self.xml.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lang is not None:
                self.lang = lang

        for child in self.xml.xpath("ti:description", namespaces=ns):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                self.metadata["description"][lg] = child.text

        for child in self.xml.xpath("ti:label", namespaces=ns):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                self.metadata["label"][lg] = child.text

        return None

def Edition(resource=None, urn=None, parents=None):
    return Text(resource=resource, urn=urn, parents=parents, subtype="Edition")

def Translation(resource=None, urn=None, parents=None):
    return Text(resource=resource, urn=urn, parents=parents, subtype="Translation")

class Work(inventory.Work):

    """ Represents a CTS Textgroup in XML
    """

    def __init__(self, **kwargs):
        super(Work, self).__init__(**kwargs)

    def parse(self, resource):
        self.xml = parse(resource)

        lang = self.xml.get("{http://www.w3.org/XML/1998/namespace}lang")
        if lang is not None:
            self.lang = lang

        for child in self.xml.xpath("ti:title", namespaces=ns):
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
    """

    def __init__(self, **kwargs):
        super(TextGroup, self).__init__(**kwargs)

    def parse(self, resource):
        self.xml = parse(resource)

        for child in self.xml.xpath("ti:groupname", namespaces=ns):
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
    """

    def __init__(self, **kwargs):
        super(TextInventory, self).__init__(**kwargs)

    def parse(self, resource):
        self.xml = parse(resource)

        self.textgroups = xpathDict(
            xml=self.xml,
            xpath='//ti:textgroup',
            children=TextGroup,
            parents=self
        )
        return self.textgroups
