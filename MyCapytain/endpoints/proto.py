# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.endpoints.proto
   :synopsis: Prototypes of APIs endpoint

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""


class API(object):
    """
    API Prototype object

    :param self: Object
    :type self: API
    :param endpoint: URL of the API
    :type endpoint: text

    :ivar endpoint: Url of the endpoint
    """

    def __init__(self, endpoint):
        """ Instantiate an API class
        """
        self.endpoint = endpoint


class Ahab(API):
    """
    Abstract Capitains Ahab API
    See : http://capitains.github.io/pages/ahab.html
    """
    def search(self, query, urn, start=1, limit=5, format="json"):
        """ Perform a search on given namespace

        :param query: Term to perform search on
        :type query: text
        :param urn: Partial or complete urn identifying the request
        :type urn: text
        :param start: Starting element to display
        :type start: int
        :param limit: Limit of result displayed
        :type limit: int
        :param format: Format to request (json or xml)
        :type format: str
        :rtype: str
        """
        raise NotImplementedError()

    def permalink(self, urn, format="xml"):
        """ Perform a permalink request on API

        :rtype: str
        """
        raise NotImplementedError()


class CTS(API):
    """
    CTS API Endpoint Prototype 
    """
    def getCapabilities(self, inventory):
        """ Retrieve the inventory information of an API 

        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        raise NotImplementedError()

    def getValidReff(self, urn, inventory, level=1):
        """ Retrieve valid urn-references for a text

        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param level: Depth of references expected
        :type level: int
        :rtype: str
        """
        raise NotImplementedError()

    def getFirstUrn(self, urn, inventory):
        """ Retrieve the first passage urn of a text

        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        raise NotImplementedError()

    def getPrevNextUrn(self, urn, inventory):
        """ Retrieve the previous and next passage urn of one passage

        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        raise NotImplementedError()

    def getLabel(self, urn, inventory):
        """ Retrieve informations about a CTS Urn

        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        raise NotImplementedError()

    def getPassage(self, urn, inventory, context=None):
        """ Retrieve a passage

        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn, immediately preceding and immediately following the requested urn to include in the reply
        :type context: int
        :rtype: str
        """
        raise NotImplementedError()

    def getPassagePlus(self, urn, inventory, context=None):
        """ Retrieve a passage and informations about it
        
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn, immediately preceding and immediately following the requested urn to include in the reply
        :type context: int
        :rtype: str
        """
        raise NotImplementedError()