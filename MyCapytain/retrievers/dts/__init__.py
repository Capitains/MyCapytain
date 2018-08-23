# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.retrievers.cts5
   :synopsis: Cts5 endpoint implementation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
import MyCapytain.retrievers.prototypes
from MyCapytain import __version__
import requests
from MyCapytain.common.utils import parse_uri


class HttpDtsRetriever(MyCapytain.retrievers.prototypes.API):
    def __init__(self, endpoint):
        super(HttpDtsRetriever, self).__init__(endpoint)
        self._routes = None

    def call(self, route, parameters, mimetype="application/ld+json"):
        """ Call an endpoint given the parameters

        :param route: Named of the route which is called
        :type route: str
        :param parameters: Dictionary of parameters
        :type parameters: dict
        :param mimetype: Mimetype to require
        :type mimetype: str
        :rtype: text
        """

        parameters = {
            key: str(parameters[key]) for key in parameters if parameters[key] is not None
        }
        parameters.update(self.routes[route].query_dict)

        request = requests.get(
            self.routes[route].path,
            params=parameters,
            headers={
                "Accept": mimetype,
                "Accept-Charset": "utf-8",
                "User-Agent": "MyCapytain/{MyCapVersion} {DefaultRequestUA}".format(
                    MyCapVersion=__version__,
                    DefaultRequestUA=requests.utils.default_user_agent()
                )
            }
        )
        request.raise_for_status()
        if request.encoding is None:
            request.encoding = "utf-8"
        return request

    @property
    def routes(self):
        """ Retrieves the main routes of the DTS Collection

        Response format expected :
            {
              "@context": "/dts/api/contexts/EntryPoint.jsonld",
              "@id": "/dts/api/",
              "@type": "EntryPoint",
              "collections": "/dts/api/collections/",
              "documents": "/dts/api/documents/",
              "navigation" : "/dts/api/navigation"
            }

        :returns: Dictionary of main routes with their path
        :rtype: dict
        """
        if self._routes:
            return self._routes

        request = requests.get(self.endpoint)
        request.raise_for_status()
        data = request.json()
        self._routes = {
            "collections": parse_uri(data["collections"], self.endpoint),
            "documents": parse_uri(data["documents"], self.endpoint),
            "navigation": parse_uri(data["navigation"], self.endpoint)
        }
        return self._routes

    def get_collection(self, collection_id=None, nav="children", page=None):
        """ Makes a call on the Collection API

        :param collection_id: Id of the collection to retrieve
        :param nav: Direction of the navigation
        :param page: Page to retrieve
        :return: Response
        :rtype: requests.Response
        """
        return self.call(
            "collections",
            {
                "id": collection_id,
                "nav": nav,
                "page": page
            }
        )

    def get_navigation(
            self, collection_id,
            level=None, ref=None, group_size=None, max_=None, exclude=None,
            page=None):
        """ Make a navigation request on the DTS API

        :param collection_id: Id of the collection
        :param level: Lever at which the references should be listed
        :param ref: If ref is a tuple, it is treated as a range. String or int are treated as single ref
        :param group_size: Size of the ranges the server should produce
        :param max_: Maximum number of results
        :param exclude: Exclude specific metadata.
        :param page: Page
        :return: Response
        :rtype: requests.Response
        """
        parameters = {
            "id": collection_id,
            "level": level,
            "groupSize": group_size,
            "max": max_,
            "exclude": exclude,
            "page": page
        }
        if isinstance(ref, tuple):
            parameters["start"], parameters["end"] = ref
        elif ref:
            parameters["ref"] = ref

        return self.call(
            "navigation",
            parameters
        )

    def get_document(
            self,
            collection_id, ref=None, mimetype="application/tei+xml, application/xml"):
        """ Make a navigation request on the DTS API

        :param collection_id: Id of the collection
        :param ref: If ref is a tuple, it is treated as a range. String or int are treated as single ref
        :param mimetype: Media type to request
        :return: Response
        :rtype: requests.Response
        """
        parameters = {
            "id": collection_id
        }
        if isinstance(ref, tuple):
            parameters["start"], parameters["end"] = ref
        elif ref:
            parameters["ref"] = ref

        return self.call(
            "navigation",
            parameters,
            mimetype=mimetype
        )
