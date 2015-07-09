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

NS = {
    "tei": "http://www.tei-c.org/ns/1.0",
    "ahab": "http://localhost.local",
    "ti": "http://chs.harvard.edu/xmlns/cts",
    "xml": "http://www.w3.org/XML/1998/namespace"
}

def xmlparser(xml):
    doclose = None
    if isinstance(xml, etree._Element):
        return xml
    elif isinstance(xml, IOBase):
        pass
    elif isinstance(xml, (basestring)):
        xml = StringIO(xml)
        doclose = True
    else:
        raise TypeError("Unsupported type of resource")
    parsed = etree.parse(xml).getroot()
    if doclose:
        xml.close()
    return parsed

