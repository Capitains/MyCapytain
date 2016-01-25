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
from MyCapytain.common.utils import xmlparser, NS, copyNode, passageLoop, normalizeXpath
from MyCapytain.common.reference import URN, Citation, Reference
from MyCapytain.resources.proto import text
from MyCapytain.errors import InvalidSiblingRequest
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
        self._passages = Passage()
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

        self._passages = Passage(resource=xml, citation=self.citation, urn=self.urn, reference=None)

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

    def getPassage(self, reference, hypercontext=True):
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

        if isinstance(reference, Reference):
            reference = reference.start

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
            reference = Reference(".".join(reference))
        elif len(reference.end) == 0 or isinstance(reference, list):
            start, end = reference.start, reference.start
        else:
            start, end = reference.start, reference.end

        if len(start) > len(self.citation):
            raise ReferenceError("URN is deeper than citation scheme")

        citation_start = [citation for citation in self.citation][len(start)-1]
        citation_end = [citation for citation in self.citation][len(end)-1]

        start, end = citation_start.fill(passage=start), citation_end.fill(passage=end)

        nodes = etree._ElementTree()

        start, end = normalizeXpath(start.split("/")[2:]), normalizeXpath(end.split("/")[2:])

        root = copyNode(self.xml)
        nodes._setroot(root)
        root = passageLoop(self.xml, root, start, end)

        if self.urn:
            urn, reeference = URN("{}:{}".format(self.urn, reference)), reference
        else:
            urn, reference = None, reference
        return ContextPassage(
            urn=urn,
            resource=root, parent=self, citation=self.citation
        )

    def getPassagePlus(self, reference, hypercontext=False):
        """ Finds a passage in the current text with its previous and following node

        :param reference: Identifier of the subreference / passages
        :type reference: List, MyCapytain.common.reference.Reference
        :rtype: text.PassagePlus
        :returns: Asked passage with metainformations
        """
        P = self.getPassage(reference=reference, hypercontext=hypercontext)
        return text.PassagePlus(P, P.prev.reference, P.next.reference)

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

        return [passage.reference for passage in passages]

    def text(self, exclude=None):
        return self._passages.text(exclude=exclude)


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
    :param reference: Identifier of the subreference without URN informations
    :type reference: List

    .. note:: *id* is used in to identify the current passage in case the URN is unknown
    """

    def __init__(self, urn=None, resource=None, parent=None, citation=None, reference=None):
        super(Passage, self).__init__(resource=resource, parent=parent)

        self.__next = False
        self.__prev = False

        self.citation = None
        if isinstance(citation, Citation):
            self.citation = citation

        self.__reference = Reference("")
        if urn:
            self.urn = urn
        if reference:
            self.reference = reference

        self.__children = OrderedDict()
        self.__parsed = False

    @property
    def reference(self):
        """ Id represents the passage subreference as a list of basestring

        :rtype: list
        :returns: Representation of the passage subreference as a list
        """
        return self.__reference

    @reference.setter
    def reference(self, value):
        """ Set up ID property

        :param value: Representation of the passage subreference as a list
        :type value: list

        .. note:: `Passage.id = [..]` will update automatically the URN property as well if correct
        """
        _value = None
        if isinstance(value, (list, tuple)):
            _value = Reference(".".join(value))
        elif isinstance(value, str):
            _value = Reference(value)
        elif isinstance(value, Reference):
            _value = value

        if _value and self.__reference != _value:
            self.__reference = _value
            if self._URN and len(self._URN):
                if len(value):
                    self._URN = URN("{}:{}".format(self._URN["text"], str(_value)))
                else:
                    self._URN = URN(self._URN["text"])

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
            value = URN(value)
        elif not isinstance(value, URN):
            raise TypeError()

        if str(a) != str(value):
            self._URN = value

            if value.reference and self.__reference != value.reference:
                self.__reference = value.reference
            elif not value.reference and self.__reference and len(self.__reference):
                self._URN = URN("{}:{}".format(str(value), str(self.__reference)))

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
        ids = [self.reference["start_list"]+[element.get("n")] for element in elements]
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
                reference=_id,
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

            if self.parent is None:  # When top of hierarchy is access, should return None
                self.__next = None
                return None

            keys = list(self.parent.children.copy().keys())
            current = keys.index(str(self.reference))
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

            if self.parent is None:  # When top of hierarchy is access, should return None
                self.__prev = None
                return None

            keys = list(self.parent.children.copy().keys())
            current = keys.index(str(self.reference))
            if current > 0:
                self.__prev = self.parent.get(keys[current - 1])[0]
            else:
                n = self.parent.prev
                if n is None:
                    self.__prev = None
                else:
                    self.__prev = n.last

        return self.__prev


class ContextPassage(Passage):
    """ Range / Tree Passage object """
    def __init__(self, urn=None, resource=None, parent=None, citation=None, reference=None):
        """

        :param urn:
        :param resource:
        :param parent: Text object
        :param citation:
        :param reference:
        :return:
        """
        super(ContextPassage, self).__init__(urn=urn, reference=reference)

        self.resource = resource
        self.parent = parent
        self.citation = parent.citation

        self.depth = self.depth_2 = 1

        if self.reference.start:
            self.depth_2 = self.depth = len(self.reference.start)
        if self.reference and self.reference.end:
            self.depth_2 = len(self.reference.end)

    def xpath(self, *args, **kwargs):
        return self.resource.xpath(*args, **kwargs)

    def tostring(self, *args, **kwargs):
        return etree.tostring(self.resource, *args, **kwargs)

    def get(self, key=None):
        """ Get a child or multiple children

        :param key: String identifying a passage
        :type key: basestring or int
        :raises KeyError: When key identifies a child unknown to this passage
        :rtype: List.Passage
        :returns: List of passage identified by key. If key is None, returns all children

        .. note:: Call time depends on parsing status. If the passage was never parsed, then on first call citation is
            used to find children
        """
        pass

    @property
    def first(self):
        """ First child of current Passage

        :rtype: None or Passage
        :returns: None if current Passage has no children,  first child passage if available
        """
        if self.depth >= len(self.citation):
            return None
        else:
            return ""

    @property
    def last(self):
        """ Last child of current Passage

        :rtype: None or Passage
        :returns: None if current Passage has no children, last child passage if available
        """
        if self.depth >= len(self.citation):
            return None
        else:
            return ""

    @property
    def children(self):
        """ Children of the passage

        :rtype: OrderedDict
        :returns: Dictionary of chidren, where key are subreferences
        """
        if self.depth >= len(self.citation):
            return None
        else:
            return ""

    @property
    def next(self):
        """ Next passage

        :rtype: Passage
        :returns: Next passage at same level
        """
        if self.depth != self.depth_2:
            raise InvalidSiblingRequest()

    @property
    def prev(self):
        """ Previous passage

        :rtype: Passage
        :returns: Previous passage at same level
        """
        if self.depth != self.depth_2:
            raise InvalidSiblingRequest()

    def __getSiblings(self):
        """

        :return: List of references
        """
        document_references = self.parent.getValidReff(level=self.depth)
        passage_references = self.resource.getValidReff(level=self.depth)
        return len(passage_references), document_references
