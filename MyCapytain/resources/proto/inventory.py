"""
    Resources Prototypes
"""

class Resource(object):
    """ Resource represents any resource from the inventory """
    def __init__(self, resource=None):
        """ Initiate a TextInventory resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        """
        if resource is not None:
            self.setResource(resource)

    def setResource(self, resource):
        """ Set the object property resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :rtype: Any
        :returns: Input resource
        """
        self.resource = resource
        self.parse(resource)
        return self.resource

    def parse(self, resource):
        """ Parse the object resource 

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :rtype: List
        """
        raise NotImplementedError()

class Text(Resource):
    """ Represents a CTS Text
    """
    def __init__(self, resource=None, urn=None, parents=None, type="Edition"):
        """ Initiate a Work resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :param urn: Identifier of the Text
        :type urn: str
        """
        self.urn = None
        if resource is not None:
            self.setResource(resource)
        self.parents = ()
        if parents is not None:
            self.parents = None

    def getWork(self):
        """ Find Work parent
        
        :rtype: Work
        :returns: The Work
        """
        return self.parents[2]

    def getTextGroup(self):
        """ Find TextGroup parent
        
        :rtype: TextGroup
        :returns: The TextGroup
        """
        return self.parents[1]

    def getInventory(self):
        """ Find Inventory parent
        
        :rtype: TextInventory
        :returns: The Inventory
        """
        return self.parents[0]

def Edition(resource=None, urn=None):
    return Text(resource=resource, urn=urn, parents=None, type="Edition")

def Translation(resource=None, urn=None):
    return Text(resource=resource, urn=urn, parents=None, type="Translation")
    
class Work(Resource):
    """ Represents a CTS Work
    """
    def __init__(self, resource=None, urn=None, parents=None):
        """ Initiate a Work resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :param urn: Identifier of the Work
        :type urn: str
        :param parents: List of parents for current object
        :type parents: Tuple.<TextInventory> 
        """
        self.urn = None
        self.texts = []
        if resource is not None:
            self.setResource(resource)

        self.parents = ()
        if parents is not None:
            self.parents = parents

    def getTextGroup(self):
        """ Find TextGroup parent
        
        :rtype: TextGroup
        :returns: The TextGroup
        """
        return self.parents[1]

    def getInventory(self):
        """ Find Inventory parent
        
        :rtype: TextInventory
        :returns: The Inventory
        """
        return self.parents[0]

class TextGroup(Resource):
    """ Represents a CTS Textgroup
    """
    def __init__(self, resource=None, urn=None, parents=None):
        """ Initiate a TextGroup resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :param urn: Identifier of the TextGroup
        :type urn: str
        :param parents: List of parents for current object
        :type parents: Tuple.<TextInventory> 
        """
        self.urn = None
        self.works = []

        self.parents = ()
        if parents:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    def getInventory(self):
        """ Find Inventory parent

        :rtype: TextInventory
        :returns: The Inventory
        """
        return self.parents[0]

class TextInventory(Resource):
    """ Represents a CTS Inventory file
    """
    def __init__(self, resource=None, id=None):
        """ Initiate a TextInventory resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :param id: Identifier of the TextInventory
        :type id: str
        """
        self.textgroups = []
        self.id = id
        if resource is not None:
            self.setResource(resource)

    def parse(self, resource):
        """ Parse the object resource 

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        :rtype: List
        :returns: List of TextGroup objects
        """
        self.textgroups = []
        return self.textgroups