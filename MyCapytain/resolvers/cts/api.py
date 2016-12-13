# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resolvers.cts.api
   :synopsis: Resolver built for CTS APIs

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.resources.texts.api.cts import Text
from MyCapytain.resources.collections.cts import TextInventory
from MyCapytain.retrievers.cts5 import CTS


class HttpCTSResolver(Resolver):
    """ HttpCTSResolver provide a resolver for CTS API http endpoint.

    :param endpoint: CTS API Retriever
    :type endpoint: CTS

    :ivar endpoint: CTS API Retriever
    :type endpoint: CTS
    """
    def __init__(self, endpoint):
        if not isinstance(endpoint, CTS):
            raise TypeError("Endpoint should be a CTS Endpoint object")
        self.__endpoint__ = endpoint

    @property
    def endpoint(self):
        """ CTS Endpoint of the resolver

        :return: CTS Endpoint
        :rtype: CTS
        """
        return self.__endpoint__

    def getTextualNode(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: Text Identifier
        :type textId: str
        :param subreference: Passage Reference
        :type subreference: str
        :param prevnext: Retrieve graph representing previous and next passage
        :type prevnext: boolean
        :param metadata: Retrieve metadata about the passage and the text
        :type metadata: boolean
        :return: Passage
        :rtype: Passage
        """
        text = Text(
            urn=textId,
            retriever=self.endpoint
        )
        if metadata or prevnext:
            return text.getPassagePlus(reference=subreference)
        else:
            return text.getTextualNode(subreference=subreference)

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :type textId: str
        :param subreference: Passage Reference
        :type subreference: str
        :return: Tuple of references
        :rtype: (str, str)
        """
        text = Text(
            urn=textId,
            retriever=self.endpoint
        )
        return text.getPrevNextUrn(subreference)

    def getReffs(self, textId, level=1, subreference=None):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :type textId: str
        :param level: Depth for retrieval
        :type level: int
        :param subreference: Passage Reference
        :type subreference: str
        :return: List of references
        :rtype: [str]
        """
        text = Text(
            urn=textId,
            retriever=self.endpoint
        )
        return text.getReffs(level, subreference)

    def getMetadata(self, objectId=None, **filters):
        """ Request metadata about a text or a collection

        :param objectId: Object Identifier to filter on
        :type objectId: str
        :param filters: Kwargs parameters.
        :type filters: dict
        :return: Collection
        """
        if objectId is not None:
            filters["urn"] = objectId

        ti = TextInventory()
        ti.parse(self.endpoint.getCapabilities(**filters))
        if objectId:
            return [x for x in [ti] + ti.descendants if x.id == objectId][0]
        return ti
