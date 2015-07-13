# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml


Local files handler for CTS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from collections import OrderedDict
from MyCapytain.common.utils import xmlparser, NS
from MyCapytain.common.reference import URN, Citation
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
        print([el.get("n") for el in xml.xpath("//tei:cRefPattern", namespaces=NS)])
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
        if isinstance(value,  MyCapytain.resources.texts.tei.Citation):
            self._cRefPattern = value
        elif isinstance(value, Citation):
            # .. todo:: Should support conversion between Citation...
            self._cRefPattern = MyCapytain.resources.texts.tei.Citation(name=value.name, xpath=value.xpath, scope=value.scope, child=value.child)