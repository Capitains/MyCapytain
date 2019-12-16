from MyCapytain.resources.prototypes.metadata import Collection, ResourceCollection
from MyCapytain.resources.collections.cts import _parse_structured_metadata
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.common.constants import XPATH_NAMESPACES, Mimetypes, RDF_NAMESPACES
from MyCapytain.common.reference._capitains_cts import Citation as CitationPrototype
from MyCapytain.resources.prototypes.capitains import collection as capitains

XPATH_NAMESPACES.update({'dc': "http://purl.org/dc/elements/1.1/"})


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


class XmlCapitainsCitation(CitationPrototype):
    """ XmlCtsCitation XML implementation for CtsTextInventoryMetadata

    """

    @classmethod
    def ingest(cls, resource, element=None, xpath="ti:citation"):
        """ Ingest xml to create a citation

        :param resource: XML on which to do xpath
        :param element: Element where the citation should be stored
        :param xpath: XPath to use to retrieve citation

        :return: XmlCapitainsCitation
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


class XmlCapitainsReadableMetadata(capitains.CapitainsReadableMetadata):
    """ Represents a general Capitains CtsTextMetadata

    """
    DEFAULT_EXPORT = Mimetypes.PYTHON.ETREE
    CLASS_CITATION = XmlCapitainsCitation

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
        :type obj: XmlCapitainsTextMetadata
        :param xml: An xml representation object
        :type xml: lxml.etree._Element
        """

        for child in xml.xpath("dc:description", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_capitains_property("description", child.text, lg)

        for child in xml.xpath("dc:title", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                obj.set_capitains_property("title", child.text, lg)

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

    @classmethod
    def parse(cls, resource, parent=None):
        xml = xmlparser(resource)
        o = cls(urn=xml.xpath("cpt:identifier", namespaces=XPATH_NAMESPACES)[0].text, parent=parent)
        lang = xml.xpath("dc:language", namespaces=XPATH_NAMESPACES)[0].text
        if lang is not None:
            o.lang = lang
        o.path = xml.get('path')
        o.subtype = xml.xpath("dc:type", namespaces=XPATH_NAMESPACES)[0].text
        if parent is not None:
            o.parent = parent
        cls.parse_metadata(o, xml)
        return o

    def __init__(self, *args, **kwargs):
        super(XmlCapitainsReadableMetadata, self).__init__(*args, **kwargs)
        self._path = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value


class XmlCapitainsCollectionMetadata(capitains.CapitainsCollectionMetadata):
    """ Represents a CTS Textgroup in XML
    """
    CLASS_READABLE = XmlCapitainsReadableMetadata

    @classmethod
    def parse(cls, resource, parent=None, _with_children=False):
        """ Parse a resource

        :param resource: Element rerpresenting a work
        :param parent: Parent of the object
        :type parent: XmlCapitainsCollectionMetadata
        """
        xml = xmlparser(resource)
        # This is for a remote collection
        identifier = xml.get('identifier') or xml.get('urn')
        # This is for a local collection
        if identifier is None:
            identifier = xml.xpath("cpt:identifier", namespaces=XPATH_NAMESPACES)[0].text
        o = cls(urn=identifier)
        o.path = xml.get('path')
        o.subtype = [t.text for t in xml.xpath("dc:type", namespaces=XPATH_NAMESPACES)]
        if parent is not None:
            o.parent = parent

        for child in xml.xpath("dc:title", namespaces=XPATH_NAMESPACES):
            lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
            if lg is not None:
                o.set_label(child.text, lg)

        _parse_structured_metadata(o, xml)

        if _with_children:
            # Parse children
            children = []
            children.extend(_xpathDict(
                xml=xml, xpath='cpt:members/cpt:collection[@readable="true"]',
                cls=cls.CLASS_READABLE, parent=o
            ))
            children.extend(_xpathDict(
                xml=xml, xpath='cpt:members/cpt:collection[not(@readable="true")]',
                cls=cls, parent=o
            ))
            return o, children
        return o

    def __init__(self, *args, **kwargs):
        super(XmlCapitainsCollectionMetadata, self).__init__(*args, **kwargs)
        self._path = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        self._path = value
