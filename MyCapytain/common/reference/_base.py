from MyCapytain.common.base import Exportable
from MyCapytain.common.constants import get_graph, Mimetypes, RDF_NAMESPACES
from MyCapytain.errors import CitationDepthError
from copy import copy
from typing import Tuple
from abc import abstractmethod


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
        """ Sets children

        :param val: List of citation children
        """
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
        """ Adds a child to the CitationSet

        :param child: Child citation to add
        :return:
        """
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
        """ Depth of the citation scheme: if multiple scheme are available,
        the deepest one from the current node is chosen (if there is two possibilities,
        a->((b->c)(d->e->f)) 4 is the depth

        .. example:: If we have a Book, Poem, Line system,
         and the citation we are looking at is Poem, depth is 2


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

    def is_empty(self) -> bool:
        """ Check if the citation has not been set

        :return: True if nothing was setup
        :rtype: bool
        """
        return len(self.children) == 0

    def is_root(self) -> bool:
        """ Check if the Citation is the root

        :return:
        """
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

    def __init__(self, name: str=None, children: list=None, root: BaseCitationSet=None):
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

    def is_root(self) -> str:
        """
        :return: If the current object is the root of the citation set, True
        :rtype: bool
        """
        return self._root is None

    def is_set(self) -> bool:
        """ Checks that the current object is set

        :rtype: bool
        """
        return self.name is not None

    @property
    def root(self) -> BaseCitationSet:
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
    def name(self) -> str:
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
    def depth(self) -> int:
        """ Depth of the citation scheme

        .. example:: If we have a Book, Poem, Line system, and the citation we are looking at is Poem, depth is 1


        :rtype: int
        :return: Depth of the citation scheme
        """
        if len(self.children):
            return 1 + max([child.depth for child in self.children])
        else:
            return 1


class BaseReference(tuple):
    """ BaseReference represents a passage identifier, range or not

    It is made of two major properties : .start and .end

    To check if the object is a range, you can use the method .is_range()
    """
    def __new__(cls, *refs):
        if len(refs) == 1 and not isinstance(refs[0], tuple):
            refs = refs[0], None

        obj = tuple.__new__(cls, refs)

        return obj

    def is_range(self) -> int:
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


class BaseReferenceSet(tuple):
    """ A BaseReferenceSet is a set of Reference (= a bag of identifier)
    that can carry citation and level information (what kind of reference is this reference ?
    Where am I in the levels of the current document ?)

    It can be iterate like a tuple and has a .citation and .level property

    """
    def __new__(cls, *refs, citation: BaseCitationSet=None, level: int=1):
        if len(refs) == 1 and not isinstance(refs, BaseReference):
            refs = refs[0]
        obj = tuple.__new__(cls, refs)
        obj._citation = None
        obj._level = level

        if citation is not None:
            obj._citation = citation
        return obj

    @property
    def citation(self) -> BaseCitationSet:
        return self._citation

    @property
    def level(self) -> int:
        """ Level represents the depth at which lies the reference.

        eg. depth is the number of floors, level is the actual floor number.
        """
        return self._level

    def __repr__(self):
        return "<{typ} ({repr}) level:{level}, citation:{citation}>".format(
            typ=type(self).__name__,
            repr=", ".join([str(s) for s in self]),
            level=self.level,
            citation=str(self.citation)
        )


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
        self._children = children or []
        self._parent = parent
        self._prev_id, self._next_id = siblings
        self._identifier = identifier
        self._depth = depth

    @property
    def depth(self) -> int:
        """ Depth of the node in the global hierarchy of the text tree
        """
        return self._depth

    @property
    def childIds(self) -> BaseReferenceSet:
        """ Children Ids
        """
        return self._children

    @property
    def firstId(self) -> BaseReference:
        """ First child Id
        """
        if len(self._children) == 0:
            return None
        return self._children[0]

    @property
    def lastId(self) -> BaseReference:
        """ Last child id
        """
        if len(self._children) == 0:
            return None
        return self._children[-1]

    @property
    def parentId(self) -> BaseReference:
        """ Parent Id
        """
        return self._parent

    @property
    def siblingsId(self) -> Tuple[BaseReference, BaseReference]:
        """ Siblings Id
        """
        return self.prevId, self.nextId

    @property
    def prevId(self) -> BaseReference:
        """ Previous Id (Sibling)
        """
        return self._prev_id

    @property
    def nextId(self) -> BaseReference:
        """ Next Id
        """
        return self._next_id

    @property
    def id(self):
        """Current object identifier

        :rtype: str
        """
        return self._identifier
