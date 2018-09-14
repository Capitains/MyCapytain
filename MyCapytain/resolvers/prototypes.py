"""
.. module:: MyCapytain.resolvers.prototypes
   :synopsis: Resolver Prototype

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from typing import Tuple, Union, Optional, Dict, Any
from MyCapytain.resources.prototypes.metadata import Collection
from MyCapytain.resources.prototypes.text import TextualNode
from MyCapytain.common.reference import BaseReference, BaseReferenceSet


__all__ = [
    "Resolver"
]


class Resolver(object):
    """ Resolver provide a native python API which returns python objects.

    Initiation of resolvers are dependent on the implementation of the prototype

    """
    def getMetadata(self, objectId: str=None, **filters) -> Collection:
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
