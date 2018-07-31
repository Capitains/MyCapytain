from MyCapytain.resources.prototypes.metadata import Collection
from rdflib import URIRef


class DTSCollection(Collection):
    CLASS_SHORT = DTSCollectionShort

    @classmethod
    def parse(cls, resource, mimetype="application/json+ld"):
        """ Given a dict representation of a json object, generate a DTS Collection

        :param resource:
        :param mimetype:
        :return:
        """
        obj = cls(identifier=resource["@id"])
        obj.type = resource["type"]
        obj.version = resource["version"]
        for label in resource["label"]:
            obj.set_label(label["value"], label["lang"])
        for key, value in resource["metadata"].items():
            term = URIRef(key)
            if isinstance(value, list):
                if isinstance(value[0], dict):
                    for subvalue in value:
                        obj.metadata.add(term, subvalue["@value"], subvalue["@lang"])
                else:
                    for subvalue in value:
                        if subvalue.startswith("http") or subvalue.startswith("urn"):
                            obj.metadata.add(term, URIRef(subvalue))
                        else:
                            obj.metadata.add(term, subvalue)
            else:
                if value.startswith("http") or value.startswith("urn"):
                    obj.metadata.add(term, URIRef(value))
                else:
                    obj.metadata.add(term, value)

        for member in resource["members"]["contents"]:
            subobj = cls.CLASS_SHORT.parse(member)
            subobj.parent = member

        last = obj
        for member in resource["parents"]:
            subobj = cls.CLASS_SHORT.parse(member)
            last.parent = subobj

        return obj


class DTSCollectionShort(DTSCollection):
    @classmethod
    def parse(cls, resource):
        """ Given a dict representation of a json object, generate a DTS Collection

        :param resource:
        :param mimetype:
        :return:
        """
        obj = cls(identifier=resource["@id"])
        obj.type = resource["type"]
        obj.model = resource["model"]
        for label in resource["label"]:
            obj.set_label(label["value"], label["lang"])
        return obj
