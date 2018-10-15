from MyCapytain.common.constants import RDF_NAMESPACES
from pyld.jsonld import expand
import re

from ._base import DtsCollection


_hyd = RDF_NAMESPACES.HYDRA
_empty = [{"@value": None}]
_re_page = re.compile("page=(\d+)")


class PaginatedProxy:
    def __init__(self, proxied, update_lambda, condition_lambda):
        self._proxied = proxied
        self._condition_lambda = condition_lambda
        self._update_lambda = update_lambda

    def __getattr__(self, item):
        if item == "update":
            return self._proxied.update
        if item == "add":
            return self._proxied.add
        if item == "set":
            return self.set
        else:
            if not self._condition_lambda():
                self._update_lambda()
        return getattr(self._proxied, item)

    def set(self, value):
        self._proxied = value

    def __iter__(self):
        return iter(self._proxied)

    def __getitem__(self, item):
        if isinstance(self._proxied, dict):
            return self._proxied[item]
        raise TypeError("'PaginatedProxy' object is not subscriptable")


class HttpResolverDtsCollection(DtsCollection):
    def __init__(
            self,
            identifier: str,
            resolver: "HttpDtsResolver",
            metadata_parsed=True, *args, **kwargs):
        super(HttpResolverDtsCollection, self).__init__(identifier, *args, **kwargs)

        self._children = PaginatedProxy(
            self._children,
            lambda: self._parse_paginated_members(direction="children"),
            lambda: self._parsed["children"]
        )
        self._parents = PaginatedProxy(
            self._parents,
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
            data = expand(data)

            self.parse_member(obj=data, collection=self, direction=direction)
            self._last_page_parsed[direction] = page

            page = None
            if "https://www.w3.org/ns/hydra/core#view" in data:
                if "https://www.w3.org/ns/hydra/core#next" in data["https://www.w3.org/ns/hydra/core#view"][0]:
                    page = _re_page.findall(
                        data["https://www.w3.org/ns/hydra/core#view"]
                            [0]["https://www.w3.org/ns/hydra/core#next"]
                            [0]["@value"]
                    )[0]

        self._parsed[direction] = True

    @property
    def children(self):
        if not self._parsed["children"]:
            self._parse_paginated_members(direction="children")
        return super(HttpResolverDtsCollection, self).children

    @property
    def parents(self):
        if not self._parsed["parents"]:
            self._parse_paginated_members(direction="parents")
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
            collection: "DtsCollection",
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
