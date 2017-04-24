# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.retrievers.protoypes
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


class CitableTextServiceRetriever(API):
    """ Citable CtsTextMetadata Service retrievers should have at least have some of the following properties

    """

    def getMetadata(self, objectId=None, **filters):
        """ Request metadata about a text or a collection

        :param objectId: CtsTextMetadata Identifier
        :param filters: Kwargs parameters. URN and Inv are available
        :return: Metadata of text from an API or the likes as bytes
        """
        raise NotImplementedError

    def getTextualNode(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: CtsTextMetadata Identifier
        :param subreference: CapitainsCtsPassage Reference
        :param prevnext: Retrieve graph representing previous and next passage
        :param metadata: Retrieve metadata about the passage and the text
        :return: CtsTextMetadata of a CapitainsCtsPassage from an API or the likes as bytes
        """
        raise NotImplementedError

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :param subreference: CapitainsCtsPassage Reference
        :return: Siblings references from an API or the likes as bytes
        """
        raise NotImplementedError

    def getReffs(self, textId, level=1, subreference=None):
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param level: Depth for retrieval
        :type level: int
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :return: List of references
        :rtype: [str]
        """
        raise NotImplementedError


class CtsRetriever(CitableTextServiceRetriever):
    """ CTS API Endpoint Prototype
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
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn, \
         immediately preceding and immediately following the requested urn to include in the reply
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
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn,\
         immediately preceding and immediately following the requested urn to include in the reply
        :type context: int
        :rtype: str
        """
        raise NotImplementedError()
