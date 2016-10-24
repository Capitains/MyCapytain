from MyCapytain.common.metadata import Metadata
from MyCapytain.common.utils import RDF_PREFIX, Mimetypes
from copy import deepcopy


class Collection(object):
    """ Collection represents any resource's metadata. It has members and parents
    """
    DC_TITLE_KEY = None

    @property
    def title(self):
        if hasattr(type(self), "DC_TITLE_KEY") and self.DC_TITLE_KEY:
            __title = Metadata(keys="dc:title")
            __title["dc:title"] = deepcopy(self.metadata[type(self).DC_TITLE_KEY])
            return __title

    def __init__(self):
        self.metadata = Metadata()
        self.__id__ = None
        self.properties = {
            RDF_PREFIX["dts"]+":model": "http://w3id.org/dts-ontology/collection"
        }
        self.parents = []

    @property
    def id(self):
        return self.__id__

    @id.setter
    def id(self, value):
        self.__id__ = value

    @property
    def members(self):
        return []

    def default_export(self, output=Mimetypes.JSON_DTS, domain=""):
        if output == Mimetypes.JSON_DTS:
            if self.title:
                m = self.metadata + self.title
            else:
                m = self.metadata
            o = {
                "@id": domain+self.id,
                RDF_PREFIX["dts"] + "description": m.export(Mimetypes.JSON_DTS),
                RDF_PREFIX["dts"] + "properties" : self.properties
            }
            if len(self.members):
                o[RDF_PREFIX["dts"] + "members"] = [
                    member.export(Mimetypes.JSON_DTS, domain) for member in self.members
                ]
            return o

    def export(self, output=None, domain=""):
        return self.default_export(output, domain)