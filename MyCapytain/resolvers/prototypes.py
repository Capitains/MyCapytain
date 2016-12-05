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

    def getReffs(self, textId, level=1, subreference=None):
        """ Retrieve the siblings of a textual node

        :param textId: Text Identifier
        :param level: Depth for retrieval
        :param subreference: Passage Reference
        :return: (str, str)
        """
        raise NotImplementedError()
