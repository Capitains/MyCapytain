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


class TextualNode(object):
    def __init__(self, textId=None, graph=None, citation=None):
        self.__id__ = textId
        self.__graph__ = graph or Node()
        self.__citation__ = citation or Citation()
        self.__text__ = ""

    @property
    def citation(self):
        return self.__citation__

    @citation.setter
    def citation(self, value):
        if not isinstance(value, Citation):
            raise TypeError("Citation property can only be a Citation object")
        self.__citation__ = value

    def text(self):
        return self.__text__

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

    def default_export(self, output=Mimetypes.JSON_DTS, domain=""):
        """ Export the textual node item in the Mimetype required

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """
        raise NotImplementedError()

    def export(self, output=None):
        """ Export the collection item in the Mimetype required.

        ..note:: If current implementation does not have special mimetypes, reuses default_export method

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """
        return self.default_export(output)


class CTSNode(TextualNode):
    """ Initiate a Resource object
    
    :param urn: A URN identifier
    :type urn: URN
    """

    def __init__(self, urn=None, graph=None, citation=None):
        super(CTSNode, self).__init__(textId=str(urn), citation=citation, graph=graph)
        self._URN = None

        if urn is not None:
            self.urn = urn

    @property
    def urn(self):
        """ URN Identifier of the object

        :rtype: URN

        """
        return self._URN
    
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
        self._URN = value


class ParsedCTSNode(CTSNode):
    """

    :param resource: A resource
    :type resource: Any
    """
    def __init__(self, resource=None, *args, **kwargs):
        super(ParsedCTSNode, self).__init__(**kwargs)
        self.resource = resource


class Passage(ParsedCTSNode):
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
        raise NotImplementedError()

    @property
    def next(self):
        """ Following passage 

        :rtype: Passage
        :returns: Following passage at same level
        """ 
        raise NotImplementedError()

    @property
    def first(self):
        """ First child of current Passage 
        
        :rtype: None or Passage
        :returns: None if current Passage has no children,  first child passage if available
        """
        raise NotImplementedError()

    @property
    def last(self):
        """ Last child of current Passage 
        
        :rtype: None or Passage
        :returns: None if current Passage has no children, last child passage if available
        """
        raise NotImplementedError()

    @property
    def children(self):
        """ Children of the passage

        :rtype: OrderedDict
        :returns: Dictionary of chidren, where key are subreferences
        """
        raise NotImplementedError()


class Text(ParsedCTSNode):
    """ A CTS Text """
    def __init__(self, citation=None, metadata=None, **kwargs):
        super(Text, self).__init__(**kwargs)

        self._cRefPattern = Citation()
        if citation is not None:
            self.citation = citation

        if metadata is not None:
            self.metadata = metadata
        else:
            self.metadata = Metadata()

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

    def getChildren(self, reference=None, depth=None):
        """ Given a resource, Text will compute valid reffs

        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param passage: Subreference (optional)
        :type passage: Reference
        :rtype: List.basestring
        :returns: Node
        """
        raise NotImplementedError()

    def getPassage(self, reference):
        """ Retrieve a passage and store it in the object
        
        :param reference: Reference of the passage
        :type reference: MyCapytain.common.reference.Reference or List of basestring
        :rtype: Passage
        :returns: Object representing the passage
        :rtype: Passage

        :raises: *TypeError* when reference is not a list or a Reference
        """

        raise NotImplementedError()

    def getLabel(self):
        """ Retrieve metadata about the text
        
        :rtype: dict
        :returns: Dictionary with label informations
        """
        raise NotImplementedError()

    @property
    def reffs(self):
        """ Get all valid reffs for every part of the Text

        :rtype: MyCapytain.resources.texts.tei.Citation
        """
        return [reff for reffs in [self.getValidReff(level=i) for i in range(1, len(self.citation) + 1)] for reff in reffs]

    @property
    def citation(self):
        """ Get the lowest cRefPattern in the hierarchy

        :rtype: MyCapytain.common.reference.Citation
        """
        return self._cRefPattern
    
    @citation.setter
    def citation(self, value):
        """ Set the cRefPattern

        :param value: Citation to be saved
        :type value:  MyCapytain.common.reference.Citation
        """
        if isinstance(value, Citation):
            self._cRefPattern = value