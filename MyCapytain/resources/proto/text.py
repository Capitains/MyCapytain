# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.proto.text
   :synopsis: Prototypes for Text

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from . import inventory

class Resource(object):
    def __init__(self, urn, resource= None):
        """ Initiate a Resource object
        
        :param resource: A resource
        :type resource: Any
        """
        self.urn = urn
        self.resource = resource

class Passage(Resource):
    def setText(self):
        raise NotImplementedError()

    def getText(self):
        raise NotImplementedError()

    def getNext(self):
        raise NotImplementedError()

    def getPrev(self):
        raise NotImplementedError()

class Text(Resource):
    """ A CTS Text """
        
    def __parseReference(self, reference):
        """ Parse a CTS URN
        
        :param reference: A urn or a passage reference
        :type reference: str
        :rtype: List.str
        :returns: List of references
        """
        if ":" in reference:
            reference = reference.split(":")[-1]
        return reference.split("-")

    def getValidReff(self, level = None):
        """ Given a resource, Text will compute valid reffs 
        
        :param level: Depth required. If not set, should retrieve deeper level
        :type level: Int
        :rtype: List
        :returns: List of levels
        """
        raise NotImplementedError()

    def getPassage(self, reference):
        """ Retrieve a passage and store it in the object
        
        :param reference: Reference of the passage
        :type reference: str
        :rtype: Passage
        :returns: Object representing the passage
        """
        raise NotImplementedError()

    def getLabel(self):
        """ Retrieve a passage and store it in the object
        
        :param reference: Reference of the passage
        :type reference: str
        :rtype: dict
        :returns: Dictionary with label informations
        """
        raise NotImplementedError()