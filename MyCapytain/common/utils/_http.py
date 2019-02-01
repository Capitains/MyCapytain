from collections import namedtuple
from urllib.parse import parse_qs, urlparse, urljoin

import link_header

_Route = namedtuple("Route", ["path", "query_dict"])
_Navigation = namedtuple("Navigation", ["prev", "next", "last", "current", "first"])


def parse_pagination(headers):
    """ Parses headers to create a pagination objects

    :param headers: HTTP Headers
    :type headers: dict
    :return: Navigation object for pagination
    :rtype: _Navigation
    """
    links = {
        link.rel: parse_qs(link.href).get("page", None)
        for link in link_header.parse(headers.get("Link", "")).links
    }
    return _Navigation(
        links.get("previous", [None])[0],
        links.get("next", [None])[0],
        links.get("last", [None])[0],
        links.get("current", [None])[0],
        links.get("first", [None])[0]
    )


def parse_uri(uri, endpoint_uri):
    """ Parse a URI into a Route namedtuple

    :param uri: URI or relative URI
    :type uri: str
    :param endpoint_uri: URI of the endpoint
    :type endpoint_uri: str
    :return: Parsed route
    :rtype: _Route
    """
    temp_parse = urlparse(uri)
    return _Route(
        urljoin(endpoint_uri, temp_parse.path),
        parse_qs(temp_parse.query)
    )
