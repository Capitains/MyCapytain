from rdflib import Namespace, Graph
from rdflib.namespace import SKOS


#: List of XPath Namespaces used in guidelines
XPATH_NAMESPACES = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "ti": "http://chs.harvard.edu/xmlns/cts",
    "cpt": "http://purl.org/capitains/ns/1.0#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "xml": "http://www.w3.org/XML/1998/namespace",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
}


class RDF_NAMESPACES:
    """ Namespaces Constants used to provide Namespace capacities across the library

    :cvar CTS: CTS Namespace
    :type CTS: Namespace
    :cvar TEI: TEI Namespace
    :type TEI: Namespace
    :cvar DC: DC Elements
    :type DC: Namespace
    :cvar CAPITAINS: CapiTainS Ontology
    :type CAPITAINS: Namespace
    """
    CTS = Namespace("http://chs.harvard.edu/xmlns/cts/")
    DTS = Namespace("http://w3id.org/dts-ontology/")
    TEI = Namespace("http://www.tei-c.org/ns/1.0/")
    CAPITAINS = Namespace("http://purl.org/capitains/ns/1.0#")


class Mimetypes:
    """ Mimetypes constants that are used to provide export functionality to base MyCapytain object.

    :cvar JSON: JSON Resource mimetype
    :cvar XML: XML Resource mimetype
    :cvar PYTHON: Python Native Object
    :cvar PLAINTEXT: Plain string format

    """

    class JSON:
        """ Json Mimetype

        :cvar Std: Standard JSON Export
        :cvar CTS: CTS Json Export
        """
        Std = "application/text"
        CTS = "application/ld+json:CTS"
        LD = "application/ld+json"

        class DTS:
            """ JSON DTS Expression

            :cvar Std: Standard DTS Json-LD Expression
            :cvar NoParents: DTS Json-LD Expression without parents expression
            """
            Std = "application/ld+json:DTS"
            NoParents = "application/ld+json:DTS/NoParents"

    class XML:
        """ XML Mimetype

        :cvar Std: Standard XML Export
        :cvar RDF: RDF XML Expression Export
        :cvar CTS: CTS API XML Expression Export
        :cvar TEI: TEI XML Expression Export
        """
        Std = "text/xml"
        RDF = "application/rdf+xml"
        RDFa = "application/rdfa+xml"
        CTS = "text/xml:CTS"
        TEI = "text/xml:tei"

        class CapiTainS:
            """ CapiTainS Guideline XML Structured metadata

            """
            CTS = "text/xml:CTS_CapiTainS"

    class PYTHON:
        """ Python Native Objects

        :cvar NestedDict: Nested Dictionary Object
        :cvar ETREE: Python LXML Etree Object
        """
        NestedDict = "python/NestedDict"
        ETREE = "python/lxml"

        class MyCapytain:
            """ MyCapytain Objects

            :cvar ReadableText: MyCapytain.resources.prototypes.text.CitableText
            """
            TextualElement = "Capitains/TextualElement"

    PLAINTEXT = "text/plain"


global __MYCAPYTAIN_TRIPLE_GRAPH__
__MYCAPYTAIN_TRIPLE_GRAPH__ = Graph()
__MYCAPYTAIN_TRIPLE_GRAPH__.bind("", RDF_NAMESPACES.CTS)
__MYCAPYTAIN_TRIPLE_GRAPH__.bind("dts", RDF_NAMESPACES.DTS)
__MYCAPYTAIN_TRIPLE_GRAPH__.bind("tei", RDF_NAMESPACES.TEI)
__MYCAPYTAIN_TRIPLE_GRAPH__.bind("skos", SKOS)
__MYCAPYTAIN_TRIPLE_GRAPH__.bind("cpt", RDF_NAMESPACES.CAPITAINS)


def set_graph(graph):
    global __MYCAPYTAIN_TRIPLE_GRAPH__
    __MYCAPYTAIN_TRIPLE_GRAPH__ = graph


def get_graph():
    return __MYCAPYTAIN_TRIPLE_GRAPH__

RDFLIB_MAPPING = {
    Mimetypes.XML.RDF: "xml",
    Mimetypes.JSON.LD: "json-ld",
    Mimetypes.JSON.DTS.Std: "json-ld"
}

