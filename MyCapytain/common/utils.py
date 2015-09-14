# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.reference
   :synopsis: Common useful tools and constants

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals


from lxml import etree
from io import IOBase, StringIO
from past.builtins import basestring
import re

__strip = re.compile("([ ]{2,})+")


def normalize(string):
    """ Remove double-or-more spaces in a string

    :param string: A string to change
    :type string: basestring
    :rtype: Basestring
    :returns: Clean string
    """
    return __strip.sub(" ", string)

#: Dictionary of namespace that can be useful
NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "ahab": "http://localhost.local",
    "ti": "http://chs.harvard.edu/xmlns/cts",
    "xml": "http://www.w3.org/XML/1998/namespace"
}


def xmlparser(xml):
    """ Parse xml 

    :param xml: XML element
    :type xml: basestring, lxml.etree._Element
    :rtype: lxml.etree._Element
    :returns: An element object
    :raises: TypeError if element is not in accepted type

    """
    doclose = None
    if isinstance(xml, etree._Element):
        return xml
    elif isinstance(xml, IOBase):
        pass
    elif isinstance(xml, basestring):
        xml = StringIO(xml)
        doclose = True
    else:
        raise TypeError("Unsupported type of resource")
    parsed = etree.parse(xml).getroot()
    if doclose:
        xml.close()
    return parsed

