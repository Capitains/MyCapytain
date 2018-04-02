# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.retrievers.cts5
   :synopsis: Cts5 endpoint implementation

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
import MyCapytain.retrievers.prototypes
from MyCapytain import __version__
import requests
from MyCapytain.common.utils import parse_uri, parse_pagination


class DTS_Retriever(MyCapytain.retrievers.prototypes.API):
    def __init__(self, endpoint):
        super(DTS_Retriever, self).__init__(endpoint)
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
        return request.text, parse_pagination(request.headers)

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
        :return: Response and Navigation Tuple
        :rtype: (str, MyCapytain.common.utils._Navigation)
        """
        return self.call(
            "collections",
            {
                "id": collection_id,
                "nav": nav,
                "page": page
            }
        )
