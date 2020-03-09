"""
.. module:: MyCapytain.resolvers.prototypes
   :synopsis: Resolver Prototype

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from typing import Tuple, Union, Optional, Dict, Any, Set
from MyCapytain.resources.prototypes.text import TextualNode
from MyCapytain.common.reference import BaseReference, BaseReferenceSet
from collections import defaultdict


__all__ = [
    "Resolver"
]


class Resolver(object):
    """ Resolver provide a native python API which returns python objects.

    Initiation of resolvers are dependent on the implementation of the prototype

    """
    def __init__(self):
        """
        :ivar _id_to_coll: maps a collection id to that collection's object
        :type _id_to_coll: {str: Collection}
        :ivar _parents: maps a child id to the ids of its direct parents
        :type _parents: {str: {str}}
        :ivar _children: maps a parent id to the ids of its direct descendants, i.e., its children
        :type _children: {str: {str}}

        """
        self._id_to_coll = dict()
        self._parents = defaultdict(set)
        self._children = defaultdict(set)

    @property
    def id_to_coll(self) -> Dict[str, Any]:
        """ Returns a mapping from collection's id to its Collection object"""
        return self._id_to_coll

    def add_collection(self, id: str, collection: Any):
        """ Adds an id to coll mapping to self._id_to_coll"""
        if not isinstance(id, str):
            id = str(id)
        self._id_to_coll.update({id: collection})

    @property
    def parents(self) -> Dict[str, Set[str]]:
        """ Returns a mapping from a collection's id to the ids of its direct parents"""
        return self._parents

    def add_parent(self, collection_id: str, parent_id: str):
        """ Adds a parent id to the set of a collection's parents"""
        if not isinstance(collection_id, str):
            collection_id = str(collection_id)
        if not isinstance(parent_id, str):
            parent_id = str(parent_id)
        self._parents[collection_id].add(parent_id)
        self.add_child(parent_id, collection_id)

    @property
    def children(self) -> Dict[str, Set[str]]:
        """ Returns a mapping from a collection's id to the ids of its direct children"""
        return self._children

    def add_child(self, collection_id: str, child_id: str):
        """ Adds a child id to the set of a collection's children"""
        if not isinstance(collection_id, str):
            collection_id = str(collection_id)
        if not isinstance(child_id, str):
            child_id = str(child_id)
        self._children[collection_id].add(child_id)

    @property
    def texts(self) -> Dict[str, Any]:
        """ returns all readable texts

        :return: Readable descendants
        :rtype: {str: CapitainsReadableMetadata}
        """
        # Changed to a dictionary to match with the return type for XmlCapitainsCollectionMetadata.texts
        texts = {}
        for s in self.children.values():
            for v in s:
                c = self.id_to_coll[v]
                if c.readable:
                    texts[v] = c
        return texts

    def getMetadata(self, objectId: str=None, **filters) -> Any:
        """ Request metadata about a text or a collection

        :param objectId: Object Identifier to filter on
        :type objectId: str
        :param filters: Kwargs parameters.
        :type filters: dict
        :return: Collection
        """
        raise NotImplementedError()

    def getTextualNode(
            self,
            textId: str,
            subreference: Union[str, BaseReference]=None,
            prevnext: bool=False,
            metadata: bool=False
    ) -> TextualNode:
        """ Retrieve a text node from the API

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :param prevnext: Retrieve graph representing previous and next passage
        :type prevnext: boolean
        :param metadata: Retrieve metadata about the passage and the text
        :type metadata: boolean
        :return: CapitainsCtsPassage
        :rtype: CapitainsCtsPassage
        """
        raise NotImplementedError()

    def getSiblings(self, textId: str, subreference: Union[str, BaseReference]) -> Tuple[BaseReference, BaseReference]:
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :return: Tuple of references
        :rtype: (str, str)
        """
        raise NotImplementedError()

    def getReffs(
            self,
            textId: str,
            level: int=1,
            subreference: Union[str, BaseReference]=None,
            include_descendants: bool=False,
            additional_parameters: Optional[Dict[str, Any]]=None
    ) -> BaseReferenceSet:
        """ Retrieve the siblings of a textual node

        :param textId: CtsTextMetadata Identifier
        :type textId: str
        :param level: Depth for retrieval
        :type level: int
        :param subreference: CapitainsCtsPassage Reference
        :type subreference: str
        :param include_descendants:
        :param additional_parameters:
        :return: List of references
        :rtype: [str]

        ..toDo :: This starts to be a bloated function....
        """
        raise NotImplementedError()
