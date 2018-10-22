from typing import TYPE_CHECKING, Optional
import link_header
from urllib.parse import parse_qs, urlparse

from MyCapytain.common.reference import BaseReference, DtsReference
from MyCapytain.common.utils.xml import xmlparser
from MyCapytain.resources.texts.base.tei import TeiResource


if TYPE_CHECKING:  # Required for nice and beautiful type checking
    from requests import Response
    from lxml.etree import ElementTree
    from MyCapytain.resolvers.dts.api_v1 import HttpDtsResolver
    from MyCapytain.resources.collections.dts import HttpResolverDtsCollection


class DtsResolverDocument(TeiResource):
    def __init__(
            self,
            identifier: str,
            resolver: "HttpDtsResolver",
            resource: "ElementTree",
            reference: Optional[DtsReference]=None,
            collection: Optional["HttpResolverDtsCollection"]=None,
            **kwargs
    ):
        super(DtsResolverDocument, self).__init__(identifier=identifier, resource=resource, **kwargs)
        self._resolver = resolver
        self._reference = reference
        self._resource = resource

        self._parent = None
        self._prev_id, self._next_id = None, None
        self._parsed_metadata = False
        self._collection = collection
        self._depth = None
        self._metadata = None

    @property
    def collection(self):
        if not self._collection:
            self._collection = self.resolver.getMetadata(self.id)
        return self._collection

    @property
    def depth(self):
        if self._depth is None:
            self._depth = self.collection.citation.depth
        return self._depth

    @property
    def metadata(self):
        if not self._metadata:
            self._metadata = self.collection.metadata
        return self._metadata

    @property
    def resolver(self) -> "HttpDtsResolver":
        return self._resolver

    def getTextualNode(self, subreference: DtsReference) -> "DtsResolverPassage":
        obj = self.resolver.getTextualNode(textId=self.id, subreference=subreference)
        # We set up the collection with the current one :
        #   if it has been retrieved, it'll be used
        obj._collection = self._collection
        return obj

    def getReffs(self, level: int=1, subreference: DtsReference=None):
        return self.resolver.getReffs(textId=self.id, subreference=(subreference or self.reference))

    def _dict_to_ref(self, header_dic):
        ref = header_dic.get("ref", [None])[0]
        if ref:
            return DtsReference(ref)

        s = header_dic.get("start", [None])[0]
        e = header_dic.get("end", [None])[0]
        if s and e:
            return DtsReference(s, e)

    @classmethod
    def parse(cls, identifier: str, reference: DtsReference, resolver: "HttpDtsResolver", response: "Response"):
        o = cls(
            identifier=identifier,
            reference=reference,
            resolver=resolver,
            resource=xmlparser(response.text)
        )

        links = link_header.parse(response.headers.get("Link", ""))
        links = {
            link.rel: parse_qs(urlparse(link.href).query)
            for link in links.links
        }
        if links.get("next"):
            o._next_id = o._dict_to_ref(links.get("next"))
        if links.get("prev"):
            o._prev_id = o._dict_to_ref(links.get("prev"))
        if links.get("parent"):
            o._parent = o._dict_to_ref(links.get("up"))
        if links.get("first"):
            o._first_id = o._dict_to_ref(links.get("first"))
        if links.get("parent"):
            o._last_id = o._dict_to_ref(links.get("last"))
        if links.get("collection"):
            o._collection = o._dict_to_ref(links.get("collection"))

        return o

    @property
    def reference(self) -> DtsReference:
        return self._reference
