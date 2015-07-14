# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml


Local files handler for CTS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from collections import OrderedDict, defaultdict
from MyCapytain.common.utils import xmlparser, NS
from MyCapytain.common.reference import URN, Citation, Reference
import MyCapytain.resources.texts.tei
from MyCapytain.resources.proto import text

class Text(text.Text):
    """ Implementation of CTS tools for local files 

    :param citation: A citation object
    :type citation: Citation
    :param resource:
    :type resource:

    :ivar passages: (OrderedDict) Dictionary of passages
    :ivar citation: (`MyCapytain.resources.texts.tei.Citation`)
    :ivar resource: Test
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


    def __findCRefPattern(self, xml):
        self.citation.ingest(xml.xpath("//tei:cRefPattern", namespaces=NS))

    @property
    def reffs(self):
        """ Get the lowest cRefPattern in the hierarchy
        :rtype: MyCapytain.resources.texts.tei.Citation
        """
        return self.getValidReff()

    @property
    def passages(self):
        """ Get the lowest cRefPattern in the hierarchy
        :rtype: MyCapytain.resources.texts.tei.Citation
        """
        return self._passages

    @property
    def urn(self):
        """ Get the lowest cRefPattern in the hierarchy
        :rtype: MyCapytain.resources.texts.tei.Citation
        """
        return self._URN
    
    @urn.setter
    def urn(self, value):
        """ Set the cRefPattern

        :param value: Citation to be saved
        :type value:  MyCapytain.resources.texts.tei.Citation or Citation
        :raises: TypeEr
        """
        self._URN = value

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

    def __getNode(self, passage=None):
        """ Retrieve a node from a passage

        :param passage:
        :type passage:
        """
        pass

    def getValidReff(self, level=1, passage=None):
        """ Retrieve valid passages directly 

        :param level: (1 Based)
        :type level: Level required
        :param passage: Passage Reference
        :type passage: Reference

        .. note:: GetValidReff works for now as a loop using Passage, subinstances of Text, to retrieve the valid informations. Maybe something is more powerfull ?
        """
        a = OrderedDict()
        start = 1
        xml = self.xml.xpath(self.citation.scope, namespaces=NS)[0]

        if passage is not None:
            start = len(passage[2])
            nodes = [".".join(passage[2][0:i+1]) for i in range(0, start)] + [None]
            if level < start:
                level = start + 1
        else:
            nodes = [None for i in range(0, level)]

        self._passages = TextTree(xml=xml, citation=self.citation, id=None)
        passages = [self._passages] # For consistency
        while len(nodes) >= 1:
            passages = [passage for sublist in [p.get(nodes[0]) for p in passages] for passage in sublist]
            nodes.pop(0)

        return [".".join(passage.id) for passage in passages]

class TextTree(object):
    """ Helper class for GetValidReff 

    """

    def __init__(self, xml, citation, id):
        self.xml = xml
        self.citation = citation
        self.id = id

        if id is None:
            self.id = []

        self.__children = OrderedDict()
        self.__parsed = False

    def get(self, key=None):
        if len(self.__children) == 0:
            if self.__parsed is True:
                return None
            else:
                self.__parse()

        if key is None:
            return [self.__children[key] for key in self.__children]
        elif key not in self.__children:
            print(key, list(self.__children.keys()))
            raise KeyError()
        else:
            return [self.__children[key]]

    def __parse(self):
        if self.citation is None:
            return []
        elements = self.xml.xpath("."+self.citation.fill(passage=None, xpath=True), namespaces=NS)
        for element in elements:
            n = self.id + [element.get("n")]
            self.__children[".".join(n)] = TextTree(
                xml=element,
                citation=self.citation.child,
                id=n
            )
        self.__parsed = True

    def __iter__(self):
        for key in self.__children:
            yield (key, self.__children[key])
    