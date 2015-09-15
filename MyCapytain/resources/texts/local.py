# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml


Local files handler for CTS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from collections import OrderedDict, defaultdict
from past.builtins import basestring

from MyCapytain.common.utils import xmlparser, NS
from MyCapytain.common.reference import URN, Citation, Reference
from MyCapytain.resources.proto import text
import MyCapytain.resources.texts.tei


class Text(text.Text):
    """ Implementation of CTS tools for local files
    
    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param citation: Highest Citation level
    :type citation: MyCapytain.common.reference.Citation

    :ivar resource: lxml
    """

    def __init__(self, urn=None, citation=None, resource=None):
        self._passages = OrderedDict() # Represents real full passages / reffs informations. Only way to set it up is getValidReff without passage ?
        self._orphan = defaultdict(Reference) # Represents passage we got without asking for all. Storing convenience ?

        self._cRefPattern = MyCapytain.resources.texts.tei.Citation()
        self.resource = None
        self.xml = None
        self._URN = None

        if citation is not None:
            self.citation = citation
        if resource is not None:
            self.resource = resource
            self.xml = xmlparser(resource)

            self.__findCRefPattern(self.xml)

            xml = self.xml.xpath(self.citation.scope, namespaces=NS)[0]
            self._passages = Passage(resource=xml, citation=self.citation, urn=self.urn, id=None)

    def __findCRefPattern(self, xml):
        self.citation = MyCapytain.resources.texts.tei.Citation.ingest(
            resource=xml.xpath("//tei:refsDecl[@n='CTS']", namespaces=MyCapytain.common.utils.NS),
            xpath=".//tei:cRefPattern"
        )

    @property
    def citation(self):
        """ Get the lowest cRefPattern in the hierarchy

        :rtype: MyCapytain.resources.texts.tei.Citation
        """
        return self._cRefPattern

    @citation.setter
    def citation(self, value):
        """ Set the cRefPattern

        :param value: Citation to be saved
        :type value:  MyCapytain.resources.texts.tei.Citation or Citation
        :raises: TypeError when value is not a TEI Citation or a Citation
        """
        if isinstance(value, MyCapytain.resources.texts.tei.Citation):
            self._cRefPattern = value
        elif isinstance(value, Citation):
            # .. todo:: Should support conversion between Citation...
            self._cRefPattern = MyCapytain.resources.texts.tei.Citation(
                name=value.name,
                refsDecl=value.refsDecl,
                child=value.child
            )

    def getPassage(self, reference):
        """ Finds a passage in the current text

        :param reference: Identifier of the subreference / passages
        :type reference: List, MyCapytain.common.reference.Reference
        :rtype: Passage 
        :returns: Asked passage
        """
        if isinstance(reference, MyCapytain.common.reference.Reference):
            reference = reference["start_list"]

        reference = [".".join(reference[:i]) for i in range(1, len(reference) + 1 )]
        passages = [self._passages]
        while len(reference) > 0:
            passages = [passage for sublist in [p.get(reference[0]) for p in passages] for passage in sublist]
            reference.pop(0)

        return passages[0]

    def getPassagePlus(self, reference):
        """ Finds a passage in the current text with its previous and following node

        :param reference: Identifier of the subreference / passages
        :type reference: List, MyCapytain.common.reference.Reference
        :rtype: text.PassagePlus
        :returns: Asked passage with metainformations
        """
        P = self.getPassage(reference=reference)
        return text.PassagePlus(P, P.prev.id, P.next.id)

    def getValidReff(self, level=1, reference=None):
        """ Retrieve valid passages directly 
        
        :param level: Depth required. If not set, should retrieve first encountered level (1 based)
        :type level: Int
        :param reference: Subreference (optional)
        :type reference: Reference
        :rtype: List.basestring
        :returns: List of levels

        .. note:: GetValidReff works for now as a loop using Passage, subinstances of Text, to retrieve the valid informations. Maybe something is more powerfull ?
        """

        if reference is not None:
            start = len(reference[2])
            nodes = [".".join(reference[2][0:i+1]) for i in range(0, start)] + [None]
            if level <= start:
                level = start + 1
        else:
            nodes = [None for i in range(0, level)]

        passages = [self._passages] # For consistency
        while len(nodes) >= 1:
            passages = [passage for sublist in [p.get(nodes[0]) for p in passages] for passage in sublist]
            nodes.pop(0)

        return [".".join(passage.id) for passage in passages]


