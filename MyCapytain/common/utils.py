# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.reference
   :synopsis: Common useful tools and constants

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals

import re
from collections import OrderedDict, defaultdict
from copy import copy
from functools import reduce
from io import IOBase, StringIO

from lxml import etree
from lxml.objectify import ObjectifiedElement, parse, SubElement, Element
from six import text_type
from xml.sax.saxutils import escape
from rdflib import BNode, Graph, Literal, URIRef

from MyCapytain.common.constants import XPATH_NAMESPACES

__strip = re.compile("([ ]{2,})+")
__parser__ = etree.XMLParser(collect_ids=False, resolve_entities=False)


def make_xml_node(graph, name, close=False, attributes=None, text="", complete=False, innerXML=""):
    """ Create an XML Node

    :param graph: Graph used to geneates prefixes
    :param name: Name of the tag
    :param close: Produce closing tag (close=False -> "<tag>", close=True -> "</tag>")
    :param attributes: Dictionary of attributes
    :param text: CapitainsCtsText to put inside the node
    :param complete: Complete node (node with opening and closing tag)
    :param innerXML: XML to append to the node
    :return: String representation of the node
    :rtype: str
    """
    name = graph.namespace_manager.qname(name)
    if complete:
        if attributes is not None:
            return "<{0} {1}>{2}{3}</{0}>".format(
                name,
                " ".join(
                    [
                        "{}=\"{}\"".format(attr_name, attr_value)
                        for attr_name, attr_value in attributes.items()
                    ]
                ),
                escape(text),
                innerXML
            )
        return "<{0}>{1}{2}</{0}>".format(name, escape(text), innerXML)
    elif close is True:
        return "</{}>".format(name)
    elif attributes is not None:
        return "<{} {}>".format(
            name,
            " ".join(
                [
                    "{}=\"{}\"".format(attr_name, attr_value)
                    for attr_name, attr_value in attributes.items()
                ]
            )
        )
    return "<{}>".format(name)


def LiteralToDict(value):
    """ Transform an object value into a dict readable value

    :param value: Object of a triple which is not a BNode
    :type value: Literal or URIRef
    :return: dict or str or list
    """
    if isinstance(value, Literal):
        if value.language is not None:
            return {"@value": str(value), "@lang": value.language}
        return value.toPython()
    elif isinstance(value, URIRef):
        return {"@id": str(value)}
    elif value is None:
        return None
    return str(value)


class Subgraph(object):
    """ Utility class to generate subgraph around one or more items

    :param
    """
    def __init__(self, namespace_manager):
        self.graph = Graph()
        self.graph.namespace_manager = namespace_manager
        self.downwards = defaultdict(lambda: True)
        self.updwards = defaultdict(lambda: True)

    def graphiter(self, graph, target, ascendants=0, descendants=1):
        """ Iter on a graph to finds object connected

        :param graph: Graph to serialize
        :type graph: Graph
        :param target: Node to iterate over
        :type target: Node
        :param ascendants: Number of level to iter over upwards (-1 = No Limit)
        :param descendants: Number of level to iter over downwards (-1 = No limit)
        :return:
        """

        asc = 0 + ascendants
        if asc != 0:
            asc -= 1

        desc = 0 + descendants
        if desc != 0:
            desc -= 1

        t = str(target)

        if descendants != 0 and self.downwards[t] is True:
            self.downwards[t] = False
            for pred, obj in graph.predicate_objects(target):
                if desc == 0 and isinstance(obj, BNode):
                    continue
                self.add((target, pred, obj))

                # Retrieve triples about the object
                if desc != 0 and self.downwards[str(obj)] is True:
                    self.graphiter(graph, target=obj, ascendants=0, descendants=desc)

        if ascendants != 0 and self.updwards[t] is True:
            self.updwards[t] = False
            for s, p in graph.subject_predicates(object=target):
                if desc == 0 and isinstance(s, BNode):
                    continue
                self.add((s, p, target))

                # Retrieve triples about the parent as object
                if asc != 0 and self.updwards[str(s)] is True:
                    self.graphiter(graph, target=s, ascendants=asc, descendants=0)

    def serialize(self, *args, **kwargs):
        return self.graph.serialize(*args, **kwargs)

    def add(self, *args, **kwargs):
        self.graph.add(*args, **kwargs)


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
    :type string: text_type
    :rtype: text_type
    :returns: Clean string
    """
    return __strip.sub(" ", string)

#: Dictionary of namespace that can be useful

#: Dictionary of RDF Prefixes

#: Mapping of known domains to RDF Classical Prefixes


def xmlparser(xml, objectify=True):
    """ Parse xml

    :param xml: XML element
    :type xml: Union[text_type, lxml.etree._Element]
    :rtype: lxml.etree._Element
    :returns: An element object
    :raises: TypeError if element is not in accepted type

    """
    doclose = None
    if isinstance(xml, (etree._Element, ObjectifiedElement, etree._ElementTree)):
        return xml
    elif isinstance(xml, text_type):
        xml = StringIO(xml)
        doclose = True
    elif not isinstance(xml, IOBase):
        raise TypeError("Unsupported type of resource {}".format(type(xml)))

    if objectify is False:
        parsed = etree.parse(xml).getroot()
    else:
        parsed = parse(xml).getroot()
    if doclose:
        xml.close()
    return parsed


def __formatXpath__(xpath):
    """ Format at XPath for perform XPath

    :param xpath: XPath element lists
    :return: Tuple where the first element is an XPath representing the next node to retrieve and the second the list \
    of other elements to find
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
            namespaces=XPATH_NAMESPACES
        )
        if len(result) == 0:
            result = parent.xpath(
                "*[{}]".format(xpath),
                namespaces=XPATH_NAMESPACES
            )
            loop = True
    else:
        result = parent.xpath(
            xpath,
            namespaces=XPATH_NAMESPACES
        )
    return result[0], loop


def copyNode(node, children=False, parent=False):
    """ Copy an XML Node

    :param node: Etree Node
    :param children: Copy children nodes is set to True
    :param parent: Append copied node to parent if given
    :return: New Element
    """
    if parent is not False:
        element = SubElement(
            parent,
            node.tag,
            attrib=node.attrib,
            nsmap={None: "http://www.tei-c.org/ns/1.0"}
        )
    else:
        element = Element(
            node.tag,
            attrib=node.attrib,
            nsmap={None: "http://www.tei-c.org/ns/1.0"}
        )
    if children:
        if node.text:
            element._setText(node.text)
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
    current_1, queue_1 = __formatXpath__(xpath1)
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
                current_2, queue_2 = __formatXpath__(xpath2)
        else:
            current_2, queue_2 = __formatXpath__(xpath2)

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
    """ Extension of Default Dict that makes an OrderedDefaultDict

    :param default_factory__: Default class to initiate
    """

    def __init__(self, default_factory=None, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        val = self[key] = self.default_factory()
        return val


def nested_ordered_dictionary():
    """ Helper to create a nested ordered default dictionary

    :rtype OrderedDefaultDict:
    :return: Nested Ordered Default Dictionary instance
    """
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


def expand_namespace(nsmap, string):
    """ If the string starts with a known prefix in nsmap, replace it by full URI

    :param nsmap: Dictionary of prefix -> uri of namespace
    :param string: String in which to replace the namespace
    :return: Expanded string with no namespace
    """
    for ns in nsmap:
        if isinstance(string, str) and isinstance(ns, str) and string.startswith(ns+":"):
            return string.replace(ns+":", nsmap[ns])
    return string