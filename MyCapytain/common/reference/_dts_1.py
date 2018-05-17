from ._base import CitationSet, BaseCitation
import re
from MyCapytain.common.constants import RDF_NAMESPACES


_tei = RDF_NAMESPACES.TEI


class DtsCitationRoot(CitationSet):
    """ Set of citation that are supposed

    """
    def __init__(self):
        self._citation_graph = []

    def add_child(self, child):
        self._citation_graph.append(child)

    def match(self, passageId):
        """ Match a passagedId against the citation graph

        :param passageId: PassageID
        :return:
        :rtype: Dts_Citation
        """
        for citation in self._citation_graph:
            if re.match(citation.pattern, passageId):
                return citation

    @staticmethod
    def ingest(resource, _root_class=None, _citation_class=None):
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
        _set = DtsCitationRoot()
        for data in resource:
            _set.add_child(
                DtsCitation.ingest(data)
            )
        return _set


class DtsCitation(BaseCitation):
    def __init__(self, name=None, children=None, root=None, match_pattern=None, replacement_pattern=None):
        super(DtsCitation, self).__init__(name=name, children=children, root=root)
        self._match_pattern = None
        self._replacement_pattern = None

        self.match_pattern = match_pattern
        self.replacement_pattern = replacement_pattern

    @property
    def match_pattern(self):
        return self._match_pattern

    @match_pattern.setter
    def match_pattern(self, value):
        self._match_pattern = value

    @property
    def replacement_pattern(self):
        return self._replacement_pattern

    @replacement_pattern.setter
    def replacement_pattern(self, value):
        self._replacement_pattern = value

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
