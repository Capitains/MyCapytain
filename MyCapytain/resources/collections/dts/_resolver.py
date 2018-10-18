from MyCapytain.common.constants import RDF_NAMESPACES
from pyld.jsonld import expand
import re

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

    def _run(self, item=None):
        if not self._condition_lambda():
            self._update_lambda()
            # Replace the Proxied instance by the actualy proxied value
            setattr(self._obj, self._attr, self._proxied)

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

        self._children = PaginatedProxy(
            self,
            "_children",
            lambda: self._parse_paginated_members(direction="children"),
            lambda: self._parsed["children"]
        )
        self._parents = PaginatedProxy(
            self,
            "_parents",
            lambda: self._parse_paginated_members(direction="parents"),
            lambda: self._parsed["parents"]
        )

        self._resolver = resolver
        self._metadata_parsed = metadata_parsed

        self._parsed = {
            "children": False,
            "parents": False,
            "metadata": False
        }
        self._last_page_parsed = {
            "children": None,
            "parents": None,
        }

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
            else:
                self._parsed[direction] = True

    @property
    def children(self):
        return super(HttpResolverDtsCollection, self).children

    @property
    def parents(self):
        return super(HttpResolverDtsCollection, self).parents

    def retrieve(self):
        if not self._metadata_parsed:
            query = self._resolver.endpoint.get_collection(self.id)
            data = query.json()
            if not len(data):
                raise Exception("We'll see this one later")  # toDo: What error should it be ?
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

        for member in obj.get(str(_hyd.member), []):
            subcollection = cls.parse(member, metadata_parsed=False, **additional_parameters)
            if direction == "children":
                subcollection._parents.set({collection})
            members.append(subcollection)

        if "https://www.w3.org/ns/hydra/core#view" not in obj:
            collection._parsed[direction] = True

        return members
