from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.errors import JsonLdCollectionMissing
from MyCapytain.common.reference import DtsCitationSet
from MyCapytain.common.constants import RDF_NAMESPACES
from MyCapytain.common.utils import dict_to_literal

from rdflib import URIRef
from pyld import jsonld


_hyd = RDF_NAMESPACES.HYDRA
_dts = RDF_NAMESPACES.DTS
_cap = RDF_NAMESPACES.CAPITAINS
_tei = RDF_NAMESPACES.TEI
_empty_extensions = [{}]


class DTSCollection(Collection):

    CitationSet = DtsCitationSet

    def __init__(self, identifier="", *args, **kwargs):
        super(DTSCollection, self).__init__(identifier, *args, **kwargs)
        self._expanded = False  # Not sure I'll keep this
        self._citation = DtsCitationSet()

    @property
    def citation(self):
        return self._citation

    @citation.setter
    def citation(self, citation: CitationSet):
        self._citation = citation

    @property
    def size(self):
        for value in self.metadata.get_single(RDF_NAMESPACES.HYDRA.totalItems):
            return int(value)
        return 0

    @property
    def readable(self):
        if self.type == RDF_NAMESPACES.HYDRA.Resource:
            return True
        return False

    @classmethod
    def parse(cls, resource, direction="children"):
        """ Given a dict representation of a json object, generate a DTS Collection

        :param resource:
        :type resource: dict
        :param direction: Direction of the hydra:members value
        :return: DTSCollection parsed
        :rtype: DTSCollection
        """

        collection = jsonld.expand(resource)
        if len(collection) == 0:
            raise JsonLdCollectionMissing("Missing collection in JSON")
        collection = collection[0]

        obj = cls(identifier=resource["@id"])

        # We retrieve first the descriptiooon and label that are dependant on Hydra
        for val_dict in collection[str(_hyd.title)]:
            obj.set_label(val_dict["@value"], None)

        for val_dict in collection["@type"]:
            obj.type = val_dict

        # We retrieve the Citation System
        _cite_structure_term = str(_dts.term("citeStructure"))
        if _cite_structure_term in collection and collection[_cite_structure_term]:
            obj.citation = cls.CitationSet.ingest(collection[_cite_structure_term])

        for val_dict in collection[str(_hyd.totalItems)]:
            obj.metadata.add(_hyd.totalItems, val_dict["@value"], 0)

        for val_dict in collection.get(str(_hyd.description), []):
            obj.metadata.add(_hyd.description, val_dict["@value"], None)

        for key, value_set in collection.get(str(_dts.dublincore), _empty_extensions)[0].items():
            term = URIRef(key)
            for value_dict in value_set:
                obj.metadata.add(term, *dict_to_literal(value_dict))

        for key, value_set in collection.get(str(_dts.extensions), _empty_extensions)[0].items():
            term = URIRef(key)
            for value_dict in value_set:
                print(value_dict)
                obj.metadata.add(term, *dict_to_literal(value_dict))

        for member in collection.get(str(_hyd.member), []):
            subcollection = cls.parse(member)
            if direction == "children":
                subcollection.parent = obj

        return obj
