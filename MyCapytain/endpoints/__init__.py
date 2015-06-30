from . import proto

class CTS(proto.CTS):
    """ Basic integration of the proto.CTS abstractiojn
    """

    def call(self, parameters):
        """ Call an endpoint given the parameters
        :param parameters: Dictionary of parameters
        :type parameters: dict
        :rtype: text
        """
        # DEV !
        return self.endpoint+"?"+"&".join([key+"="+parameters[key] for key in parameters])

    def getCapabilities(self, **kwargs):
        """ Retrieve the inventory information of an API 
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        args = dict(kwargs)
        args["request"] = "GetCapabilities"
        return self.call(args)

    def getValidReff(self, **kwargs):
        """ Retrieve valid urn-references for a text
        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param level: Depth of references expected
        :type level: int
        :rtype: str
        """
        raise NotImplementedError()

    def getFirstUrn(self, **kwargs):
        """ Retrieve the first passage urn of a text
        :param urn: URN identifying the text
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        raise NotImplementedError()

    def getPrevNextUrn(self, **kwargs):
        """ Retrieve the previous and next passage urn of one passage
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        raise NotImplementedError()

    def getLabel(self, **kwargs):
        """ Retrieve informations about a CTS Urn
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :rtype: str
        """
        raise NotImplementedError()

    def getPassage(self, **kwargs):
        """ Retrieve a passage
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn, immediately preceding and immediately following the requested urn to include in the reply
        :type context: int
        :rtype: str
        """
        raise NotImplementedError()

    def getPassagePlus(self, **kwargs):
        """ Retrieve a passage and informations about it
        :param urn: URN identifying the text's passage (Minimum depth : 1)
        :type urn: text
        :param inventory: Name of the inventory
        :type inventory: text
        :param context: Number of citation units at the same level of the citation hierarchy as the requested urn, immediately preceding and immediately following the requested urn to include in the reply
        :type context: int
        :rtype: str
        """
        raise NotImplementedError()