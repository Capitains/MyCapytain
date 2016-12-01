class Resolver(object):
    def getMetadata(self, objectId=None, **filters):
        """ Request metadata about a text or a collection

        :param textId: Object Identifier to filter on
        :param filters: Kwargs parameters. URN and Inv are available
        :return: Collection
        """
        raise NotImplementedError

    def getPassage(self, textId, subreference=None, prevnext=False, metadata=False):
        """ Retrieve a text node from the API

        :param textId: Text Identifier
        :param subreference: Passage Reference
        :param prevnext: Retrieve graph representing previous and next passage
        :param metadata: Retrieve metadata about the passage and the text
        :return: Passage
        :rtype: Passage
        """
        raise NotImplementedError()

    def getSiblings(self, textId, subreference):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :param subreference: Passage Reference
        :return: (str, str)
        """
        raise NotImplementedError()

    def getChildren(self, textId, reference=None, depth=None):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :param reference: Passage Reference
        :return: Graph
        """
        raise NotImplementedError()
