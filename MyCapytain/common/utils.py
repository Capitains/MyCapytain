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


def formatXpath(xpath):
    """

    :param xpath:
    :return:
    """
    if len(xpath) > 1:
        current, queue = xpath[0], xpath[1:]
        current = "./{}[./{}]".format(
            current,
            "/".join(queue)
        )
    else:
        current, queue = "./{}".format(xpath[0]), []

    return current, queue


def performXpath(parent, xpath):
    """

    :param parent:
    :param xpath:
    :return:
    """
    if xpath.startswith(".//"):
        result = parent.xpath(
            parent.replace(".//", "./"),
            namespaces=NS
        )
        if len(result) == 0:
            result = parent.xpath(
                xpath,
                namespaces=NS
            )
    else:
        result = parent.xpath(
            xpath,
            namespaces=NS
        )
    return result


def copyNode(node, children=False, parent=False):
    """

    :param node:
    :param children:
    :param parent:
    :return:
    """
    if parent is not False:
        element = etree.SubElement(
            parent,
            node.tag,
            attrib=node.attrib,
            nsmap={None: "http://www.tei-c.org/ns/1.0"}
        )
    else:
        element = etree.Element(
            node.tag,
            attrib=node.attrib,
            nsmap={None: "http://www.tei-c.org/ns/1.0"}
        )
    if children:
        element.text = node.text
        for child in node:
            element.append(child)
    return element


def normalizeXpath(xpath):
    """ Normalize XPATH splitted around slashes

    :param xpath: List of xpath elements
    :type xpath: [str]
    :return: List of refined xpath
    :rtype: [str]
    """
    new_xpath = []
    for x in range(0, len(xpath)):
        if x > 0 and len(xpath[x-1]) == 0:
            new_xpath.append("/"+xpath[x])
        elif len(xpath[x]) > 0:
            new_xpath.append(xpath[x])
    return new_xpath


def passageLoop(parent, new_tree, xpath1, xpath2=None, preceding_siblings=False, following_siblings=False):
    """

    :param parent: Parent on which to perform xpath
    :param new_tree: Parent on which to add nodes
    :param xpath: List of xpath elements
    :type xpath: [str]
    :return:
    """

    current_1, queue_1 = formatXpath(xpath1)
    if xpath2 is None:  # In case we need what is following or preceding our node
        result_1 = performXpath(parent, current_1)[0]
        siblings = list(parent)
        index_1 = siblings.index(result_1)
        children = len(queue_1) == 0

        # We fill the gaps using the list option of LXML
        if preceding_siblings:
            [
                copyNode(child, parent=new_tree, children=True)
                for child in siblings
                if index_1 > siblings.index(child)
            ]
            child = copyNode(result_1, children=children, parent=new_tree)
        elif following_siblings:
            child = copyNode(result_1, children=children, parent=new_tree)
            [
                copyNode(child, parent=new_tree, children=True)
                for child in siblings
                if index_1 < siblings.index(child)
            ]

        if not children:
            child = passageLoop(
                result_1,
                child,
                queue_1,
                None,
                preceding_siblings=preceding_siblings,
                following_siblings=following_siblings
            )
    else:
        current_2, queue_2 = formatXpath(xpath2)

        result_1 = performXpath(parent, current_1)

        if xpath1 != xpath2:
            result_2 = performXpath(parent, current_2)
            result_1 = result_1[0]
            result_2 = result_2[0]
        else:
            result_2 = result_1 = result_1[0]

        if result_1 == result_2:
            children = len(queue_1) == 0
            child = copyNode(result_1, children=children, parent=new_tree)
            if not children:
                child = passageLoop(
                    result_1,
                    child,
                    queue_1,
                    queue_2
                )
        else:
            children = list(parent)
            index_1 = children.index(result_1)
            index_2 = children.index(result_2)
            # Appends the starting passage
            children_1 = len(queue_1) == 0
            child_1 = copyNode(result_1, children=children_1, parent=new_tree)
            if not children_1:
                passageLoop(result_1, child_1, queue_1, None, following_siblings=True)
            # Appends what's in between
            nodes = [
                copyNode(child, parent=new_tree, children=True)
                for child in children
                if index_1 < children.index(child) < index_2
            ]
            # Appends the Ending passage
            children_2 = len(queue_2) == 0
            child_2 = copyNode(result_2, children=children_2, parent=new_tree)

            if not children_2:
                passageLoop(result_2, child_2, queue_2, None, preceding_siblings=True)

    return new_tree