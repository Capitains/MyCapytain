# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.proto.text
   :synopsis: Prototypes for CitableText

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from six import text_type
from MyCapytain.common.reference import URN, Citation, NodeId
from MyCapytain.common.metadata import Metadata
from MyCapytain.common.constants import Mimetypes, Exportable
from MyCapytain.resources.prototypes.metadata import Collection


class TextualElement(Exportable):
    """ Node representing a text passage.

    :param identifier: Identifier of the text
    :type identifier: str
    :param metadata: Collection Information about the Item
    :type metadata: Collection

    :cvar default_exclude: Default exclude for exports
    """

    default_exclude = []

    def __init__(self, identifier=None, metadata=None):
        self.__about__ = Collection()
        self.__identifier__ = identifier
        if metadata:
            self.metadata = metadata

    @property
    def text(self):
        """ String representation of the text

        :return: String representation of the text
        :rtype: text_type
        """
        return self.export(output=Mimetypes.PLAINTEXT, exclude=self.default_exclude)

    @property
    def id(self):
        """ Identifier of the text

        :return: Identifier of the text
        :rtype: text_type
        """
        return self.__identifier__

    @property
    def about(self):
        """ Metadata information about the text

        :return: Collection object with metadata about the text
        :rtype Collection:
        """
        return self.__about__

    @about.setter
    def about(self, value):
        """ Set the metadata collection attribute

        :param value: Collection of metadata
        :type value: Collection
        """
        if isinstance(value, Collection):
            self.__about__ = value
        else:
            raise TypeError(".about should be an instance of Collection")

    @property
    def metadata(self):
        """ Metadata information about the text

        :return: Collection object with metadata about the text
        :rtype: Metadata
        """
        return self.about.metadata

    @metadata.setter
    def metadata(self, value):
        """ Set the metadata collection attribute

        :param value: Collection of metadata
        :type value: Collection
        """
        if isinstance(value, Metadata):
            self.about.metadata = value
        else:
            raise TypeError(".metadata should be an instance of Metadata")

    def export(self, output=None, exclude=None, **kwargs):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses MyCapytain.common.constants.Mimetypes)
        :type output: str
        :param exclude: Information to exclude. Specific to implementations
        :type exclude: [str]
        :return: Object using a different representation
        """
        return Exportable.export(self, output, exclude=exclude, **kwargs)


class TextualNode(TextualElement, NodeId):
    """ Node representing a text passage.

    :param identifier: Identifier of the text
    :type identifier: str
    :param metadata: Collection Information about the Item
    :type metadata: Collection
    :param citation: Citation system of the text
    :type citation: Citation
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int

    :cvar default_exclude: Default exclude for exports
    """

    def __init__(self, identifier=None, citation=None, **kwargs):
        super(TextualNode, self).__init__(identifier=identifier, **kwargs)
        self.__citation__ = citation or Citation()

    @property
    def citation(self):
        """ Citation Object of the Text

        :return: Citation Object of the Text
        :rtype: Citation
        """
        return self.__citation__

    @citation.setter
    def citation(self, value):
        if not isinstance(value, Citation):
            raise TypeError("Citation property can only be a Citation object")
        self.__citation__ = value


class TextualGraph(TextualNode):
    """ Node representing a text passage.

    :param identifier: Identifier of the text
    :type identifier: str
    :param metadata: Collection Information about the Item
    :type metadata: Collection
    :param citation: Citation system of the text
    :type citation: Citation
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    :param resource: Resource used to navigate through the textual graph

    :cvar default_exclude: Default exclude for exports
    """
    def __init__(self, identifier=None, **kwargs):
        super(TextualGraph, self).__init__(identifier=identifier, **kwargs)

    def getTextualNode(self, subreference):
        """ Retrieve a passage and store it in the object

        :param subreference: Reference of the passage to retrieve
        :type subreference: str or Node or Reference
        :rtype: TextualNode
        :returns: Object representing the passage

        :raises: *TypeError* when reference is not a list or a Reference
        """

        raise NotImplementedError()

    def getReffs(self, level=1, subreference=None):
        """ Reference available at a given level

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param passage: Subreference (optional)
        :type passage: Reference
        :rtype: [text_type]
        :returns: List of levels
        """
        raise NotImplementedError()


class InteractiveTextualNode(TextualGraph):
    """ Node representing a text passage.

    :param identifier: Identifier of the text
    :type identifier: str
    :param metadata: Collection Information about the Item
    :type metadata: Collection
    :param citation: Citation system of the text
    :type citation: Citation
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    :param resource: Resource used to navigate through the textual graph

    :cvar default_exclude: Default exclude for exports
    """
    def __init__(self, identifier=None, **kwargs):
        super(InteractiveTextualNode, self).__init__(identifier=identifier, **kwargs)
        self.__childIds__ = None

    @property
    def prev(self):
        """ Get Previous Passage

        :rtype: Passage
        """
        if self.prevId is not None:
            return self.getTextualNode(self.prevId)

    @property
    def next(self):
        """ Get Next Passage

        :rtype: Passage
        """
        if self.nextId is not None:
            return self.getTextualNode(self.nextId)

    @property
    def children(self):
        """ Children Passages

        :rtype: iterator(Passage)
        """
        for ID in self.childIds:
            yield self.getTextualNode(ID)

    @property
    def parent(self):
        """ Parent Passage

        :rtype: Passage
        """
        return self.getTextualNode(self.parentId)

    @property
    def first(self):
        """ First Passage

        :rtype: Passage
        """
        if self.firstId is not None:
            return self.getTextualNode(self.firstId)

    @property
    def last(self):
        """ Last Passage

        :rtype: Passage
        """
        if self.lastId is not None:
            return self.getTextualNode(self.lastId)

    @property
    def childIds(self):
        """ Identifiers of children

        :return: Identifiers of children
        :rtype: [str]
        """
        if self.__childIds__ is None:
            self.__childIds__ = self.getReffs()
        return self.__childIds__

    @property
    def firstId(self):
        """ First child of current Passage

        :rtype: str
        :returns: First passage node Information
        """
        if self.childIds is not None:
            if len(self.childIds) > 0:
                return self.childIds[0]
            return None
        else:
            raise NotImplementedError

    @property
    def lastId(self):
        """ Last child of current Passage

        :rtype: str
        :returns: Last passage Node representation
        """
        if self.childIds is not None:
            if len(self.childIds) > 0:
                return self.childIds[-1]
            return None
        else:
            raise NotImplementedError


class CTSNode(InteractiveTextualNode):
    """ Initiate a Resource object
    
    :param urn: A URN identifier
    :type urn: URN
    :param metadata: Collection Information about the Item
    :type metadata: Collection
    :param citation: Citation system of the text
    :type citation: Citation
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    :param resource: Resource used to navigate through the textual graph

    :cvar default_exclude: Default exclude for exports
    """

    def __init__(self, urn=None, **kwargs):
        super(CTSNode, self).__init__(identifier=str(urn), **kwargs)
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
        if isinstance(value, text_type):
            value = URN(value)
        elif not isinstance(value, URN):
            raise TypeError()
        self.__urn__ = value

    def getValidReff(self, level=1, reference=None):
        """ Given a resource, CitableText will compute valid reffs

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param passage: Subreference (optional)
        :type passage: Reference
        :rtype: List.text_type
        :returns: List of levels
        """
        raise NotImplementedError()

    def getLabel(self):
        """ Retrieve metadata about the text

        :rtype: Collection
        :returns: Retrieve Label informations in a Collection format
        """
        raise NotImplementedError()


class Passage(CTSNode):
    """ Passage objects possess metadata informations

    :param urn: A URN identifier
    :type urn: URN
    :param metadata: Collection Information about the Item
    :type metadata: Collection
    :param citation: Citation system of the text
    :type citation: Citation
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    :param resource: Resource used to navigate through the textual graph

    :cvar default_exclude: Default exclude for exports
    """

    def __init__(self, **kwargs):
        super(Passage, self).__init__(**kwargs)

    @property
    def reference(self):
        return self.urn.reference


class CitableText(CTSNode):
    """ A CTS CitableText
    """
    def __init__(self, citation=None, metadata=None, **kwargs):
        super(CitableText, self).__init__(citation=citation, metadata=metadata, **kwargs)
        self.__reffs__ = None

    @property
    def reffs(self):
        """ Get all valid reffs for every part of the CitableText

        :rtype: [str]
        """
        if not self.__reffs__:
            self.__reffs__ = [reff for reffs in [self.getReffs(level=i) for i in range(1, len(self.citation) + 1)] for reff in reffs]
        return self.__reffs__
