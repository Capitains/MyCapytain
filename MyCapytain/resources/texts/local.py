# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml


Local files handler for CTS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from collections import OrderedDict
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

    def __init__(self, citation=None, resource=None):
        self.passages = OrderedDict()
        self._cRefPattern = MyCapytain.resources.texts.tei.Citation()
        self.resource = None
        self.xml = None

        if citation is not None:
            self.citation = citation
        if resource is not None:
            self.resource = resource
            self.xml = xmlparser(resource)

            self.__findCRefPattern(self.xml)

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
        """
        a = OrderedDict()
        start = 1
        citations = [cite for cite in self.citation]

        if passage is not None:
            xml = self.__getNode(passage=passage)
            start = len(passage[2])
            nodes = passage[2] + [None]
            if level < start:
                level = start + 1
        else:
            xml = self.xml.xpath(self.citation.scope, namespaces=NS)[0]
            nodes = [None] * level

        for x in range(start, level+1):
            elements = xml.xpath("."+citations[x - 1].fill(passage=nodes[x-1], xpath=True), namespaces=NS)
            break

