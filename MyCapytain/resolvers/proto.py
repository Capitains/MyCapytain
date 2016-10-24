from MyCapytain.retrievers.proto import CitableTextServiceRetriever


class Resolver(CitableTextServiceRetriever):
    def __init__(self, endpoint):
        super(Resolver, self).__init__(endpoint)

    def getMetadata(self, textId=None, **filters):
        """ Request metadata about a text or a collection

        :param textId: Text Identifier
        :param filters: Kwargs parameters. URN and Inv are available
        :return: Collection
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