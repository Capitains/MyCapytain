# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.endpoints.cts5
   :synopsis: CTS5 endpoint implementation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
import MyCapytain.endpoints.proto
import requests


class CTS(MyCapytain.endpoints.proto.CTS):

    """ 
        Basic integration of the MyCapytain.endpoints.proto.CTS abstraction
    """

    def __init__(self, endpoint, inventory=None):
        """ API Prototype object

        :param self: Object
        :type self: API
        :param endpoint: URL of the API
        :type endpoint: str
        :param inventory: Inventory to use
        :type inventory: str

        :ivar endpoint: Url of the endpoint
        :ivar inventory: Default Inventory
        """
        super(CTS, self).__init__(endpoint)
        self.inventory = inventory

    def call(self, parameters):
        """ Call an endpoint given the parameters
        
        :param parameters: Dictionary of parameters
        :type parameters: dict
        :rtype: text
        """
        # DEV !
        parameters = {
            key: str(parameters[key]) for key in parameters if parameters[key] is not None
        }
        if self.inventory is not None and "inv" not in parameters:
            parameters["inv"] = self.inventory

        request = requests.get(self.endpoint, params=parameters)
        return request.text

    def getCapabilities(self, inventory=None):
        """ Retrieve the inventory information of an API 
        
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        return self.call({
            "inv": inventory,
            "request": "GetCapabilities"
        })

    def getValidReff(self, urn, inventory=None, level=None):
        """ Retrieve valid urn-references for a text
        
        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param level: Depth of references expected
        :type level: int
        :rtype: str
        """
        return self.call({
            "inv": inventory,
            "urn": urn,
            "level": level,
            "request": "GetValidReff"
        })

    def getFirstUrn(self, urn, inventory=None):
        """ Retrieve the first passage urn of a text
        
        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        return self.call({
            "inv": inventory,
            "urn": urn,
            "request": "GetFirstUrn"
        })

    def getPrevNextUrn(self, urn, inventory=None):
        """ Retrieve the previous and next passage urn of one passage
        
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        return self.call({
            "inv": inventory,
            "urn": urn,
            "request": "GetPrevNextUrn"
        })

    def getLabel(self, urn, inventory=None):
        """ Retrieve informations about a CTS Urn
        
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        return self.call({
            "inv": inventory,
            "urn": urn,
            "request": "GetLabel"
        })

    def getPassage(self, urn, inventory=None, context=None):
        """ Retrieve a passage
        
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn, immediately preceding and immediately following the requested urn to include in the reply
        :type context: int
        :rtype: str
        """
        return self.call({
            "inv": inventory,
            "urn": urn,
            "context": context,
            "request": "GetPassage"
        })

    def getPassagePlus(self, urn, inventory=None, context=None):
        """ Retrieve a passage and informations about it
        
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn, immediately preceding and immediately following the requested urn to include in the reply
        :type context: int
        :rtype: str
        """
        return self.call({
            "inv": inventory,
            "urn": urn,
            "context": context,
            "request": "GetPassagePlus"
        })
