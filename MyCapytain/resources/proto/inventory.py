"""
    Resources Prototypes
"""
from ...utils import URN, Reference
from past.builtins import basestring

class Resource(object):
    """ Resource represents any resource from the inventory """
    def __init__(self, resource=None):
        """ Initiate a TextInventory resource

        :param resource: Resource representing the TextInventory 
        :type resource: Any
        """
        if resource is not None:
            self.setResource(resource)

    def __getitem__(self, key):
        """ Direct key access function for Text objects """
        if key == 0:
            return self
        elif isinstance(key, int) and 1 <= key <= len(self.parents):
            r = self.parents[key - 1]
            if isinstance(r, (list, tuple)):
                return r[0]
            else:
                return r
        elif isinstance(key, basestring):
            return self.__urnitem__(key)
        else:
            None

    def __eq__(self, other):
        if self is other:
            return True
        if not isinstance(other, self.__class__):
            return False
        if self.resource is None:
            # Not totally true
            return (hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn)
        return (hasattr(self, "urn") and hasattr(other, "urn") and self.urn == other.urn) and self.resource == other.resource

    def __urnitem__(self, key):
        urn = URN(key)

        if len(urn) <= 2:
            raise ValueError("Not valid urn")
        elif hasattr(self, "urn") and self.urn == urn:
            return self
        else:
            if hasattr(self, "urn"):
                i = len(self.urn)
            else:
                i = 2

            if isinstance(self, TextInventory):
                children = self.textgroups
            elif isinstance(self, TextGroup):
                children = self.works
            elif isinstance(self, Work):
                children = self.texts

            order = ["", "", "textgroup", "work", "text"]

            while i <= len(urn) - 1:
                children = children[urn[order[i]]]
                if not hasattr(children, "urn"):
                    raise ValueError("Unrecognized urn at level " + order[i])
                i += 1
            return children

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
        self.parents = ()

        if urn is not None:
            self.urn = URN(urn)

        if parents is not None:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    def getWork(self):
        """ Find Work parent
        
        :rtype: Work
        :returns: The Work
        """
        return self[1]

    def getTextGroup(self):
        """ Find TextGroup parent
        
        :rtype: TextGroup
        :returns: The TextGroup
        """
        return self[2]

    def getInventory(self):
        """ Find Inventory parent
        
        :rtype: TextInventory
        :returns: The Inventory
        """
        return self[3]

def Edition(resource=None, urn=None, parents=None):
    return Text(resource=resource, urn=urn, parents=parents, type="Edition")

def Translation(resource=None, urn=None, parents=None):
    return Text(resource=resource, urn=urn, parents=parents, type="Translation")
    
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
        self.parents = ()

        if urn is not None:
            self.urn = URN(urn)

        if parents is not None:
            self.parents = parents

        if resource is not None:
            self.setResource(resource)

    def getTextGroup(self):
        """ Find TextGroup parent
        
        :rtype: TextGroup
        :returns: The TextGroup
        """
        return self.parents[0]

    def getInventory(self):
        """ Find Inventory parent
        
        :rtype: TextInventory
        :returns: The Inventory
        """
        return self.parents[1]

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

        if urn is not None:
            self.urn = URN(urn)

        if parents:
            self.parents = [parents]

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
        self.parents = ()
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