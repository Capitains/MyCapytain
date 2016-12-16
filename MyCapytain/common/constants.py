from collections import namedtuple
from inspect import getmro

#: List of XPath Namespaces used in guidelines
NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "ahab": "http://localhost.local",
    "ti": "http://chs.harvard.edu/xmlns/cts",
    "xml": "http://www.w3.org/XML/1998/namespace"
}

#: List of RDF Prefixes with their equivalents
RDF_PREFIX = {
  "foaf": "http://xmlns.com/foaf/0.1/",
  "dc": "http://purl.org/dc/elements/1.1/",
  "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
  "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
  "owl": "http://www.w3.org/2002/07/owl#",
  "geonames": "http://www.geonames.org/ontology#",
  "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
  "skos": "http://www.w3.org/2004/02/skos/core#",
  "dbp": "http://dbpedia.org/property/",
  "swrc": "http://swrc.ontoware.org/ontology#",
  "sioc": "http://rdfs.org/sioc/ns#",
  "xsd": "http://www.w3.org/2001/XMLSchema#",
  "dbo": "http://dbpedia.org/ontology/",
  "dc11": "http://purl.org/dc/elements/1.1/",
  "doap": "http://usefulinc.com/ns/doap#",
  "dts": "http://w3id.org/dts-ontology/",
  "dbpprop": "http://dbpedia.org/property/",
  "content": "http://purl.org/rss/1.0/modules/content/",
  "wot": "http://xmlns.com/wot/0.1/",
  "rss": "http://purl.org/rss/1.0/",
  "gen": "http://purl.org/gen/0.1#",
  "dbpedia": "http://dbpedia.org/resource/",

  "tei": "http://www.tei-c.org/ns/1.0/",
  "ti": "http://chs.harvard.edu/xmlns/cts/"
}

#: List of RDF URI with their equivalent Prefix
RDF_MAPPING = {
    'http://chs.harvard.edu/xmlns/cts/': 'ti',
    'http://dbpedia.org/ontology/': 'dbo',
    'http://dbpedia.org/property/': 'dbp',
    'http://dbpedia.org/resource/': 'dbpedia',
    'http://purl.org/dc/elements/1.1/': 'dc11',
    'http://purl.org/gen/0.1#': 'gen',
    'http://purl.org/rss/1.0/': 'rss',
    'http://purl.org/rss/1.0/modules/content/': 'content',
    'http://rdfs.org/sioc/ns#': 'sioc',
    'http://swrc.ontoware.org/ontology#': 'swrc',
    'http://usefulinc.com/ns/doap#': 'doap',
    'http://www.geonames.org/ontology#': 'geonames',
    'http://www.tei-c.org/ns/1.0/': 'tei',
    'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
    'http://www.w3.org/2000/01/rdf-schema#': 'rdfs',
    'http://www.w3.org/2001/XMLSchema#': 'xsd',
    'http://www.w3.org/2002/07/owl#': 'owl',
    'http://www.w3.org/2003/01/geo/wgs84_pos#': 'geo',
    'http://www.w3.org/2004/02/skos/core#': 'skos',
    'http://xmlns.com/foaf/0.1/': 'foaf',
    'http://xmlns.com/wot/0.1/': 'wot'
}

#: Namespace tuple that can be used to express namespace information
Namespace = namedtuple("Namespace", ["uri", "prefix"])


class NAMESPACES:
    """ Namespaces Constants used to provide Namespace capacities across the library

    :cvar CTS: CTS Namespace
    :type CTS: Namespace
    :cvar TEI: TEI Namespace
    :type TEI: Namespace
    :cvar DC: DC Elements
    :type DC: Namespace
    """
    CTS = Namespace("http://chs.harvard.edu/xmlns/cts/", "ti")
    TEI = Namespace("http://www.tei-c.org/ns/1.0/", "tei")
    DC = Namespace("http://purl.org/dc/elements/1.1/", "dc")


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
        """
        Std = "text/xml"
        RDF = "application/rdf+xml"
        CTS = "text/xml:CTS"

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
            ReadableText = "Capitains/ReadableText"

    PLAINTEXT = "text/plain"


class Exportable(object):
    """ Objects that supports Export

    :cvar EXPORT_TO: List of Mimetypes the resource can export to
    """
    EXPORT_TO = []
    DEFAULT_EXPORT = None

    @property
    def export_capacities(self):
        """  List Mimetypes that current object can export to
        """
        return [export for cls in getmro(type(self)) if hasattr(cls, "EXPORT_TO") for export in cls.EXPORT_TO]

    def __export__(self, output=None, **kwargs):
        """ Export the collection item in the Mimetype required.

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """
        return None

    def export(self, output=None, **kwargs):
        """ Export the collection item in the Mimetype required.

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """
        if output is None:
            output = self.DEFAULT_EXPORT
        if output is not None and output in self.export_capacities:
            for cls in getmro(type(self)):
                if hasattr(cls, "EXPORT_TO") and output in cls.EXPORT_TO:
                    return cls.__export__(self, output, **kwargs)
        raise NotImplementedError(
            "Mimetype {} has not been implemented for this resource".format(output or "(No Mimetype)")
        )