class Passage(MyCapytain.resources.texts.tei.Passage):
    """ Passage representing object
    
    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param parent: Parent of the current passage
    :type parent: MyCapytain.resources.texts.tei.Passage
    :param citation: Citation for children level
    :type citation: MyCapytain.resources.texts.tei.Citation
    :param id: Identifier of the subreference without URN informations
    :type id: List

    .. note:: *id* is used in to identify the current passage in case the URN is unknown
    """

    def __init__(self, urn=None, resource=None, parent=None, citation=None, id=None):
        super(Passage, self).__init__(urn=urn, resource=resource, parent=parent)

        self.__next = False
        self.__prev = False

        self.citation = None
        if isinstance(citation, Citation):
            self.citation = citation

        self.__id = []

        if id is not None:
            self.id = id

        self.__children = OrderedDict()
        self.__parsed = False

    @property
    def id(self):
        """ Id represents the passage subreference as a list of basestring

        :rtype: list
        :returns: Representation of the passage subreference as a list
        """
        return self.__id

    @id.setter
    def id(self, value):
        """ Set up ID property

        :param value: Representation of the passage subreference as a list
        :type value: list

        .. note:: `Passage.id = [..]` will update automatically the URN property as well if correct
        """
        if isinstance(value, (list, tuple)):
            self.__id = value
            self.__updateURN()

    @property
    def urn(self):
        """ URN Identifier of the object

        :rtype: MyCapytain.common.reference.URN

        """
        return self._URN

    @urn.setter
    def urn(self, value):
        """ Set the urn

        :param value: URN to be saved
        :type value:  MyCapytain.common.reference.URN
        :raises: *TypeError* when the value is not URN compatible

        .. note:: `Passage.URN = ...` will update automatically the id property if Passage is set

        """
        a = self._URN
        if isinstance(value, basestring):
            value = MyCapytain.common.reference.URN(value)
        elif not isinstance(value, MyCapytain.common.reference.URN):
            raise TypeError()
        if str(a) != str(value):
            self._URN = value
            self.__updateURN()

    def __updateURN(self):
        """ Private method allowing for update of self.id or self.urn
        """
        if self.id is not None and len(self.id) > 0 and isinstance(self.urn, URN):
            self.urn = URN(self.urn["text"] + ":" + ".".join(self.id))
        elif self._URN is not None \
            and self._URN["reference"] is not None \
            and len(self._URN["reference"][2]) > 0 \
            and self.id != self._URN["reference"][2]:

            self.__id = self._URN["reference"][2]

    def get(self, key=None):
        """ Get a child or multiple children

        :param key: String identifying a passage
        :type key: basestring or int 
        :raises KeyError: When key identifies a child unknown to this passage
        :rtype: List.Passage
        :returns: List of passage identified by key. If key is None, returns all children
        
        .. note:: Call time depends on parsing status. If the passage was never parsed, then on first call citation is used to find children
        """
        if len(self.__children) == 0 and self.__parsed is False:
            self.__parse()

        if key is None:
            return [self.__children[key] for key in self.__children]
        elif isinstance(key, int):
            keys = list(self.__children.copy().keys())
            return [self.__children[keys[key]]]
        elif key not in self.__children:
            raise KeyError()
        else:
            return [self.__children[key]]

    def __parse(self):
        """ Private method for parsing children
        """
        if self.citation is None:
            self.__parsed = True
            return []
        elements = self.resource.xpath("."+self.citation.fill(passage=None, xpath=True), namespaces=NS)
        for element in elements:
            n = self.id + [element.get("n")]
            self.__children[".".join(n)] = Passage(
                resource=element,
                citation=self.citation.child,
                id=n,
                urn=self.urn,
                parent=self
            )
        self.__parsed = True

    @property
    def first(self):
        """ First child of current Passage 
        
        :rtype: None or Passage
        :returns: None if current Passage has no children,  first child passage if available
        """
        try:
            return self.get(0)[0]
        except:
            return None

    @property
    def last(self):
        """ Last child of current Passage 
        
        :rtype: None or Passage
        :returns: None if current Passage has no children, last child passage if available
        """
        try:
            return self.get(-1)[0]
        except :
            return None

    @property
    def children(self):
        """ Children of the passage

        :rtype: OrderedDict
        :returns: Dictionary of chidren, where key are subreferences
        """
        if len(self.__children) == 0 and self.__parsed is False:
            self.__parse()

        return self.__children
    
    @property
    def next(self):
        """ Next passage 

        :rtype: Passage
        :returns: Next passage at same level
        """ 
        if self.__next is False:

            if self.parent is None: # When top of hierarchy is access, should return None
                self.__next = None
                return None

            keys = list(self.parent.children.copy().keys())
            current = keys.index(".".join(self.id))
            if len(keys) - 1 > current:
                self.__next = self.parent.get(keys[current + 1])[0]
            else:
                n = self.parent.next
                if n is None:
                    self.__next = None
                else:
                    self.__next = n.first

        return self.__next

    @property
    def prev(self):
        """ Previous passage 

        :rtype: Passage
        :returns: Previous passage at same level
        """ 
        if self.__prev is False:

            if self.parent is None: # When top of hierarchy is access, should return None
                self.__prev = None
                return None

            keys = list(self.parent.children.copy().keys())
            current = keys.index(".".join(self.id))
            if current > 0:
                self.__prev = self.parent.get(keys[current - 1])[0]
            else:
                n = self.parent.prev
                if n is None:
                    self.__prev = None
                else:
                    self.__prev = n.last

        return self.__prev