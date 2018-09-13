import os.path
import json
import typing
import unittest
import requests_mock
from MyCapytain.resolvers.dts.api_v1 import HttpDtsResolver


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


def _load_json_mock(endpoint: str, example: str) -> typing.Union[dict, list]:
    return json.loads(_load_mock(endpoint, example))


class TestHttpDtsResolver(unittest.TestCase):
    def setUp(self):
        self.root_uri = "http://foobar.com/api/dts"
        self.resolver = HttpDtsResolver(self.root_uri)

    @requests_mock.mock()
    def test_navigation_simple(self, mock_set):
        _id = "urn:cts:greekLit:tlg0012.tlg001.opp-grc"
        mock_set.get(self.root_uri, text=_load_mock("root.json"))
        mock_set.get(
            self.root_uri+"/navigation?level=1&groupSize=1&id="+_id,
            text=_load_mock("navigation", "example1.json"),
            complete_qs=True
        )
        reffs = self.resolver.getReffs(_id)
        print(reffs)

