import os.path
import json
import typing
import unittest
import requests_mock
from MyCapytain.resolvers.dts.api_v1 import HttpDtsResolver
from MyCapytain.common.reference import DtsReferenceSet, DtsReference, DtsCitation
from MyCapytain.common.metadata import Metadata
from MyCapytain.common.constants import Mimetypes
from rdflib.term import URIRef

# Set-up for the test classes
_cur_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__)
    )
)


def quote(string):
    return string.replace(":", "%3A")


def _load_mock(*files: str) -> str:
    """ Easily load a mock file

    :param endpoint: Endpoint that is being tested
    :param example: Example to load
    :return: Example data
    """
    fname = os.path.abspath(
        os.path.join(
            _cur_path,
            "data",
            *files
        )
    )
    with open(fname) as fopen:
        data = fopen.read()
    return data


from MyCapytain.common.constants import set_graph, bind_graph


def reset_graph():
    set_graph(bind_graph())
