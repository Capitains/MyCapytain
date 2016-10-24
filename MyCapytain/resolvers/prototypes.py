


class Resolver(object):
    def getMetadata(self, objectId=None, **filters):
        """ Request metadata about a text or a collection

        :param textId: Object Identifier to filter on
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
        :return: Graph
        """
        raise NotImplementedError

    def getChildren(self, textId, reference=None, depth=None):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :param reference: Passage Reference
        :return: Graph
        """
        raise NotImplementedError