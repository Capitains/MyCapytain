from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.resources.texts.api.cts import Text, Passage
from MyCapytain.retrievers.cts5 import CTS


class HttpCTSResolver(Resolver):
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

    def getPassage(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: Text Identifier
        :param subreference: Passage Reference
        :param prevnext: Retrieve graph representing previous and next passage
        :param metadata: Retrieve metadata about the passage and the text
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
            return text.getPassage(reference=subreference)

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :param subreference: Passage Reference
        :return: (str, str)
        """
        text = Text(
            urn=textId,
            retriever=self.endpoint
        )
        return text.getPrevNextUrn(subreference)

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :param subreference: Passage Reference
        :return: (str, str)
        """
        text = Text(
            urn=textId,
            retriever=self.endpoint
        )
        return text.getPrevNextUrn(subreference)

