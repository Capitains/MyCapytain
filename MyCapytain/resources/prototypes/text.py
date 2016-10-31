# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.proto.text
   :synopsis: Prototypes for Text

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from past.builtins import basestring
from MyCapytain.common.reference import URN, Reference, Citation, Node
from MyCapytain.common.metadata import Metadata
from MyCapytain.common.utils import Mimetypes
from MyCapytain.resources.prototypes.metadata import Collection


class TextualNode(object):
    """ Node representing a text passage.

    :param textId: Identifier of the text
    :type textId: str
    :param graph: Graph giving the information about the node position in a text tree
    :type graph: Node
    :param citation: Citation system of the text
    :type citation: Citation

    :cvar default_exclude: Default exclude for exports
    """

    default_exclude = []

    def __init__(self, textId=None, graph=None, citation=None):
        self.__id__ = textId
        self.__graph__ = graph or Node()
        self.__citation__ = citation or Citation()
        self.__text__ = ""
        self.__metadata__ = None

    @property
    def citation(self):
        """

        :rtype: Citation
        """
        return self.__citation__

    @citation.setter
    def citation(self, value):
        if not isinstance(value, Citation):
            raise TypeError("Citation property can only be a Citation object")
        self.__citation__ = value

    def text(self):
        return self.export(output=Mimetypes.PLAINTEXT, exclude=self.default_exclude)

    @property
    def id(self):
        return self.__id__

    @id.setter
    def id(self, value):
        self.__id__ = value

    @property
    def graph(self):
        return self.__graph__

    @graph.setter
    def graph(self, value):
        if not isinstance(value, Node):
            raise TypeError("Graph property can only be a Node object")
        self.__graph__ = value

    def default_export(self, output=Mimetypes.JSON_DTS, exclude=None):
        """ Export the textual node item in the Mimetype required

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :param exclude: Informations to exclude. Specific to implementations
        :type exclude: [str]
        :return: Object using a different representation
        """
        raise NotImplementedError

    def export(self, output=None, exclude=None):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :param exclude: Informations to exclude. Specific to implementations
        :type exclude: [str]
        :return: Object using a different representation
        """
        if exclude is None:
            exclude = self.default_exclude
        return self.default_export(output, exclude)

    @property
    def metadata(self):
        """ Metadata information about the text

        :return: Collection object with metadata about the text
        """
        return self.__metadata__

    @metadata.setter
    def metadata(self, value):
        """ Set the metadata collection attribute

        :param value: Collection of metadata
        :type value: Collection
        """
        if isinstance(value, Collection):
            self.__metadata__ = value
        else:
            raise TypeError("Metadata should be collection based")

    def getPassage(self, reference):
        """ Retrieve a passage and store it in the object

        :param reference: Reference of the passage to retrieve
        :type reference: str or Node or Reference
        :rtype: TextualNode
        :returns: Object representing the passage

        :raises: *TypeError* when reference is not a list or a Reference
        """

        raise NotImplementedError()


class CTSNode(TextualNode):
    """ Initiate a Resource object
    
    :param urn: A URN identifier
    :type urn: URN
    :param graph: Graph giving the information about the node position in a text tree
    :type graph: Node
    :param citation: Citation system of the text
    :type citation: Citation

    :cvar default_exclude: Default exclude for exports
    """

    def __init__(self, urn=None, graph=None, citation=None):
        super(CTSNode, self).__init__(textId=str(urn), citation=citation, graph=graph)
        self.__urn__ = None

        if urn is not None:
            self.urn = urn

    @property
    def urn(self):
        """ URN Identifier of the object

        :rtype: URN
        """
        return self.__urn__
    
    @urn.setter
    def urn(self, value):
        """ Set the urn

        :param value: URN to be saved
        :type value:  URN
        :raises: *TypeError* when the value is not URN compatible

        """
        if isinstance(value, basestring):
            value = URN(value)
        elif not isinstance(value, URN):
            raise TypeError()
        self.__urn__ = value


class Passage(CTSNode):
    """ Passage representing object prototype
    
    :param urn: A URN identifier
    :type urn: URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param parent: Parent of the current passage
    :type parent: Passage
    :param citation: Citation for children level
    :type citation: MyCapytain.resources.texts.tei.Citation
    :param id: Identifier of the subreference without URN informations
    :type id: List
    
    """

    def __init__(self, parent=None, **kwargs):
        super(Passage, self).__init__(**kwargs)
        self.parent = None
        if parent is not None and isinstance(parent, Passage):
            self.parent = parent
        elif isinstance(parent, Text):
            self.parent = parent

    @property
    def prev(self):
        """ Previous passage 

        :rtype: Passage
        :returns: Previous passage at same level
        """
        return self.graph.prev

    @property
    def next(self):
        """ Following passage 

        :rtype: Passage
        :returns: Following passage at same level
        """
        return self.graph.next

    @property
    def first(self):
        """ First child of current Passage 
        
        :rtype: Node
        :returns: First passage node Information
        """
        if len(self.graph.children):
            return self.graph.children[0]
        else:
            raise NotImplementedError

    @property
    def last(self):
        """ Last child of current Passage 
        
        :rtype: Node
        :returns: Last passage Node representation
        """
        if len(self.graph.children):
            return self.graph.children[-1]
        else:
            raise NotImplementedError

    @property
    def children(self):
        """ Children of the passage

        :rtype: [Node]
        :returns: List of childrens according to .graph
        """
        return self.graph.children

    def getValidReff(self, level=1, reference=None):
        """ Given a resource, Text will compute valid reffs

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param passage: Subreference (optional)
        :type passage: Reference
        :rtype: List.basestring
        :returns: List of levels
        """
        raise NotImplementedError()

    def getLabel(self):
        """ Retrieve metadata about the text

        :rtype: Collection
        :returns: Retrieve Label informations in a Collection format
        """
        raise NotImplementedError()


class Text(Passage):
    """ A CTS Text """
    def __init__(self, citation=None, metadata=None, **kwargs):
        super(Text, self).__init__(**kwargs)

        self._cRefPattern = Citation()
        if citation is not None:
            self.citation = citation

        if metadata is not None:
            self.__metadata__ = metadata
        else:
            self.__metadata__ = Metadata()

        self.__reffs__ = None

    @property
    def reffs(self):
        """ Get all valid reffs for every part of the Text

        :rtype: MyCapytain.resources.texts.tei.Citation
        """
        if not self.__reffs__:
            self.__reffs__ = [reff for reffs in [self.getValidReff(level=i) for i in range(1, len(self.citation) + 1)] for reff in reffs]
        return self.__reffs__