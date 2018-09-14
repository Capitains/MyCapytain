from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.errors import JsonLdCollectionMissing
from MyCapytain.common.reference import DtsCitationSet
from MyCapytain.common.constants import RDF_NAMESPACES
from MyCapytain.common.utils.dts import parse_metadata


from typing import List
from pyld import jsonld


__all__ = [
    "DtsCollection"
]


_hyd = RDF_NAMESPACES.HYDRA
_dts = RDF_NAMESPACES.DTS
_cap = RDF_NAMESPACES.CAPITAINS
_tei = RDF_NAMESPACES.TEI
_empty_extensions = [{}]


class DtsCollection(Collection):

    CitationSet = DtsCitationSet

    def __init__(self, identifier="", *args, **kwargs):
        super(DtsCollection, self).__init__(identifier, *args, **kwargs)
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
        :rtype: DtsCollection
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

        _cite_depth_term = str(_dts.term("citeDepth"))
        if _cite_depth_term in collection and collection[_cite_depth_term]:
            obj.citation.depth = collection[_cite_depth_term][0]["@value"]

        for val_dict in collection[str(_hyd.totalItems)]:
            obj.metadata.add(_hyd.totalItems, val_dict["@value"], 0)

        for val_dict in collection.get(str(_hyd.description), []):
            obj.metadata.add(_hyd.description, val_dict["@value"], None)

        parse_metadata(obj.metadata, collection)
        members = cls.parse_member(
            collection, obj, direction
        )
        if direction == "children":
            obj.children.update({
                coll.id: coll
                for coll in members
            })
        else:
            obj.parents.extend(members)

        return obj

    @classmethod
    def parse_member(
            cls,
            obj: dict,
            collection: "DtsCollection",
            direction) -> List["DtsCollection"]:
        """ Parse the member value of a Collection response
        and returns the list of object while setting the graph
        relationship based on `direction`

        :param obj: PyLD parsed JSON+LD
        :param collection: Collection attached to the member property
        :param direction: Direction of the member (children, parent)
        """
        members = []

        for member in obj.get(str(_hyd.member), []):
            subcollection = cls.parse(member)
            if direction == "children":
                subcollection.parent = collection
            members.append(subcollection)

        return members
