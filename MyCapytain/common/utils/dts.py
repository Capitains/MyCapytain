from ._json_ld import dict_to_literal
from rdflib import URIRef
from ..metadata import Metadata


__all__ = [
    "parse_metadata"
]


def parse_metadata(metadata_obj: Metadata, metadata_dictionary: dict) -> None:
    """ Adds to a Metadata object any DublinCore or dts:Extensions object
    found in the given dictionary

    :param metadata_obj:
    :param metadata_dictionary:
    """
    for key, value_set in metadata_dictionary.get("https://w3id.org/dts/api#dublincore", [{}])[0].items():
        term = URIRef(key)
        for value_dict in value_set:
            metadata_obj.add(term, *dict_to_literal(value_dict))

    for key, value_set in metadata_dictionary.get("https://w3id.org/dts/api#extensions", [{}])[0].items():
        term = URIRef(key)
        for value_dict in value_set:
            metadata_obj.add(term, *dict_to_literal(value_dict))
