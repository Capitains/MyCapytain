from ._base import BaseCitationSet, BaseCitation, BaseReference, BaseReferenceSet
from ..metadata import Metadata
from MyCapytain.common.constants import RDF_NAMESPACES


_dts = RDF_NAMESPACES.DTS
_cite_type_term = str(_dts.term("citeType"))
_cite_structure_term = str(_dts.term("citeStructure"))


class DtsReference(BaseReference):
    def __new__(cls, *refs, metadata: Metadata=None):
        o = super(DtsReference).__new__(*refs)
        if metadata:
            o._metadata = metadata
        else:
            o._metadata = Metadata()  # toDo : Figure how to deal with Refs ID in the Sparql Graph


class DtsReferenceSet(BaseReferenceSet):
    def __contains__(self, item: str) -> bool:
        return BaseReferenceSet.__contains__(self, item) or \
               BaseReferenceSet.__contains__(self, DtsReference(item))


class DtsCitation(BaseCitation):
    def __init__(self, name=None, children=None, root=None):
        super(DtsCitation, self).__init__(name=name, children=children, root=root)

    @classmethod
    def ingest(cls, resource, root=None, **kwargs):
        """ Ingest a dictionary of DTS Citation object (as parsed JSON-LD) and
        creates the Citation Graph

        :param resource: List of Citation objects from the
            DTS Collection Endpoint (as expanded JSON-LD)
        :type resource: dict
        :param root: Root of the citation tree
        :type root: BaseCitationSet
        :return:
        """
        cite = cls(
            name=resource.get(_cite_type_term, [{"@value": None}])[0]["@value"],  # Not really clean ?
            root=root
        )
        for subCite in resource.get(_cite_structure_term, []):
            cite.add_child(cls.ingest(subCite, root=root))
        return cite

    def match(self, passageId):
        raise NotImplementedError("Passage Match is not part of the DTS Standard Citation")


class DtsCitationSet(BaseCitationSet):
    """ Set of citation that are supposed

    """

    def __init__(self, children=None):
        super(DtsCitationSet, self).__init__(children=children)
        self._depth = None

    @property
    def depth(self) -> int:
        if self._depth:
            return self._depth
        return super(DtsCitationSet, self).depth

    @depth.setter
    def depth(self, value: int):
        self._depth = value

    def __repr__(self):
        return "<MyCapytain.common.reference.DtsCitationSet object at %s>" % id(self)

    CitationClass = DtsCitation

    def match(self, passageId):
        raise NotImplementedError("Passage Match is not part of the DTS Standard Citation")

    @classmethod
    def ingest(cls, resource):
        """ Ingest a list of DTS Citation object (as parsed JSON-LD) and
        creates the Citation Graph

        :param resource: List of Citation objects from the
            DTS Collection Endpoint (as expanded JSON-LD)
        :type resource: list
        :return: Citation Graph
        """
        _set = cls()
        for data in resource:
            _set.add_child(
                cls.CitationClass.ingest(data, root=_set)
            )
        return _set
