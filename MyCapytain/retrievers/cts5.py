# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.retrievers.cts5
   :synopsis: Cts5 endpoint implementation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
import MyCapytain.retrievers.prototypes
from MyCapytain.common.reference import Reference
import requests


class HttpCtsRetriever(MyCapytain.retrievers.prototypes.CtsRetriever):
    """ Basic integration of the MyCapytain.retrievers.proto.CTS abstraction
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
        super(HttpCtsRetriever, self).__init__(endpoint)
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
        request.raise_for_status()
        if request.encoding is None:
            request.encoding = "utf-8"
        return request.text

    def getCapabilities(self, inventory=None, urn=None):
        """ Retrieve the inventory information of an API

        :param inventory: Name of the inventory
        :type inventory: text
        :param urn: URN to filter with
        :type urn: str
        :rtype: str
        """
        return self.call({
            "inv": inventory,
            "urn": urn,
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
        :return: XML Response from the API as string
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
        """ Retrieve a passage and information about it

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

    #
    # Common methods
    #

    def getMetadata(self, objectId=None, **filters):
        """ Request metadata about a text or a collection

        :param objectId: Filter for some object identifier
        :param filters: Kwargs parameters. URN and Inv are available
        :return: GetCapabilities CTS API request response
        """
        filters.update({"urn": objectId})
        return self.getCapabilities(**filters)

    def getTextualNode(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: CtsTextMetadata Identifier
        :param subreference: CapitainsCtsPassage Reference
        :param prevnext: Retrieve graph representing previous and next passage
        :param metadata: Retrieve metadata about the passage and the text
        :return: GetPassage or GetPassagePlus CTS API request response
        """
        if  subreference:
            textId = "{}:{}".format(textId, subreference)

        if prevnext or metadata:
            return self.getPassagePlus(urn=textId)
        else:
            return self.getPassage(urn=textId)

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :param reference: CapitainsCtsPassage Reference
        :return: GetPrevNextUrn request response from the endpoint
        """
        textId = "{}:{}".format(textId, subreference)
        return self.getPrevNextUrn(urn=textId)

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
        depth = level
        if subreference:
            textId = "{}:{}".format(textId, subreference)
        if subreference:
            if isinstance(subreference, Reference):
                depth += len(subreference)
            else:
                depth += len(Reference(subreference))
        if level:
            level = max(depth, level)
        return self.getValidReff(urn=textId, level=level)
