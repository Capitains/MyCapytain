# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.resolvers.cts.remote
   :synopsis: Resolver built for CTS APIs

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from typing import Union, Optional, Any, Dict

from MyCapytain.resolvers.prototypes import Resolver
from MyCapytain.common.reference import BaseReference, BaseReferenceSet, \
    DtsReference, DtsReferenceSet, DtsCitation
from MyCapytain.retrievers.dts import HttpDtsRetriever
from MyCapytain.common.utils.dts import parse_metadata

from pyld.jsonld import expand


_empty = [{"@value": None}]


def _parse_ref(ref_dict, default_type :str =None):
    if "https://w3id.org/dts/api#ref" in ref_dict:
        refs = ref_dict["https://w3id.org/dts/api#ref"][0]["@value"],
    elif "https://w3id.org/dts/api#start" in ref_dict and \
         "https://w3id.org/dts/api#end" in ref_dict:
        refs = (
            ref_dict["https://w3id.org/dts/api#start"][0]["@value"],
            ref_dict["https://w3id.org/dts/api#end"][0]["@value"]
        )
    else:
        return None  # Maybe Raise ?
    type_ = default_type
    if "https://w3id.org/dts/api#citeType" in ref_dict:
        type_ = ref_dict["https://w3id.org/dts/api#citeType"][0]["@value"]

    obj = DtsReference(*refs, type_=type_)
    parse_metadata(obj.metadata, ref_dict)

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
            exclude=additional_parameters.get("exclude", None),
            group_by=additional_parameters.get("groupBy", 1)
        )
        response.raise_for_status()

        data = response.json()
        data = expand(data)

        default_type = data[0].get("https://w3id.org/dts/api#citeType", _empty)[0]["@value"]

        members = data[0].get("https://www.w3.org/ns/hydra/core#member", [])

        reffs.extend([
            _parse_ref(ref, default_type=default_type)
            for ref in members
        ])

        citation = None
        if default_type:
            citation = DtsCitation(name=default_type)

        reffs = DtsReferenceSet(
            *reffs,
            level=data[0].get("https://w3id.org/dts/api#level", _empty)[0]["@value"],
            citation=citation
        )
        return reffs
