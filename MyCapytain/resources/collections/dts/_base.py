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
        self._parents = set()

    @property
    def citation(self):
        return self._citation

    @citation.setter
    def citation(self, citation: CitationSet):
        self._citation = citation

    @property
    def size(self):
        value = self.metadata.get_single(RDF_NAMESPACES.HYDRA.totalItems)
        if value:
            return int(value)
        return 0

    @property
    def readable(self):
        if self.type == RDF_NAMESPACES.HYDRA.Resource:
            return True
        return False

    @property
    def parents(self):
        return self._parents

    @parents.setter
    def parents(self, value):
        self._parents = value

    @property
    def parent(self):
        raise NotImplementedError("In DTS, parent only exists in plural, via .parents")

    @parent.setter
    def parent(self, value):
        raise NotImplementedError("In DTS, parent only exists in plural, via .parents")

    @classmethod
    def parse(cls, resource, direction="children", **additional_parameters) -> "DtsCollection":
        """ Given a dict representation of a json object, generate a DTS Collection

        :param resource:
        :type resource: dict
        :param direction: Direction of the hydra:members value
        :return: DTSCollection parsed
        :rtype: DtsCollection
        """

        data = jsonld.expand(resource)
        if len(data) == 0:
            raise JsonLdCollectionMissing("Missing collection in JSON")
        data = data[0]

        obj = cls(
            identifier=resource["@id"],
            **additional_parameters
        )

        obj._parse_metadata(data)
        obj._parse_members(data, direction=direction, **additional_parameters)

        return obj

    def _parse_members(self, data, direction: str="children", **additional_parameters: dict):
        """

        :param data:
        :param direction:
        :param additional_parameters:
        :return:
        """
        members = self.parse_member(
            data, self, direction, **additional_parameters
        )
        if direction == "children":  # ToDo: Should be in a third function ?
            self.children.update({
                coll.id: coll
                for coll in members
            })
        else:
            self.parents.add(members)

    def _parse_metadata(self, data: dict):

        # We retrieve first the descriptiooon and label that are dependant on Hydra
        for val_dict in data[str(_hyd.title)]:
            self.set_label(val_dict["@value"], None)
        for val_dict in data["@type"]:
            self.type = val_dict

        # We retrieve the Citation System
        _cite_structure_term = str(_dts.term("citeStructure"))
        if _cite_structure_term in data and data[_cite_structure_term]:
            self.citation = self.CitationSet.ingest(data[_cite_structure_term])

        _cite_depth_term = str(_dts.term("citeDepth"))
        if _cite_depth_term in data and data[_cite_depth_term]:
            self.citation.depth = data[_cite_depth_term][0]["@value"]

        for val_dict in data[str(_hyd.totalItems)]:
            self.metadata.add(_hyd.totalItems, val_dict["@value"])

        for val_dict in data.get(str(_hyd.description), []):
            self.metadata.add(_hyd.description, val_dict["@value"], None)

        parse_metadata(self.metadata, data)

    def retrieve(self) -> bool:
        """ If needed, retrieves complete metadata

        :return: Status of retrieval
        """
        return True

    @classmethod
    def parse_member(
            cls,
            obj: dict,
            collection: "DtsCollection",
            direction: str,
            **additional_parameters) -> List["DtsCollection"]:
        """ Parse the member value of a Collection response
        and returns the list of object while setting the graph
        relationship based on `direction`

        :param obj: PyLD parsed JSON+LD
        :param collection: Collection attached to the member property
        :param direction: Direction of the member (children, parent)
        """
        members = []

        for member in obj.get(str(_hyd.member), []):
            subcollection = cls.parse(member, **additional_parameters)
            if direction == "children":
                subcollection.parents.update({collection})
            members.append(subcollection)

        return members
