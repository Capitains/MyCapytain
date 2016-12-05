# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.retrievers.proto
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


class CitableTextServiceRetriever(API):
    """ Citable Text Service retrievers should have at least have some of the following properties

    """

    def getMetadata(self, objectId=None, **filters):
        """ Request metadata about a text or a collection

        :param objectId: Text Identifier
        :param filters: Kwargs parameters. URN and Inv are available
        :return: Metadata of text from an API or the likes as bytes
        """
        raise NotImplementedError

    def getText(self, textId, reference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: Text Identifier
        :param reference: Passage Reference
        :param prevnext: Retrieve graph representing previous and next passage
        :param metadata: Retrieve metadata about the passage and the text
        :return: Text of a Passage from an API or the likes as bytes
        """
        raise NotImplementedError

    def getSiblings(self, textId, reference):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :param reference: Passage Reference
        :return: Siblings references from an API or the likes as bytes
        """
        raise NotImplementedError

    def getChildren(self, textId, reference=None, depth=None):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :param reference: Passage Reference
        :return: Children references from an API or the likes as bytes
        """
        raise NotImplementedError


class CTS(CitableTextServiceRetriever):
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