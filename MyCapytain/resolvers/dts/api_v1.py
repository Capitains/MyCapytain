# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resolvers.cts.remote
   :synopsis: Resolver built for CTS APIs

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from typing import Union, Optional, Any, Dict

from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.common.reference import BaseReference, BaseReferenceSet, \
    DtsReference, DtsReferenceSet
from MyCapytain.retrievers.dts import HttpDtsRetriever
from MyCapytain.common.utils import dict_to_literal

from rdflib import URIRef
from pyld.jsonld import expand


def _parse_ref(ref_dict):
    if "https://w3id.org/dts/api#ref" in ref_dict:
        refs = ref_dict["https://w3id.org/dts/api#"],
    elif "https://w3id.org/dts/api#start" in ref_dict and \
         "https://w3id.org/dts/api#end" in ref_dict:
        refs = ref_dict["https://w3id.org/dts/api#start"], ref_dict["https://w3id.org/dts/api#end"]
    else:
        return None  # Maybe Raise ?

    obj = DtsReference(*refs)

    for key, value_set in ref_dict.get("https://w3id.org/dts/api#dublincore", [{}])[0].items():
        term = URIRef(key)
        for value_dict in value_set:
            obj.metadata.add(term, *dict_to_literal(value_dict))

    for key, value_set in ref_dict.get("https://w3id.org/dts/api#extensions", [{}])[0].items():
        term = URIRef(key)
        for value_dict in value_set:
            obj.metadata.add(term, *dict_to_literal(value_dict))

    return obj


class HttpDtsResolver(Resolver):
    """ HttpDtsResolver provide a resolver for DTS API http endpoint.

    :param endpoint: DTS API Retriever
    """
    def __init__(self, endpoint: Union[str, HttpDtsRetriever]):
        if not isinstance(endpoint, HttpDtsRetriever):
            endpoint = HttpDtsRetriever(endpoint)
        self._endpoint = endpoint

    @property
    def endpoint(self) -> HttpDtsRetriever:
        """ DTS Endpoint of the resolver

        :return: DTS Endpoint
        :rtype: HttpDtsRetriever
        """
        return self._endpoint

    def getReffs(
            self,
            textId: str,
            level: int=1,
            subreference: Union[str, BaseReference]=None,
            include_descendants: bool=False,
            additional_parameters: Optional[Dict[str, Any]]=None
    ) -> DtsReferenceSet:
        if not additional_parameters:
            additional_parameters = {}

        reffs = []
        response = self.endpoint.get_navigation(
            textId, level=level, ref=subreference,
            group_size=additional_parameters.get("group_by", 1),
            exclude=additional_parameters.get("exclude", None)
        )
        response.raise_for_status()

        data = response.json()
        data = expand(data)
        members = data[0].get("https://w3id.org/dts/api#member", None)

        reffs.extend([
            _parse_ref(ref)
            for ref in members
        ])

        reffs = DtsReferenceSet(*reffs)

