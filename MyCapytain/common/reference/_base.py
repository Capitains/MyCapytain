from MyCapytain.common.base import Exportable
from MyCapytain.common.constants import get_graph, Mimetypes, RDF_NAMESPACES
from MyCapytain.errors import CitationDepthError
from copy import copy
from abc import abstractmethod


class BaseReference(tuple):
    def __new__(cls, start, end=None):
        obj = tuple.__new__(cls, (start, end))

        return obj

    def is_range(self):
        return bool(self[1])

    @property
    def start(self):
        """ Quick access property for start part

        :rtype: str
        """
        return self[0]

    @property
    def end(self):
        """ Quick access property for reference end list

        :rtype: str
        """
        return self[1]


class BaseReferenceSet(list):
    @property
    def citation(self):
        return self._citation

    def __new__(cls, *refs, citation=None):
        obj = list.__new__(cls, refs)
        obj._citation = None

        if citation:
            obj._citation = citation

        return obj


class BaseCitationSet(Exportable):
    """ A citation set is a collection of citations that optionnaly can be matched using a .match() function

    :param children: List of Citation
    :type children: [BaseCitation]
    """

    def __repr__(self):
        return "<MyCapytain.common.reference.BaseCitationSet object at %s>" % id(self)

    EXPORT_TO = [Mimetypes.JSON.DTS.Std]

    def __init__(self, children=None):
        self._children = []

        if children:
            self.children = children

    @property
    def children(self):
        """ Children of a citation

        :rtype: [BaseCitation]
        """
        return self._children or []

    @children.setter
    def children(self, val: list):
        final_value = []
        if val is not None:
            for citation in val:
                if citation is None:
                    continue
                elif not isinstance(citation, (BaseCitation, type(self))):
                    raise TypeError("Citation children should be Citation")
                else:
                    if isinstance(self, BaseCitation):
                        citation.root = self.root
                    else:
                        citation.root = self
                    final_value.append(citation)

        self._children = final_value

    def add_child(self, child):
        if isinstance(child, BaseCitation):
            self._children.append(child)

    def __iter__(self):
        """ Iteration method

        Loop over the citation children

        :Example:
            >>>    c = BaseCitationSet(name="line")
            >>>    b = BaseCitationSet(name="poem", children=[c])
            >>>    b2 = BaseCitationSet(name="paragraph")
            >>>    a = BaseCitationSet(name="book", children=[b])
            >>>    [e for e in a] == [a, b, c, b2],

        """
        for child in self.children:
            yield from child

    @abstractmethod
    def match(self, passageId):
        """ Given a specific passageId, matches the citation to a specific citation object

        :param passageId: Passage Identifier
        :return: Citation that matches the passageId
        :rtype: BaseCitation
        """

    @property
    def depth(self):
        """ Depth of the citation scheme

        .. example:: If we have a Book, Poem, Line system, and the citation we are looking at is Poem, depth is 1


        :rtype: int
        :return: Depth of the citation scheme
        """
        if len(self.children):
            return max([child.depth for child in self.children])
        else:
            return 0

    def __getitem__(self, item):
        """ Returns the citations at the given level.

        :param item: Citation level
        :type item: int
        :rtype: list(BaseCitation) or BaseCitation

        .. note:: Should it be a or or always a list ?
        """
        if item < 0:
            _item = self.depth + item
            if _item < 0:
                raise CitationDepthError("The negative %s is too small " % _item)
            item = _item
        if item == 0:
            yield from self.children
        else:
            for child in self.children:
                yield from child[item - 1]

    def __len__(self):
        """ Number of citation schemes covered by the object

        :rtype: int
        :returns: Number of nested citations
        """
        return len(self.children) + sum([len(child) for child in self.children])

    def __getstate__(self):
        """ Pickling method

        :return: dict
        """
        return copy(self.__dict__)

    def __setstate__(self, dic):
        self.__dict__ = dic
        return self

    def is_empty(self):
        """ Check if the citation has not been set

        :return: True if nothing was setup
        :rtype: bool
        """
        return len(self.children) == 0

    def is_root(self):
        return True

    def __export__(self, output=None, context=False, namespace_manager=None, **kwargs):
        if output == Mimetypes.JSON.DTS.Std:
            if not namespace_manager:
                namespace_manager = get_graph().namespace_manager

            _out = [
                cite.export(output, context=False, namespace_manager=namespace_manager)
                for cite in self.children
            ]

            if context:
                cite_structure_term = str(namespace_manager.qname(RDF_NAMESPACES.DTS.term("citeStructure")))
                _out = {
                    "@context": {
                        cite_structure_term.split(":")[0]: str(RDF_NAMESPACES.DTS)
                    },
                    cite_structure_term: _out
                }
            return _out


