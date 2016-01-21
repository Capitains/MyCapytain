# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resources.xml


Local files handler for CTS

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from collections import OrderedDict, defaultdict
from past.builtins import basestring
import warnings

from MyCapytain.errors import DuplicateReference, RefsDeclError
from MyCapytain.common.utils import xmlparser, NS
from MyCapytain.common.reference import URN, Citation, Reference
from MyCapytain.resources.proto import text
import MyCapytain.resources.texts.tei
from lxml import etree


class Text(text.Text):
    """ Implementation of CTS tools for local files

    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param citation: Highest Citation level
    :type citation: MyCapytain.common.reference.Citation
    :param autoreffs: Parse references on load (default : True)
    :type autoreffs: bool
    :ivar resource: lxml
    """

    def __init__(self, urn=None, citation=None, resource=None, autoreffs=True):
        super(Text, self).__init__(urn=urn, citation=citation)
        self._passages = OrderedDict()  # Represents real full passages / reffs informations. Only way to set it up is getValidReff without passage ?
        self._orphan = defaultdict(Reference)  # Represents passage we got without asking for all. Storing convenience ?

        self._cRefPattern = MyCapytain.resources.texts.tei.Citation()
        self.xml = None

        if citation is not None:
            self.citation = citation
        if resource is not None:
            self.resource = resource
            self.xml = xmlparser(resource)

            self.__findCRefPattern(self.xml)

            if autoreffs is True:
                self.parse()

    def __findCRefPattern(self, xml):
        """ Find CRefPattern in the text and set object.citation
        :param xml: Xml Resource
        :return: None
        """
        self.citation = MyCapytain.resources.texts.tei.Citation.ingest(
            resource=xml.xpath("//tei:refsDecl[@n='CTS']", namespaces=MyCapytain.common.utils.NS),
            xpath=".//tei:cRefPattern"
        )

    def parse(self):
        """ Parse the object and generate the children

        :return:
        """
        try:
            xml = self.xml.xpath(self.citation.scope, namespaces=NS)[0]
        except IndexError:
            msg = "Main citation scope does not result in any result ({0})".format(self.citation.scope)
            raise RefsDeclError(msg)
        except Exception as E:
            raise E

        self._passages = Passage(resource=xml, citation=self.citation, urn=self.urn, id=None)

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
            self._cRefPattern = MyCapytain.resources.texts.tei.Citation(
                name=value.name,
                refsDecl=value.refsDecl,
                child=value.child
            )

    def getPassage(self, reference, hypercontext=False):
        """ Finds a passage in the current text

        :param reference: Identifier of the subreference / passages
        :type reference: List, MyCapytain.common.reference.Reference
        :param hypercontext: If set to true, retrieves nodes up to the given one, cleaning non required siblings.
        :type hypercontext: bool
        :rtype: Passage
        :returns: Asked passage
        """
        if hypercontext is True:
            return self._getPassageContext(reference)

        if isinstance(reference, MyCapytain.common.reference.Reference):
            reference = reference["start_list"]

        reference = [".".join(reference[:i]) for i in range(1, len(reference) + 1)]
        passages = [self._passages]
        while len(reference) > 0:
            passages = [passage for sublist in [p.get(reference[0]) for p in passages] for passage in sublist]
            reference.pop(0)

        return passages[0]

    def _getPassageContext(self, reference):
        """ Retrieves nodes up to the given one, cleaning non required siblings.

        :param reference: Identifier of the subreference / passages
        :type reference: List, MyCapytain.common.reference.Reference
        :rtype: Passage
        :returns: Asked passage
        """
        if isinstance(reference, list):
            start, end = reference, reference
        elif len(reference["end_list"]) == 0 or isinstance(reference, list):
            start, end = reference["start_list"], reference["start_list"]
        else:
            start, end = reference["start_list"], reference["end_list"]

        if len(start) > len(self.citation):
            raise ReferenceError("URN is deeper than citation scheme")

        citation_start = [citation for citation in self.citation][len(start)-1]
        citation_end = [citation for citation in self.citation][len(end)-1]

        start, end = citation_start.fill(passage=start), citation_end.fill(passage=end)

        nodes = etree._ElementTree()

        start, end = start.split("/")[2:], end.split("/")[2:]

        root = self._copyNode(self.xml)
        nodes._setroot(root)
        root = self._passageLoop(self.xml, root, start, end)

        return root

    def _normalizeXpath(self, xpath):
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

    def _passageLoop(self, parent, new_tree, xpath1, xpath2=None, preceding_siblings=False, following_siblings=False):
        """

        :param parent: Parent on which to perform xpath
        :param new_tree: Parent on which to add nodes
        :param xpath: List of xpath elements
        :type xpath: [str]
        :return:
        """

        current_1, queue_1 = self._formatXpath(xpath1)
        if xpath2 is None:  # In case we need what is following or preceding our node
            result_1 = self._performXpath(parent, current_1)[0]
            siblings = list(parent)
            index_1 = siblings.index(result_1)
            children = len(queue_1) == 0
            if preceding_siblings:
                [
                    self._copyNode(child, parent=new_tree, children=True)
                    for child in siblings
                    if index_1 > siblings.index(child)
                ]
                child = self._copyNode(result_1, children=children, parent=new_tree)
            elif following_siblings:
                child = self._copyNode(result_1, children=children, parent=new_tree)
                [
                    self._copyNode(child, parent=new_tree, children=True)
                    for child in siblings
                    if index_1 < siblings.index(child)
                ]

            if not children:
                child = self._passageLoop(
                    result_1,
                    child,
                    queue_1,
                    None,
                    preceding_siblings=preceding_siblings,
                    following_siblings=following_siblings
                )
        else:
            current_2, queue_2 = self._formatXpath(xpath2)

            result_1 = self._performXpath(parent, current_1)

            if xpath1 != xpath2:
                result_2 = self._performXpath(parent, current_2)
                result_1 = result_1[0]
                result_2 = result_2[0]
            else:
                result_2 = result_1 = result_1[0]

            if result_1 == result_2:
                children = len(queue_1) == 0
                child = self._copyNode(result_1, children=children, parent=new_tree)
                if not children:
                    child = self._passageLoop(
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
                child_1 = self._copyNode(result_1, children=children_1, parent=new_tree)
                if not children_1:
                    self._passageLoop(result_1, child_1, queue_1, None, following_siblings=True)
                # Appends what's in between
                nodes = [
                    self._copyNode(child, parent=new_tree, children=True)
                    for child in children
                    if index_1 < children.index(child) < index_2
                ]
                # Appends the Ending passage
                children_2 = len(queue_1) == 0
                child_2 = self._copyNode(result_2, children=children_2, parent=new_tree)

                if not children_2:
                    self._passageLoop(result_2, child_2, queue_2, None, preceding_siblings=True)

        return new_tree

    def _formatXpath(self, xpath):
        if len(xpath) > 1:
            current, queue = xpath[0], xpath[1:]
            current = "./{}[./{}]".format(
                current,
                "/".join(queue)
            )
        else:
            current, queue = "./{}".format(xpath[0]), []

        return current, queue

    def _performXpath(self, parent, xpath):
        """

        :param parent:
        :param xpath:
        :return:
        """
        if xpath.startswith(".//"):
            result = parent.xpath(
                parent.replace(".//", "./"),
                namespaces=MyCapytain.common.utils.NS
            )
            if len(result) == 0:
                result = parent.xpath(
                    xpath,
                    namespaces=MyCapytain.common.utils.NS
                )
        else:
            result = parent.xpath(
                xpath,
                namespaces=MyCapytain.common.utils.NS
            )
        return result

    def _copyNode(self, node, children=False, parent=False):
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

    def getPassagePlus(self, reference):
        """ Finds a passage in the current text with its previous and following node

        :param reference: Identifier of the subreference / passages
        :type reference: List, MyCapytain.common.reference.Reference
        :rtype: text.PassagePlus
        :returns: Asked passage with metainformations
        """
        P = self.getPassage(reference=reference)
        return text.PassagePlus(P, P.prev.id, P.next.id)

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

        if reference is not None:
            start = len(reference[2])
            nodes = [".".join(reference[2][0:i+1]) for i in range(0, start)] + [None]
            if level <= start:
                level = start + 1
        else:
            nodes = [None for i in range(0, level)]

        passages = [self._passages]  # For consistency
        while len(nodes) >= 1:
            passages = [passage for sublist in [p.get(nodes[0]) for p in passages] for passage in sublist]
            nodes.pop(0)

        return [".".join(passage.id) for passage in passages]


class Passage(MyCapytain.resources.texts.tei.Passage):
    """ Passage representing object
    
    :param urn: A URN identifier
    :type urn: MyCapytain.common.reference.URN
    :param resource: A resource
    :type resource: lxml.etree._Element
    :param parent: Parent of the current passage
    :type parent: MyCapytain.resources.texts.tei.Passage
    :param citation: Citation for children level
    :type citation: MyCapytain.resources.texts.tei.Citation
    :param id: Identifier of the subreference without URN informations
    :type id: List

    .. note:: *id* is used in to identify the current passage in case the URN is unknown
    """

    def __init__(self, urn=None, resource=None, parent=None, citation=None, id=None):
        super(Passage, self).__init__(urn=urn, resource=resource, parent=parent)

        self.__next = False
        self.__prev = False

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
        """ Id represents the passage subreference as a list of basestring

        :rtype: list
        :returns: Representation of the passage subreference as a list
        """
        return self.__id

    @id.setter
    def id(self, value):
        """ Set up ID property

        :param value: Representation of the passage subreference as a list
        :type value: list

        .. note:: `Passage.id = [..]` will update automatically the URN property as well if correct
        """
        if isinstance(value, (list, tuple)):
            self.__id = value
            self.__updateURN()

    @property
    def urn(self):
        """ URN Identifier of the object

        :rtype: MyCapytain.common.reference.URN

        """
        return self._URN

    @urn.setter
    def urn(self, value):
        """ Set the urn

        :param value: URN to be saved
        :type value:  MyCapytain.common.reference.URN
        :raises: *TypeError* when the value is not URN compatible

        .. note:: `Passage.URN = ...` will update automatically the id property if Passage is set

        """
        a = self._URN
        if isinstance(value, basestring):
            value = MyCapytain.common.reference.URN(value)
        elif not isinstance(value, MyCapytain.common.reference.URN):
            raise TypeError()
        if str(a) != str(value):
            self._URN = value
            self.__updateURN()

    def __updateURN(self):
        """ Private method allowing for update of self.id or self.urn
        """
        if self.id is not None and len(self.id) > 0 and isinstance(self.urn, URN):
            self.urn = URN(self.urn["text"] + ":" + ".".join(self.id))
        elif self._URN is not None \
            and self._URN["reference"] is not None \
            and len(self._URN["reference"][2]) > 0 \
            and self.id != self._URN["reference"][2]:

            self.__id = self._URN["reference"][2]

    def get(self, key=None):
        """ Get a child or multiple children

        :param key: String identifying a passage
        :type key: basestring or int 
        :raises KeyError: When key identifies a child unknown to this passage
        :rtype: List.Passage
        :returns: List of passage identified by key. If key is None, returns all children
        
        .. note:: Call time depends on parsing status. If the passage was never parsed, then on first call citation is used to find children
        """
        if len(self.__children) == 0 and self.__parsed is False:
            self.__parse()

        if key is None:
            return [self.__children[key] for key in self.__children]
        elif isinstance(key, int):
            keys = list(self.__children.copy().keys())
            return [self.__children[keys[key]]]
        elif key not in self.__children:
            raise KeyError()
        else:
            return [self.__children[key]]

    def __parse(self):
        """ Private method for parsing children
        """
        if self.citation is None:
            self.__parsed = True
            return []

        elements = self.resource.xpath("."+self.citation.fill(passage=None, xpath=True), namespaces=NS)
        ids = [self.id+[element.get("n")] for element in elements]
        ns = [".".join(_id) for _id in ids]

        # Checking for duplicates
        duplicates = set([n for n in ns if ns.count(n) > 1])
        if len(duplicates) > 0:
            message = ", ".join(duplicates)
            warnings.warn(message, DuplicateReference)

        for element, _id, n in zip(elements, ids, ns):
            self.__children[n] = Passage(
                resource=element,
                citation=self.citation.child,
                id=_id,
                urn=self.urn,
                parent=self
            )
        self.__parsed = True

    @property
    def first(self):
        """ First child of current Passage 
        
        :rtype: None or Passage
        :returns: None if current Passage has no children,  first child passage if available
        """
        try:
            return self.get(0)[0]
        except:
            return None

    @property
    def last(self):
        """ Last child of current Passage 
        
        :rtype: None or Passage
        :returns: None if current Passage has no children, last child passage if available
        """
        try:
            return self.get(-1)[0]
        except :
            return None

    @property
    def children(self):
        """ Children of the passage

        :rtype: OrderedDict
        :returns: Dictionary of chidren, where key are subreferences
        """
        if len(self.__children) == 0 and self.__parsed is False:
            self.__parse()

        return self.__children
    
    @property
    def next(self):
        """ Next passage 

        :rtype: Passage
        :returns: Next passage at same level
        """ 
        if self.__next is False:

            if self.parent is None: # When top of hierarchy is access, should return None
                self.__next = None
                return None

            keys = list(self.parent.children.copy().keys())
            current = keys.index(".".join(self.id))
            if len(keys) - 1 > current:
                self.__next = self.parent.get(keys[current + 1])[0]
            else:
                n = self.parent.next
                if n is None:
                    self.__next = None
                else:
                    self.__next = n.first

        return self.__next

    @property
    def prev(self):
        """ Previous passage 

        :rtype: Passage
        :returns: Previous passage at same level
        """ 
        if self.__prev is False:

            if self.parent is None: # When top of hierarchy is access, should return None
                self.__prev = None
                return None

            keys = list(self.parent.children.copy().keys())
            current = keys.index(".".join(self.id))
            if current > 0:
                self.__prev = self.parent.get(keys[current - 1])[0]
            else:
                n = self.parent.prev
                if n is None:
                    self.__prev = None
                else:
                    self.__prev = n.last

        return self.__prev