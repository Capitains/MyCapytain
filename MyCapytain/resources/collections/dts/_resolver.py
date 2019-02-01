import re
from pyld.jsonld import expand
from typing import Optional

from MyCapytain.common.constants import RDF_NAMESPACES
from MyCapytain.errors import UnknownCollection
from ._base import DtsCollection


_hyd = RDF_NAMESPACES.HYDRA
_empty = [{"@value": None}]
_re_page = re.compile("page=(\d+)")


class PaginatedProxy:

    __UPDATES_CALLABLES__ = {
        "update", "add", "extend"
    }

    def __init__(
            self,
            obj,
            proxied: str,
            update_lambda,
            condition_lambda
    ):
        self._proxied = getattr(obj, proxied)
        self._obj = obj
        self._attr = proxied
        self._condition_lambda = condition_lambda
        self._update_lambda = update_lambda

    def __getattr__(self, item):
        if item in self.__UPDATES_CALLABLES__:
            return getattr(self._proxied, item)
        if item == "set":
            return self.set
        return self._run(item)

    def _run(self, item: Optional[str]=None):
        if not self._condition_lambda():
            self._update_lambda()

        if item:
            return getattr(self._proxied, item)
        return self._proxied

    def set(self, value) -> None:
        self._proxied = value

    def __iter__(self):
        return iter(self._run())

    def __getitem__(self, item):
        if isinstance(self._proxied, (list, dict, set, tuple)):
            # If it is in, we do not update the object
            if item in self._proxied:
                return self._proxied[item]
            # If it not in, and we are still in this object,
            # It means we need to crawl :
            self._run()
            return self._proxied[item]
        raise TypeError("'PaginatedProxy' object is not subscriptable")

    def __eq__(self, other):
        return self._proxied == other


class HttpResolverDtsCollection(DtsCollection):
    def __init__(
            self,
            identifier: str,
            resolver: "HttpDtsResolver",
            metadata_parsed=True, *args, **kwargs):
        super(HttpResolverDtsCollection, self).__init__(identifier, *args, **kwargs)

        self._parsed = {
            "children": False,
            "parents": False,
            "metadata": metadata_parsed
        }
        self._last_page_parsed = {
            "children": None,
            "parents": None,
        }

        self._children = PaginatedProxy(
            self,
            "_children",
            update_lambda=lambda: self._parse_paginated_members(direction="children"),
            condition_lambda=lambda: self._parsed["parents"]
        )
        self._parents = PaginatedProxy(
            self,
            "_parents",
            update_lambda=lambda: self._parse_paginated_members(direction="parents"),
            condition_lambda=lambda: self._parsed["parents"]
        )

        self._resolver = resolver

    def _parse_paginated_members(self, direction="children"):
        """ Launch parsing of children
        """

        page = self._last_page_parsed[direction]
        if not page:
            page = 1
        else:
            page = int(page)
        while page:
            if page > 1:
                response = self._resolver.endpoint.get_collection(
                    collection_id=self.id,
                    page=page,
                    nav=direction
                )
            else:
                response = self._resolver.endpoint.get_collection(
                    collection_id=self.id,
                    nav=direction
                )
            response.raise_for_status()

            data = response.json()
            data = expand(data)[0]

            if direction == "children":
                self.children.update({
                    o.id: o
                    for o in type(self).parse_member(
                        obj=data, collection=self, direction=direction, resolver=self._resolver
                    )
                })
            else:
                self.parents.update({
                    o
                    for o in type(self).parse_member(
                        obj=data, collection=self, direction=direction, resolver=self._resolver
                    )
                })
            self._last_page_parsed[direction] = page

            page = None
            if "https://www.w3.org/ns/hydra/core#view" in data:
                if "https://www.w3.org/ns/hydra/core#next" in data["https://www.w3.org/ns/hydra/core#view"][0]:
                    page = int(_re_page.findall(
                        data["https://www.w3.org/ns/hydra/core#view"]
                            [0]["https://www.w3.org/ns/hydra/core#next"]
                            [0]["@value"]
                    )[0])

        self._parsed[direction] = True

    @property
    def children(self):
        if not self._parsed["children"]:
            if not self.size == 0:
                return self._children
            else:
                self._parsed["children"] = True
        if isinstance(self._children, PaginatedProxy):

            self._children = self._children._proxied

        return self._children

    @property
    def parents(self):
        if self._parsed["parents"] and isinstance(self._parents, PaginatedProxy):
            self._parents = self._parents._proxied
        return self._parents

    def retrieve(self):
        if not self._parsed["metadata"]:
            query = self._resolver.endpoint.get_collection(self.id)
            data = query.json()
            if not len(data):
                raise UnknownCollection(
                    "The contacted endpoint seems to not have any data about collection %s " % self.id
                )
            self._parse_metadata(expand(data)[0])
        return True

    @classmethod
    def parse_member(
            cls,
            obj: dict,
            collection: "HttpResolverDtsCollection",
            direction: str,
            **additional_parameters):

        """ Parse the member value of a Collection response
        and returns the list of object while setting the graph
        relationship based on `direction`

        :param obj: PyLD parsed JSON+LD
        :param collection: Collection attached to the member property
        :param direction: Direction of the member (children, parent)
        """
        members = []

        # Start pagination check here
        hydra_members = obj.get(str(_hyd.member), [])

        if hydra_members:
            for member in hydra_members:
                subcollection = cls.parse(member, metadata_parsed=False, **additional_parameters)
                if direction == "children":
                    subcollection.parents.set({collection})
                members.append(subcollection)

            if "https://www.w3.org/ns/hydra/core#view" not in obj or \
                    (direction == "children" and collection.size == 0):
                collection._parsed[direction] = True

        return members
