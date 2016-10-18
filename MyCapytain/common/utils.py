# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.reference
   :synopsis: Common useful tools and constants

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals
from functools import reduce

from collections import OrderedDict
from lxml import etree
from io import IOBase, StringIO
from past.builtins import basestring
import re
from copy import copy
from lxml.objectify import ObjectifiedElement


__strip = re.compile("([ ]{2,})+")
__parser__ = etree.XMLParser(collect_ids=False, resolve_entities=False)


def xmliter(node):
    """ Provides a simple XML Iter method which complies with either _Element or _ObjectifiedElement

    :param node: XML Node
    :return: Iterator for iterating over children of said node.
    """
    if hasattr(node, "iterchildren"):
        return node.iterchildren()
    else:
        return node


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
    if isinstance(xml, (etree._Element, ObjectifiedElement, etree._ElementTree)):
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
    """ Perform an XPath on an element and indicate if we need to loop over it to find something

    :param parent: XML Node on which to perform XPath
    :param xpath: XPath to run
    :return: (Result, Need to loop Indicator)
    """
    loop = False
    if xpath.startswith(".//"):
        result = parent.xpath(
            xpath.replace(".//", "./"),
            namespaces=NS
        )
        if len(result) == 0:
            result = parent.xpath(
                "*[{}]".format(xpath),
                namespaces=NS
            )
            loop = True
    else:
        result = parent.xpath(
            xpath,
            namespaces=NS
        )
    return result[0], loop


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
        for child in xmliter(node):
            element.append(copy(child))
    return element


def normalizeXpath(xpath):
    """ Normalize XPATH split around slashes

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
    """ Loop over passages to construct and increment new tree given a parent and XPaths

    :param parent: Parent on which to perform xpath
    :param new_tree: Parent on which to add nodes
    :param xpath1: List of xpath elements
    :type xpath1: [str]
    :param xpath2: List of xpath elements
    :type xpath2: [str]
    :param preceding_siblings: Append preceding siblings of XPath 1/2 match to the tree
    :param following_siblings: Append following siblings of XPath 1/2 match to the tree
    :return: Newly incremented tree
    """
    current_1, queue_1 = formatXpath(xpath1)
    if xpath2 is None:  # In case we need what is following or preceding our node
        result_1, loop = performXpath(parent, current_1)
        if loop is True:
            queue_1 = xpath1

        central = None
        has_no_queue = len(queue_1) == 0
        # For each sibling, when we need them in the context of a range
        if preceding_siblings or following_siblings:
            for sibling in xmliter(parent):
                if sibling == result_1:
                    central = True
                    # We copy the node we looked for (Result_1)
                    child = copyNode(result_1, children=has_no_queue, parent=new_tree)
                    # if we don't have children
                    # we loop over the passage child
                    if not has_no_queue:
                        passageLoop(
                            result_1,
                            child,
                            queue_1,
                            None,
                            preceding_siblings=preceding_siblings,
                            following_siblings=following_siblings
                        )
                    # If we were waiting for preceding_siblings, we break it off
                    # As we don't need to go further
                    if preceding_siblings:
                        break
                elif not central and preceding_siblings:
                    copyNode(sibling, parent=new_tree, children=True)
                elif central and following_siblings:
                    copyNode(sibling, parent=new_tree, children=True)
    else:
        result_1, loop = performXpath(parent, current_1)
        if loop is True:
            queue_1 = xpath1
            if xpath2 == xpath1:
                current_2, queue_2 = current_1, queue_1
            else:
                current_2, queue_2 = formatXpath(xpath2)
        else:
            current_2, queue_2 = formatXpath(xpath2)

        if xpath1 != xpath2:
            result_2, loop = performXpath(parent, current_2)
            if loop is True:
                queue_2 = xpath2
        else:
            result_2 = result_1

        if result_1 == result_2:
            has_no_queue = len(queue_1) == 0
            child = copyNode(result_1, children=has_no_queue, parent=new_tree)
            if not has_no_queue:
                passageLoop(
                    result_1,
                    child,
                    queue_1,
                    queue_2
                )
        else:
            start = False
            # For each sibling
            for sibling in xmliter(parent):
                # If we have found start
                # We copy the node because we are between start and end
                if start:
                    # If we are at the end
                    # We break the copy
                    if sibling == result_2:
                        break
                    else:
                        copyNode(sibling, parent=new_tree, children=True)
                # If this is start
                # Then we copy it and initiate star
                elif sibling == result_1:
                    start = True
                    has_no_queue_1 = len(queue_1) == 0
                    node = copyNode(sibling, children=has_no_queue_1, parent=new_tree)
                    if not has_no_queue_1:
                        passageLoop(sibling, node, queue_1, None, following_siblings=True)

            continue_loop = len(queue_2) == 0
            node = copyNode(result_2, children=continue_loop, parent=new_tree)
            if not continue_loop:
                passageLoop(result_2, node, queue_2, None, preceding_siblings=True)

    return new_tree


class OrderedDefaultDict(OrderedDict):
    def __init__(self, default_factory=None, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        val = self[key] = self.default_factory()
        return val


def nested_ordered_dictionary():
    return OrderedDefaultDict(nested_ordered_dictionary)


def nested_get(dictionary, keys):
    """ Get value in dictionary for dictionary[keys[0]][keys[1]][keys[..n]]

    :param dictionary: An input dictionary
    :param keys: Keys where to store data
    :return:
    """
    return reduce(lambda d, k: d[k], keys, dictionary)


def nested_set(dictionary,  keys, value):
    """ Set value in dictionary for dictionary[keys[0]][keys[1]][keys[..n]]

    :param dictionary: An input dictionary
    :param keys: Keys where to store data
    :param value: Value to set at keys** target
    :return: None
    """
    nested_get(dictionary, keys[:-1])[keys[-1]] = value


class Mimetypes:
    """ Mimetypes that can be used by different classes to refer to the same items

    :cvar JSON: JSON Resource mimetype
    :cvar XML: XML Resource mimetype
    :cvar CTS_XML: XML Resource mimetype
    :cvar MY_CAPYTAIN: MyCapytain Object Resource (Native Python CapiTainS Object)

    """
    JSON = "application/text"
    XML = "text/xml"
    CTS_XML = "text/xml:CTS"
    MY_CAPYTAIN = "MyCapytain"