from MyCapytain.resources.prototypes.metadata import Collection
from rdflib import URIRef
from pyld import jsonld
from MyCapytain.errors import JsonLdCollectionMissing
from MyCapytain.common.constants import RDF_NAMESPACES


_hyd = RDF_NAMESPACES.HYDRA
_dts = RDF_NAMESPACES.DTS
_empty_extensions = [{}]


class DTSCollection(Collection):
    @property
    def size(self):
        for value in self.metadata.get_single(RDF_NAMESPACES.HYDRA.totalItems):
            return int(value)
        return 0

    @staticmethod
    def parse(resource, mimetype="application/json+ld"):
        """ Given a dict representation of a json object, generate a DTS Collection

        :param resource:
        :param mimetype:
        :return:
        """
        collection = jsonld.expand(resource)
        if len(collection) == 0:
            raise JsonLdCollectionMissing("Missing collection in JSON")
        collection = collection[0]

        obj = DTSCollection(identifier=resource["@id"])

        # We retrieve first the descriptiooon and label that are dependant on Hydra
        for val_dict in collection[str(_hyd.title)]:
            obj.set_label(val_dict["@value"], None)

        for val_dict in collection["@type"]:
            obj.type = val_dict

        for val_dict in collection[str(_hyd.totalItems)]:
            obj.metadata.add(_hyd.totalItems, val_dict["@value"], 0)

        for val_dict in collection.get(str(_hyd.description), []):
            obj.metadata.add(_hyd.description, val_dict["@value"], None)

        for key, value_set in collection[str(_dts.dublincore)][0].items():
            term = URIRef(key)
            for value_dict in value_set:
                obj.metadata.add(term, value_dict["@value"], value_dict.get("@language", None))

        for key, value_set in collection.get(str(_dts.extensions), _empty_extensions)[0].items():
            term = URIRef(key)
            for value_dict in value_set:
                obj.metadata.add(term, value_dict["@value"], value_dict.get("@language", None))

        return obj


class DTSCollectionShort(DTSCollection):
    @staticmethod
    def parse(resource):
        """ Given a dict representation of a json object, generate a DTS Collection

        :param resource:
        :param mimetype:
        :return:
        """
        obj = DTSCollectionShort(identifier=resource["@id"])
        obj.type = resource["type"]
        obj.model = resource["model"]
        for label in resource["label"]:
            obj.set_label(label["value"], label["lang"])
        return obj