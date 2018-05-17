from MyCapytain.common.base import Exportable
from copy import copy
from abc import abstractmethod, abstractproperty


class BasePassageId:
    def __init__(self, start=None, end=None):
        self._start = start
        self._end = end

    @property
    def is_range(self):
        return self._end is not None

    @property
    def start(self):
        """ Quick access property for start part

        :rtype: str
        """
        return self._start

    @property
    def end(self):
        """ Quick access property for reference end list

        :rtype: str
        """
        return self._end


class CitationSet:
    """ A citation set is a collection of citations that can be matched using
    a .match() function

    """
    @abstractmethod
    def match(self, passageId):
        """ Given a specific passageId, matches the citation to a specific citation object

        :param passageId: Passage Identifier
        :return: Citation that matches the passageId
        :rtype: BaseCitation
        """


class BaseCitation(Exportable, CitationSet):
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
        :type root: CitationSet
        """
        super(BaseCitation, self).__init__()

        self._name = None
        self._children = []
        self._root = root

        self.name = name
        self.children = children

    @property
    def is_root(self):
        """
        :return: If the current object is the root of the citation set, True
        :rtype: bool
        """
        return self._root is None

    @property
    def root(self):
        """ Returns the root of the citation set

        :return: Root of the Citation set
        :rtype: CitationSet
        """
        return self._root

    @root.setter
    def root(self, value):
        """ Set the root to which the current citation is connected to

        :param value: CitationSet root of the Citation graph
        :type value: CitationSet
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

    @property
    def children(self):
        """ Children of a citation

        :rtype: [BaseCitation]
        """
        return self._children or []

    @children.setter
    def children(self, val):
        final_value = []
        if val is not None:
            for citation in val:
                if citation is None:
                    continue
                elif not isinstance(citation, self.__class__):
                    raise TypeError("Citation children should be Citation")
                else:
                    citation.root = self.root
                    final_value.append(citation)

        self._children = final_value

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

    @property
    @abstractmethod
    def depth(self):
        """ Depth of the citation scheme

        .. example:: If we have a Book, Poem, Line system, and the citation we are looking at is Poem, depth is 2

        :rtype: int
        :return: Depth of the citation scheme
        """
        return 1

    @abstractmethod
    def __getitem__(self, item):
        """ Returns the citations at the given level.

        :param item: Citation level
        :type item: int
        :rtype: list(BaseCitation) or BaseCitation

        .. note:: Should it be a or or always a list ?
        """
        return []

    def __len__(self):
        """ Number of citation schemes covered by the object

        :rtype: int
        :returns: Number of nested citations
        """
        return 0

    def __getstate__(self):
        """ Pickling method

        :return: dict
        """
        return copy(self.__dict__)

    def __setstate__(self, dic):
        self.__dict__ = dic
        return self

    @abstractmethod
    def isEmpty(self):
        """ Check if the citation has not been set

        :return: True if nothing was setup
        :rtype: bool
        """
        return True


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