from copy import deepcopy

from MyCapytain.common.metadata import Metadata
from MyCapytain.common.utils import RDF_PREFIX, Mimetypes


class Collection(object):
    """ Collection represents any resource's metadata. It has members and parents

    :ivar properties: Properties of the collection
    :type properties: dict
    :ivar parents: Parent of the node from the direct parent to the highest ascendant
    :type parents: [Collection]
    :ivar metadata: Metadata
    :type metadata: Metadata
    :cvar DC_TITLE_KEY: Key representing the object title in the Metadata property
    :type DC_TITLE_KEY: str
    """
    DC_TITLE_KEY = None
    TYPE_URI = "http://w3id.org/dts-ontology/collection"

    @property
    def title(self):
        """ Title of the collection Item

        :rtype: Metadata
        """
        if hasattr(type(self), "DC_TITLE_KEY") and self.DC_TITLE_KEY:
            __title = Metadata(keys="dc:title")
            __title["dc:title"] = deepcopy(self.metadata[type(self).DC_TITLE_KEY])
            return __title

    def __init__(self):
        self.metadata = Metadata()
        self.__id__ = None
        self.properties = {
            RDF_PREFIX["dts"]+"model": "http://w3id.org/dts-ontology/collection",
            RDF_PREFIX["rdf"]+"type": self.TYPE_URI
        }
        self.parents = []

    @property
    def id(self):
        """ Identifier of the collection item

        :rtype: str
        """
        return self.__id__

    @property
    def readable(self):
        """ Readable property should return elements where the element can be queried for getPassage / getReffs
        """
        return False

    @id.setter
    def id(self, value):
        self.__id__ = value

    @property
    def members(self):
        """ Children of the collection's item

        :rtype: [Collection]
        """
        return []

    @property
    def descendants(self):
        """ Any descendant (no max level) of the collection's item

        :rtype: [Collection]
        """
        return self.members + \
            [submember for member in self.members for submember in member.descendants]

    @property
    def readableDescendants(self):
        """ List of element available which are readable

        :rtype: [Collection]
        """
        return [member for member in self.descendants if member.readable]

    def default_export(self, output=Mimetypes.JSON.DTS.Std, domain=""):
        """ Export the collection item in the Mimetype required

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :param domain: Domain (Necessary sometime to express some IDs)
        :type domain: str
        :return: Object using a different representation
        """
        raise NotImplementedError

    def export(self, output=None, domain=""):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :param domain: Domain (Necessary sometime to express some IDs)
        :type domain: str
        :return: Object using a different representation
        """
        if output == Mimetypes.JSON.DTS.Std or output == Mimetypes.JSON.DTS.NoParents:
            identifier = self.id
            if self.id is None:
                identifier = ""
            if self.title:
                m = self.metadata + self.title
            else:
                m = self.metadata
            o = {
                "@id": domain+identifier,
                RDF_PREFIX["dts"] + "description": m.export(Mimetypes.JSON.DTS.Std),
                RDF_PREFIX["dts"] + "properties": self.properties,
                RDF_PREFIX["dts"] + "capabilities": {
                    RDF_PREFIX["dts"] + "ordered": False,
                    RDF_PREFIX["dts"] + "supportsRole": False,
                    RDF_PREFIX["dts"] + "static": True,
                    RDF_PREFIX["dts"] + "navigation": {
                        RDF_PREFIX["dts"] + "parents": [],
                        RDF_PREFIX["dts"] + "siblings": {}
                    }
                },
            }
            if len(self.members):
                o[RDF_PREFIX["dts"] + "members"] = [
                    member.export(Mimetypes.JSON.DTS.NoParents, domain) for member in self.members
                ]
            if output != Mimetypes.JSON.DTS.NoParents and len(self.parents):
                o[RDF_PREFIX["dts"] + "capabilities"]\
                 [RDF_PREFIX["dts"] + "navigation"]\
                 [RDF_PREFIX["dts"] + "parents"] = [
                    {
                        "@id": domain+(parent.id or ""),
                        RDF_PREFIX["rdf"] + "type": parent.TYPE_URI,
                        RDF_PREFIX["dts"] + "model": "http://w3id.org/dts-ontology/collection",
                    }
                    for parent in self.parents
                ]
            return o
