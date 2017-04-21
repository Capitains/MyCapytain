# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resolvers.cts.remote
   :synopsis: Resolver built for CTS APIs

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.resources.texts.remote.cts import CtsText
from MyCapytain.resources.collections.cts import XmlCtsTextInventoryMetadata
from MyCapytain.retrievers.cts5 import HttpCtsRetriever


class HttpCtsResolver(Resolver):
    """ HttpCtsResolver provide a resolver for CTS API http endpoint.

    :param endpoint: CTS API Retriever
    :type endpoint: CTS

    :ivar endpoint: CTS API Retriever
    :type endpoint: HttpCtsRetriever
    """
    def __init__(self, endpoint):
        if not isinstance(endpoint, HttpCtsRetriever):
            raise TypeError("Endpoint should be a CTS Endpoint object")
        self.__endpoint__ = endpoint

    @property
    def endpoint(self):
        """ CTS Endpoint of the resolver

        :return: CTS Endpoint
        :rtype: HttpCtsRetriever
        """
        return self.__endpoint__

    def getTextualNode(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :param prevnext: Retrieve graph representing previous and next passage
        :type prevnext: boolean
        :param metadata: Retrieve metadata about the passage and the text
        :type metadata: boolean
        :return: CapitainsCtsPassage
        :rtype: CapitainsCtsPassage
        """
        text = CtsText(
            urn=textId,
            retriever=self.endpoint
        )
        if metadata or prevnext:
            return text.getPassagePlus(reference=subreference)
        else:
            return text.getTextualNode(subreference=subreference)

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :return: Tuple of references
        :rtype: (str, str)
        """
        text = CtsText(
            urn=textId,
            retriever=self.endpoint
        )
        return text.getPrevNextUrn(subreference)

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
        text = CtsText(
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

        ti = XmlCtsTextInventoryMetadata.parse(self.endpoint.getCapabilities(**filters))
        if objectId:
            return [x for x in [ti] + ti.descendants if x.id == objectId][0]
        return ti
