from MyCapytain.common.metadata import Metadata
from MyCapytain.common.utils import RDF_PREFIX, Mimetypes
from copy import deepcopy


class Node(object):
    """ Graph Object represent identifiers relationships in Tree object. Each property of the gram

    :param identifier: Current object identifier
    :type identifier: str
    :param children: Children of the current node
    :type children: [Node or str]
    :param parent: Parent of the current node
    :type parent: Node or str
    :param siblings: Previous and next node of the current node
    :type siblings: Node or str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    """
    def __init__(self, identifier=None, children=None, parent=None, siblings=(None, None), depth=1):
        self.__children__ = children or []
        self.__parent__ = parent
        self.__prev__, self.__next__ = siblings
        self.__identifier__ = identifier
        self.__depth__ = depth

    @property
    def depth(self):
        """ Depth of the node in the global hierarchy of the text tree

        :rtype: [Node]
        """
        return self.__depth__

    @property
    def children(self):
        """ Siblings Node

        :rtype: [Node]
        """
        return self.__children__

    @property
    def parent(self):
        """ Parent Node

        :rtype: (Node, Node)
        """
        return self.__parent__

    @property
    def siblings(self):
        """ Siblings Node

        :rtype: (Node, Node)
        """
        return self.__prev__, self.__next__

    @property
    def prev(self):
        """ Previous Node (Sibling)

        :rtype: Node
        """
        return self.__prev__

    @property
    def next(self):
        """ Next Node (Sibling)

        :rtype: Node
        """
        return self.__next__

    @property
    def id(self):
        """Current object identifier

        :rtype: Node
        """
        return self.__identifier__


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
            RDF_PREFIX["dts"]+":model": "http://w3id.org/dts-ontology/collection"
        }
        self.parents = []

    @property
    def id(self):
        """ Identifier of the collection item

        :rtype: str
        """
        return self.__id__

    @id.setter
    def id(self, value):
        self.__id__ = value

    @property
    def members(self):
        """ Children of the collection's item

        :rtype: [Collection]
        """
        return []

    def default_export(self, output=Mimetypes.JSON_DTS, domain=""):
        """ Export the collection item in the Mimetype required

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :param domain: Domain (Necessary sometime to express some IDs)
        :type domain: str
        :return: Object using a different representation
        """
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
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :param domain: Domain (Necessary sometime to express some IDs)
        :type domain: str
        :return: Object using a different representation
        """
        return self.default_export(output, domain)
