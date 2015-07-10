# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml


Local files handler for CTS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from collections import OrderedDict
from MyCapytain.common.utils import xmlparser
from MyCapytain.common.reference import URN
from MyCapytain.resources.texts.tei import Citation
from MyCapytain.resources.proto import text

class Text(text.Text):
    """ Implementation of CTS tools for local files 

    :param citation: A citation object
    :type citation: Citation
    :param resource:
    :type resource:

    :ivar passages: (OrderedDict) Dictionary of passages
    :ivar citation: (Citation)
    :ivar resource: Test
    """

    def __init__(self, citation=None, resource=None):
        self.passages = OrderedDict()
        self.citation = None
        self.resource = None

        if citation is not None:
            self.citation = citation
        if resource is not None:
            self.resource = resource

    def parse(self, resource):
        pass