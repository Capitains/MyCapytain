from rdflib import Literal, URIRef


def literal_to_dict(value):
    """ Transform an object value into a dict readable value

    :param value: Object of a triple which is not a BNode
    :type value: Literal or URIRef
    :return: dict or str or list
    """
    if isinstance(value, Literal):
        if value.language is not None:
            return {"@value": str(value), "@language": value.language}
        return value.toPython()
    elif isinstance(value, URIRef):
        return {"@id": str(value)}
    elif value is None:
        return None
    return str(value)


def dict_to_literal(dict_container: dict):
    """ Transforms a JSON+LD PyLD dictionary into
    an RDFLib object"""
    if isinstance(dict_container["@value"], int):
        return dict_container["@value"],
    else:
        return dict_container["@value"], dict_container.get("@language", None)