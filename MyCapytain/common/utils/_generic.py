import re
from collections import OrderedDict
from functools import reduce


class OrderedDefaultDict(OrderedDict):
    """ Extension of Default Dict that makes an OrderedDefaultDict

    :param default_factory__: Default class to initiate
    """

    def __init__(self, default_factory=None, *args, **kwargs):
        super(OrderedDefaultDict, self).__init__(*args, **kwargs)
        self.default_factory = default_factory

    def __missing__(self, key):
        if self.default_factory is None:
            raise KeyError(key)
        val = self[key] = self.default_factory()
        return val


def nested_ordered_dictionary():
    """ Helper to create a nested ordered default dictionary

    :rtype OrderedDefaultDict:
    :return: Nested Ordered Default Dictionary instance
    """
    return OrderedDefaultDict(nested_ordered_dictionary)


def nested_get(dictionary, keys):
    """ Get value in dictionary for dictionary[keys[0]][keys[1]][keys[..n]]

    :param dictionary: An input dictionary
    :param keys: Keys where to store data
    :return:
    """
    return reduce(lambda d, k: d[k], keys, dictionary)


def nested_set(dictionary,  keys, value):
    """ Set value in dictionary for dictionary[keys[0]][keys[1]][keys[..n]]

    :param dictionary: An input dictionary
    :param keys: Keys where to store data
    :param value: Value to set at keys** target
    :return: None
    """
    nested_get(dictionary, keys[:-1])[keys[-1]] = value


_strip = re.compile("([ ]{2,})+")


def normalize(string):
    """ Remove double-or-more spaces in a string

    :param string: A string to change
    :type string: text_type
    :rtype: text_type
    :returns: Clean string
    """
    return _strip.sub(" ", string)