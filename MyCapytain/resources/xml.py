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
            strings.append("<ti:{0} urn='{1}' workUrn='{2}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(tag_start, self.urn, self.urn["work"]))
        else:
            if len(self.parents) > 0 and hasattr(self.parents[0], "urn") is True:
                strings.append("<ti:work groupUrn='{0}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(self.parents.urn))
            else:
                strings.append("<ti:work xmlns:ti='http://chs.harvard.edu/xmlns/cts'>")

        for tag, metadatum in self.metadata:
            for lang, value in metadatum:
                strings.append("<ti:{tag} xml:lang='{lang}'>{value}</ti:{tag}>".format(tag=tag, lang=lang, value=value))

        """
        for urn in self.texts:
            string.append(str(self.texts[urn]))
        """

        strings.append("</ti:{0}>".format(tag_end))
        return "".join(strings)

    def export(self, format="xml"):
        """ Create a {format} version of the Work
        :param format: Format to be chosen (Only XML for now)
        :type param: basestring
        :rtype: lxml.etree._Element
        :returns: XML representation of the object
        """
        return parse(str(self))

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

    def __str__(self):
        """ Print the xml of the work
        :rtype: basestring
        :returns: XML representation of the work
        """
        strings = []
        if self.urn is not None:
            strings.append("<ti:work urn='{0}' groupUrn='{1}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(self.urn, self.urn["textgroup"]))
        else:
            if len(self.parents) > 0 and hasattr(self.parents[0], "urn") is True:
                strings.append("<ti:work groupUrn='{0}' xmlns:ti='http://chs.harvard.edu/xmlns/cts'>".format(self.parents.urn))
            else:
                strings.append("<ti:work xmlns:ti='http://chs.harvard.edu/xmlns/cts'>")

        for tag, metadatum in self.metadata:
            for lang, value in metadatum:
                strings.append("<ti:{tag} xml:lang='{lang}'>{value}</ti:{tag}>".format(tag=tag, lang=lang, value=value))

        for urn in self.texts:
            strings.append(str(self.texts[urn]))

        print(len(self.__editions), self.texts)
        strings.append("</ti:work>")
        return "".join(strings)

    def export(self, format="xml"):
        """ Create a {format} version of the Work
        :param format: Format to be chosen (Only XML for now)
        :type param: basestring
        :rtype: lxml.etree._Element
        :returns: XML representation of the object
        """
        return parse(str(self))

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

    def export(self, format="xml"):
        """ Create a {format} version of the TextInventory
        :param format: Format to be chosen (Only XML for now)
        :type param: basestring
        :rtype: lxml.etree._Element
        :returns: XML representation of the object
        """
        return parse(str(self))

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

    def export(self, format="xml"):
        """ Create a {format} version of the TextInventory
        :param format: Format to be chosen (Only XML for now)
        :type param: basestring
        :rtype: lxml.etree._Element
        :returns: XML representation of the object
        """
        return parse(str(self))

    def parse(self, resource):
        self.xml = parse(resource)

        self.textgroups = xpathDict(
            xml=self.xml,
            xpath='//ti:textgroup',
            children=TextGroup,
            parents=self
        )
        return self.textgroups
