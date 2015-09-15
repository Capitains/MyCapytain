# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.proto.text
   :synopsis: Prototypes for Text

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from past.builtins import basestring

import MyCapytain.common.reference
import MyCapytain.common.metadata
from collections import namedtuple

PassagePlus = namedtuple("PassagePlus", ["passage", "prev", "next"])


class Resource(object):
    """ Initiate a Resource object
    
    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: A resource
    :type resource: Any
    """

    def __init__(self, urn=None, resource=None):
        self.resource = None
        self._URN = None

        if urn is not None:
            self._URN = urn

        if resource is not None:
            self.resource = resource

    @property
    def urn(self):
        """ URN Identifier of the object

        :rtype: MyCapytain.common.reference.URN

        """
        return self._URN
    
    @urn.setter
    def urn(self, value):
        """ Set the urn

        :param value: URN to be saved
        :type value:  MyCapytain.common.reference.URN
        :raises: *TypeError* when the value is not URN compatible

        """
        if isinstance(value, basestring):
            value = MyCapytain.common.reference.URN(value)
        elif not isinstance(value, MyCapytain.common.reference.URN):
            raise TypeError()
        self._URN = value


class Passage(Resource):
    """ Passage representing object prototype
    
    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param parent: Parent of the current passage
    :type parent: MyCapytain.resources.texts.tei.Passage
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


class Text(Resource):
    """ A CTS Text """
    def __init__(self, citation=None, metadata=None, **kwargs):
        super(Text, self).__init__(**kwargs)

        self._cRefPattern = MyCapytain.common.reference.Citation()
        if citation is not None:
            self.citation = citation

        if metadata is not None:
            self.metadata = metadata
        else:
            self.metadata = MyCapytain.common.metadata.Metadata()

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

    def getPassage(self, reference):
        """ Retrieve a passage and store it in the object
        
        :param reference: Reference of the passage
        :type reference: MyCapytain.common.reference.Reference or List of basestring
        :rtype: Passage
        :returns: Object representing the passage
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
        if isinstance(value, MyCapytain.common.reference.Citation):
            self._cRefPattern = value