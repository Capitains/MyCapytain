class API(object):
    """ API Prototype object """
    def init(self, endpoint):
        """ Instantiate an API class
        :param self: Object
        :type self: API
        :param endpoint: URL of the API
        :type endpoint: str or bytes
        """
        self.endpoint = endpoint

class Ahab(API):
    def search(self, query, urn, start=1, limit=5, format="json"):
        raise NotImplementedError()

    def permalink(self, urn, format="xml"):
        raise NotImplementedError()

class CTS(API):
    def getCapabilities(self):
        pass