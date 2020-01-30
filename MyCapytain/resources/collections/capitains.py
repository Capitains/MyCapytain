from MyCapytain.resources.collections.cts import _parse_structured_metadata, XmlCtsCitation
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.common.constants import XPATH_NAMESPACES, Mimetypes, RDF_NAMESPACES
from MyCapytain.resources.prototypes.capitains import collection as capitains
from rdflib.namespace import DC
from typing import Union, List, Tuple

XPATH_NAMESPACES.update({'dc': "http://purl.org/dc/elements/1.1/", 'dct': 'http://purl.org/dc/terms/'})


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


class XmlCapitainsReadableMetadata(capitains.CapitainsReadableMetadata):
    """ Represents a general Capitains CtsTextMetadata

    """
    DEFAULT_EXPORT = Mimetypes.PYTHON.ETREE
    # We may want to update this at some point to XmlCapitainsCitation.
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
        :type obj: XmlCapitainsTextMetadata
        :param xml: An xml representation object
        :type xml: lxml.etree._Element
        """

        for child in xml.getchildren():
            if child.tag.startswith('{' + XPATH_NAMESPACES['dc']):
                lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
                obj.metadata.add(DC.term(child.tag.replace('{' + XPATH_NAMESPACES['dc'] + '}', '')),
                                 child.text, lg)

        obj.citation = cls.CLASS_CITATION.ingest(xml, obj.citation, "cpt:structured-metadata/ti:online/ti:citationMapping/ti:citation")

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
    def parse(cls, resource, parent=None, resolver=None):
        xml = xmlparser(resource)
        o = cls(urn=xml.xpath("cpt:identifier", namespaces=XPATH_NAMESPACES)[0].text, parent=parent, resolver=resolver)
        resolver = o._resolver
        o.metadata.set(RDF_NAMESPACES.CAPITAINS.identifier, o.id)
        for lang in xml.xpath("dc:language", namespaces=XPATH_NAMESPACES):
            o.lang = lang.text
        o.path = xml.get('path')
        for t in xml.xpath("dc:type", namespaces=XPATH_NAMESPACES):
            o.subtype = t.text
        resolver.add_collection(o.id, o)
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
    def parse(cls, resource, parent: 'XmlCapitainsCollectionMetadata'=None,
              _with_children: bool=False, recursive: bool=False,
              resolver=None) -> Union['XmlCapitainsCollectionMetadata',
                                      Tuple['XmlCapitainsCollectionMetadata',
                                            List[Union['XmlCapitainsCollectionMetadata',
                                                       'XmlCapitainsReadableMetadata']]]]:
        """ Parse a resource

        :param resource: Element rerpresenting a collection
        :param parent: Parent of the object
        :type parent: XmlCapitainsCollectionMetadata
        :param _with_children: Whether to parse the children of the current collection
        :type _with_children: bool
        :param recursive: Whether to recurse all the way through the tree of the metadata file.
            Note: recursive only recurses through the XML chunk currently being processed and does not seek other files.
        :type recursive: bool
        """
        xml = xmlparser(resource)
        # This is for a remote collection
        identifier = xml.get('identifier') or xml.get('urn')
        # This is for a local collection
        if identifier is None:
            identifier = xml.xpath("cpt:identifier", namespaces=XPATH_NAMESPACES)[0].text
        o = cls(urn=identifier, resolver=resolver)
        resolver = o._resolver
        o.path = xml.get('path')
        for t in xml.xpath("dc:type", namespaces=XPATH_NAMESPACES):
            o.subtype = t.text
        if o.id in resolver.id_to_coll:
            resolver.id_to_coll[o.id].update(o)
        else:
            resolver.add_collection(o.id, o)
        if parent is not None:
            o.parent = parent

        o.metadata.set(RDF_NAMESPACES.CAPITAINS.identifier, o.id)
        for child in xml.getchildren():
            if child.tag.startswith('{' + XPATH_NAMESPACES['dc']):
                lg = child.get("{http://www.w3.org/XML/1998/namespace}lang")
                o.metadata.add(DC.term(child.tag.replace('{' + XPATH_NAMESPACES['dc'] + '}', '')),
                               child.text, lg)

        _parse_structured_metadata(o, xml)

        if _with_children:
            # Parse children
            children = []
            children.extend(_xpathDict(
                xml=xml, xpath='cpt:members/cpt:collection[@readable="true"]',
                cls=cls.CLASS_READABLE, parent=o, resolver=resolver
            ))
            children.extend(_xpathDict(
                xml=xml, xpath='cpt:members/cpt:collection[not(@readable="true")]',
                cls=cls, parent=o, _with_children=recursive, recursive=recursive, resolver=resolver
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
