from .proto import inventory
from lxml import etree
from io import IOBase, StringIO
from past.builtins import basestring
import collections


ns = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "ahab": "lala",
    "ti": "http://chs.harvard.edu/xmlns/cts"
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
    parsed = etree.parse(xml)
    if doclose:
        xml.close()
    return parsed


def parseUrn(urn):
    """ Parse a urn cts string
    :param urn: Urn identifying a textinventory object
    :type urn: basestring
    :rtype: Dict
    :returns: Decomposed urn
    """
    urn = urn.split(":")
    parsed = {}
    parsed["prefix"] = ":".join(urn[0:3])

    if len(urn) == 4:
        urn = urn[3].split(".")
    if len(urn) >= 1:
        parsed["textgroup"] = urn[0]
    if len(urn) >= 2:
        parsed["work"] = urn[1]
    if len(urn) >= 3:
        parsed["text"] = urn[2]
    return parsed

def joinUrn(level, urn):
    """ Join a parsed Urn
    """
    if level == "textgroup":
        return ":".join([urn["prefix"], urn["textgroup"]])
    elif level == "work":
        return ":".join([urn["prefix"], ".".join([urn["textgroup"], urn["work"]])])
    elif level == "text":
        return ":".join([urn["prefix"], ".".join([urn["textgroup"], urn["work"], urn["text"]])])
    else:
        return ""


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

class Work(inventory.Work):

    """ Represents a CTS Textgroup in XML
    """

    def __init__(self, **kwargs):
        super(Work, self).__init__(**kwargs)
        self.title = {}

    def parse(self, resource):
        return None

class TextGroup(inventory.TextGroup):

    """ Represents a CTS Textgroup in XML
    """

    def __init__(self, **kwargs):
        super(TextGroup, self).__init__(**kwargs)
        self.groupname = {}

    def __getitem__(self, urn):
        """ Allows Obj[urn] returning an element
        :param key: A urn
        :type key: basestring
        :rtype: inventory.Resource
        :returns: inventory.Resource Corresponding
        """
        if urn == 0:
            return self
        elif not isinstance(urn, basestring):
            raise TypeError("Expected string, got something else")

        raw_urn = urn
        urn = parseUrn(urn)
        element = None

        if "work" in urn:
            element = self.works[joinUrn("work", urn)]
        if "text" in urn:
            element = element[raw_urn]
        return element

    def parse(self, resource):
        self.xml = parse(resource)

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

    def __getitem__(self, urn):
        """ Allows Obj[urn] returning an element
        :param key: A urn
        :type key: basestring
        :rtype: TextGroup
        :returns: Textgroup Corresponding
        """
        if urn == 0:
            return self
        elif not isinstance(urn, basestring):
            raise TypeError("Expected string, got something else")

        raw_urn = urn
        urn = parseUrn(urn)
        element = None
        if "textgroup" in urn:
            element = self.textgroups[joinUrn("textgroup", urn)]
        if "work" in urn:
            element = element[raw_urn]
        if "text" in urn:
            element = element[raw_urn]
        return element

    def parse(self, resource):
        self.xml = parse(resource)

        self.textgroups = xpathDict(
            xml=self.xml,
            xpath='//ti:textgroup',
            children=TextGroup,
            parents=self
        )
        return self.textgroups
