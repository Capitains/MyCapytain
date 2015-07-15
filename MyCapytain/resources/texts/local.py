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
        self._passages = OrderedDict() #: Represents real full passages / reffs informations. Only way to set it up is getValidReff without passage ?
        self._orphan = defaultdict(Reference) #: Represents passage we got without asking for all. Storing convenience ?

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
            self._passages = Passage(resource=xml, citation=self.citation, id=None, urn=self.urn)

    def __findCRefPattern(self, xml):
        self.citation.ingest(xml.xpath("//tei:cRefPattern", namespaces=NS))

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
            self._cRefPattern = MyCapytain.resources.texts.tei.Citation(name=value.name, refsDecl=value.refsDecl, child=value.child)

    def getPassage(self, reference):
        if isinstance(reference, MyCapytain.common.reference.Reference):
            reference = reference["start_list"]

        reference = [".".join(reference[:i]) for i in range(1, len(reference) + 1)]
        print(reference)

        passages = [self._passages]
        while len(reference) > 0:
            passages = [passage for sublist in [p.get(reference[0]) for p in passages] for passage in sublist]
            reference.pop(0)
            
        return passages[0]

    def getPassagePlus(self, reference):
        P = self.getPassage(reference=reference)
        return {
            "passage" : P,
            "next" : P.next.urn,
            "prev" : P.prev.urn
        }

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
        a = OrderedDict()
        start = 1

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
    """ Helper class for GetValidReff : class for ordered tree path discovering

    """

    def __init__(self, urn=None, resource=None, parent=None, citation=None, id=None):
        super(Passage, self).__init__(urn=urn, resource=resource, parent=parent)

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
        return self.__id

    @id.setter
    def id(self, value):
        if isinstance(value, (list, tuple)):
            self.__id = value
            self.__updateURN()

    @property
    def urn(self):
        return self._URN

    @urn.setter
    def urn(self, value):
        a = self._URN
        if isinstance(value, basestring):
            value = MyCapytain.common.reference.URN(value)
        elif not isinstance(value, MyCapytain.common.reference.URN):
            raise TypeError()
        if str(a) != str(value):
            self._URN = value
            self.__updateURN()

    def __updateURN(self):
        if self.id is not None and len(self.id) > 0 and isinstance(self.urn, URN):
            self.urn = URN(self.urn["text"] + ":" + ".".join(self.id))
        elif self._URN is not None \
             and self._URN["reference"] is not None \
             and len(self._URN["reference"][2]) > 0 \
             and self.id != self._URN["reference"][2]:

            self.__id = self._URN["reference"][2]
    
    def get(self, key=None):
        """ Get a children """
        if len(self.__children) == 0 and self.__parsed is False:
            self.__parse()

        if key is None:
            return [self.__children[key] for key in self.__children]
        elif key not in self.__children:
            raise KeyError()
        else:
            return [self.__children[key]]

    def __parse(self):
        if self.citation is None:
            return []
        elements = self.resource.xpath("."+self.citation.fill(passage=None, xpath=True), namespaces=NS)
        for element in elements:
            n = self.id + [element.get("n")]
            self.__children[".".join(n)] = Passage(
                resource=element,
                citation=self.citation.child,
                id=n,
                urn=self.urn,
                parent=self.parent
            )
        self.__parsed = True
    