class BaseCitation(BaseCitationSet):
    def __repr__(self):
        """

        :return: String representation of the object
        :rtype: str
        """
        return "<{} name({})>".format(type(self).__name__, self.name)

    def __init__(self, name=None, children=None, root=None):
        """ Initialize a BaseCitation object

        :param name: Name of the citation level
        :type name: str
        :param children: list of children
        :type children: [BaseCitation]
        :param root: Root of the citation group
        :type root: BaseCitationSet
        """
        super(BaseCitation, self).__init__()

        self._name = None
        self._root = None

        self.name = name
        self.children = children
        self.root = root

    def is_root(self):
        """
        :return: If the current object is the root of the citation set, True
        :rtype: bool
        """
        return self._root is None

    def is_set(self):
        """ Checks that the current object is set

        :rtype: bool
        """
        return self.name is not None

    @property
    def root(self):
        """ Returns the root of the citation set

        :return: Root of the Citation set
        :rtype: BaseCitationSet
        """
        if self._root is None:
            return self
        return self._root

    @root.setter
    def root(self, value):
        """ Set the root to which the current citation is connected to

        :param value: CitationSet root of the Citation graph
        :type value: BaseCitationSet
        :return:
        """
        self._root = value

    @property
    def name(self):
        """ Type of the citation represented

        :rtype: str
        :example: Book, Chapter, Textpart, Section, Poem...
        """
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    def __iter__(self):
        """ Iteration method

        Loop over the citation children

        :Example:
            >>>    c = BaseCitation(name="line")
            >>>    b = BaseCitation(name="poem", children=[c])
            >>>    b2 = BaseCitation(name="paragraph")
            >>>    a = BaseCitation(name="book", children=[b])
            >>>    [e for e in a] == [a, b, c, b2],

        """
        yield from [self]
        for child in self.children:
            yield from child

    def __export__(self, output=None, context=False, namespace_manager=None, **kwargs):
        if output == Mimetypes.JSON.DTS.Std:
            if not namespace_manager:
                namespace_manager = get_graph().namespace_manager

            cite_type_term = str(namespace_manager.qname(RDF_NAMESPACES.DTS.term("citeType")))
            cite_structure_term = str(namespace_manager.qname(RDF_NAMESPACES.DTS.term("citeStructure")))

            _out = {
                cite_type_term: self.name
            }

            if not self.is_empty():
                _out[cite_structure_term] = [
                    cite.export(output, context=False, namespace_manager=namespace_manager)
                    for cite in self.children
                ]

            if context:
                _out["@context"] = {cite_type_term.split(":")[0]: str(RDF_NAMESPACES.DTS)}

            return _out

    @property
    def depth(self):
        """ Depth of the citation scheme

        .. example:: If we have a Book, Poem, Line system, and the citation we are looking at is Poem, depth is 1


        :rtype: int
        :return: Depth of the citation scheme
        """
        if len(self.children):
            return 1 + max([child.depth for child in self.children])
        else:
            return 1


class NodeId(object):
    """ Collection of directional references for a Tree

    :param identifier: Current object identifier
    :type identifier: str
    :param children: Current node Children's Identifier
    :type children: [str]
    :param parent: Parent of the current node
    :type parent: str
    :param siblings: Previous and next node of the current node
    :type siblings: str
    :param depth: Depth of the node in the global hierarchy of the text tree
    :type depth: int
    """
    def __init__(self, identifier=None, children=None, parent=None, siblings=(None, None), depth=None):
        self.__children__ = children or []
        self.__parent__ = parent
        self.__prev__, self.__nextId__ = siblings
        self.__identifier__ = identifier
        self.__depth__ = depth

    @property
    def depth(self):
        """ Depth of the node in the global hierarchy of the text tree

        :rtype: int
        """
        return self.__depth__

    @property
    def childIds(self):
        """ Children Node

        :rtype: [str]
        """
        return self.__children__

    @property
    def firstId(self):
        """ First child Node

        :rtype: str
        """
        if len(self.__children__) == 0:
            return None
        return self.__children__[0]

    @property
    def lastId(self):
        """ Last child Node

        :rtype: str
        """
        if len(self.__children__) == 0:
            return None
        return self.__children__[-1]

    @property
    def parentId(self):
        """ Parent Node

        :rtype: str
        """
        return self.__parent__

    @property
    def siblingsId(self):
        """ Siblings Node

        :rtype: (str, str)
        """
        return self.__prev__, self.__nextId__

    @property
    def prevId(self):
        """ Previous Node (Sibling)

        :rtype: str
        """
        return self.__prev__

    @property
    def nextId(self):
        """ Next Node (Sibling)

        :rtype: str
        """
        return self.__nextId__

    @property
    def id(self):
        """Current object identifier

        :rtype: str
        """
        return self.__identifier__
