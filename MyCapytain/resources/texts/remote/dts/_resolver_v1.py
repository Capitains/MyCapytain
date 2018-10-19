from typing import TYPE_CHECKING, Optional
from MyCapytain.resources.prototypes.text import InteractiveTextualNode
from MyCapytain.common.reference import BaseReference
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.common.utils import parse_pagination
from MyCapytain.resources.texts.base.tei import TeiResource

if TYPE_CHECKING:  # Required for nice and beautiful type checking
    from requests import Response
    from lxml.etree import ElementTree
    from MyCapytain.resolvers.dts.api_v1 import HttpDtsResolver


class DtsResolverDocument(TeiResource):
    def __init__(
            self,
            identifier: str,
            resolver: "HttpDtsResolver",
            resource: "ElementTree",
            reference: Optional[BaseReference]=None,
            **kwargs
    ):
        super(DtsResolverDocument, self).__init__(identifier=identifier, resource=resource, **kwargs)
        self._resolver = resolver
        self._reference = reference
        self._resource = resource

        self._parent = None
        self._prev_id, self._next_id = None, None

    @property
    def resolver(self) -> "HttpDtsResolver":
        return self._resolver

    def getTextualNode(self, subreference: BaseReference) -> "DtsResolverPassage":
        return self.resolver.getTextualNode(textId=self.id, subreference=subreference)

    def getReffs(self, level: int=1, subreference: BaseReference=None):
        return self.resolver.getReffs(textId=self.id, subreference=(subreference or self.reference))

    @classmethod
    def parse(cls, identifier: str, reference: BaseReference, resolver: "HttpDtsResolver", response: "Response"):
        o = cls(
            identifier=identifier,
            reference=reference,
            resolver=resolver,
            resource=xmlparser(response.text)
        )
        nav = parse_pagination(response.headers)
        print(nav)

        return o

    @property
    def reference(self) -> BaseReference:
        return self._reference