from ._base import CitationSet, BaseCitation
from ..metadata import Metadata
from MyCapytain.common.constants import RDF_NAMESPACES, Mimetypes


_dts = RDF_NAMESPACES.DTS


class DtsCitation(Metadata, BaseCitation):
    EXPORT_TO = [Mimetypes.JSON.DTS.Std]

    def __init__(self, name=None, children=None, root=None):
        super(DtsCitation, self).__init__(name=name, children=children, root=root)


    @staticmethod
    def ingest(resource, _citation_set=None, **kwargs):
        """ Ingest a dictionary of DTS Citation object (as parsed JSON-LD) and
        creates the Citation Graph

        :param resource: List of Citation objects from the
            DTS Collection Endpoint (as expanded JSON-LD)
        :type resource: dict
        :return:
        """
        return DtsCitation(
            name=resource.get(_tei.term("type"), None),
            root=_citation_set,
            match_pattern=resource.get(_tei.term("matchPattern"), None),
            replacement_pattern=resource.get(_tei.term("replacementPattern"), None),
        )


class DtsCitationRoot(CitationSet, Metadata):
    """ Set of citation that are supposed

    """
    EXPORT_TO = [Mimetypes.JSON.DTS.Std]
    CITATION_CLASS = DtsCitation

    def __init__(self):
        self._citation_graph = []

    def add_child(self, child):
        self._citation_graph.append(child)

    def match(self, passageId):
        raise NotImplementedError("This function is not available for DTS Citation")

    @classmethod
    def ingest(cls, resource, _root_class=None, _citation_class=None):
        """ Ingest a list of DTS Citation object (as parsed JSON-LD) and
        creates the Citation Graph

        :param resource: List of Citation objects from the
            DTS Collection Endpoint (as expanded JSON-LD)
        :type resource: list
        :param _root_class: (Dev only) Class to use for instantiating the Citation Set
        :type _root_class: class
        :param _citation_class: (Dev only) Class to use for instantiating the Citation
        :type _root_class: class
        :return: Citation Graph
        """
        _set = cls()
        for data in resource:
            _set.add_child(
                cls.ingest(data)
            )
        return _set
