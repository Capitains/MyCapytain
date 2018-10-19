from typing import TYPE_CHECKING
from MyCapytain.resources.prototypes.text import InteractiveTextualNode
from MyCapytain.common.reference import BaseReference

if TYPE_CHECKING:  # Required for nice and beautiful type checking
    from MyCapytain.resolvers.dts.api_v1 import HttpDtsResolver


class DtsResolverText(InteractiveTextualNode):
    def __init__(self, identifier: str, resolver: "HttpDtsResolver", resource: str, **kwargs):
        super(InteractiveTextualNode, self).__init__(identifier=identifier, **kwargs)
        self._resolver = resolver
        self._resource = resource

    @property
    def resolver(self) -> "HttpDtsResolver":
        return self._resolver

    def getTextualNode(self, subreference: BaseReference) -> "DtsResolverPassage":
        return self.resolver.getTextualNode(textId=self.id, subreference=subreference)




class DtsResolverPassage(DtsResolverText):
    def __init__(self, identifier: str, reference: BaseReference, resolver: "HttpDtsResolver", **kwargs):
        super(DtsResolverPassage, self).__init__(identifier=identifier, resolver=resolver, **kwargs)
        self._reference = reference

    @property
    def reference(self) -> BaseReference:
        return self._reference
