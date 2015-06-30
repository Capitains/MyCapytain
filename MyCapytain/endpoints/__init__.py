from . import proto
import requests

class Ahab(proto.Ahab):
    """ Basic integration of the proto.CTS abstractiojn
    """
    pass

class CTS(proto.CTS):
    """ Basic integration of the proto.CTS abstraction
    """

    def call(self, parameters):
        """ Call an endpoint given the parameters
        :param parameters: Dictionary of parameters
        :type parameters: dict
        :rtype: text
        """
        # DEV !
        parameters = dict((key,parameters[key]) for key in parameters if parameters[key] is not None)
        request = requests.get(self.endpoint, params=parameters)
        return request.text

    def getCapabilities(self, inventory):
        """ Retrieve the inventory information of an API 
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        return self.call({
                "inv" : inventory,
                "request" : "GetCapabilities"
            })

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
        return self.call({
                "inv" : inventory,
                "urn" : urn,
                "level" : level,
                "request" : "GetValidReff"
            })

    def getFirstUrn(self, urn, inventory):
        """ Retrieve the first passage urn of a text
        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        return self.call({
                "inv" : inventory,
                "urn" : urn,
                "request" : "GetFirstUrn"
            })

    def getPrevNextUrn(self, urn, inventory):
        """ Retrieve the previous and next passage urn of one passage
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        return self.call({
                "inv" : inventory,
                "urn" : urn,
                "request" : "GetPrevNextUrn"
            })

    def getLabel(self, urn, inventory):
        """ Retrieve informations about a CTS Urn
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        return self.call({
                "inv" : inventory,
                "urn" : urn,
                "request" : "GetLabel"
            })

    def getPassage(self, urn, inventory, context=None):
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
                "inv" : inventory,
                "urn" : urn,
                "context" : context,
                "request" : "GetPassage"
            })


    def getPassagePlus(self, urn, inventory, context=None):
        """ Retrieve a passage and informations about it
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn, immediately preceding and immediately following the requested urn to include in the reply
        :type context: int
        :rtype: str
        """
        return self.call({
                "inv" : inventory,
                "urn" : urn,
                "context" : context,
                "request" : "GetPassagePlus"
            })