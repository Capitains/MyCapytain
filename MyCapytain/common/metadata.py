# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.metadata
   :synopsis: Metadata related objects

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""
from __future__ import unicode_literals


from collections import defaultdict, OrderedDict
from past.builtins import basestring
from builtins import range, object
from copy import copy


class Metadatum(object):
    """ Metadatum object represent a single field of metadata 
        
    :param name: Name of the field
    :type name: basestring
    :param children: List of tuples, where first element is the key, and second the value
    :type children: List

    :Example: 
        >>>    a = Metadatum(name="label", [("lat", "Amores"), ("fre", "Les Amours")])
        >>>    print(a["lat"]) # == "Amores"

    .. automethod:: __getitem__
    .. automethod:: __setitem__
    .. automethod:: __iter__

    """

    def __init__(self, name, children=None):
        """ Initiate a Metadatum object
        """
        self.name = name
        self.children = OrderedDict()
        self.default = None

        if children is not None and isinstance(children, list):
            for tup in children:
                self[tup[0]] = tup[1]

    def __getitem__(self, key):
        """ Add an iterable access method

        Int typed key access to the *n* th registered key in the instance. 
        If string based key does not exist, see for a default.
        
        :param key: Key of wished value
        :type key: basestring, tuple, int
        :returns: An element of children whose index is key

        :raises: KeyError if key is unknown (when using Int based key or when default is not set)

        :Example:
            >>>    a = Metadatum(name="label", [("lat", "Amores"), ("fre", "Les Amours")])
            >>>    print(a["lat"]) # Amores
            >>>    print(a[("lat", "fre")]) # Amores, Les Amours
            >>>    print(a[0]) # Amores 
            >>>    print(a["dut"]) # Amores

        """
        if isinstance(key, int):
            items = list(self.children.keys())
            if key + 1 > len(items):
                raise KeyError()
            else:
                key = items[key]
        elif isinstance(key, tuple):
            return tuple([self[k] for k in key])

        if key not in self.children:
            if self.default is None:
                raise KeyError()
            else:
                return self.children[self.default]
        else:
            return self.children[key]

    def __setitem__(self, key, value):
        """ Register index key and value for the instance
        
        :param key: Index key(s) for the metadata
        :type key: basestring, list, tuple
        :param value: Values for the metadata
        :type value: basestring, list, tuple
        :returns: An element of children whose index is key

        :raises: `TypeError` if key is not basestring or tuple of basestring
        :raises: `ValueError` if key and value are list and are not the same size

        :Example:
            >>> a = Metadatum(name="label")

            >>> a["eng"] = "Illiad"
            >>> print(a["eng"]) # Illiad

            >>> a[("fre", "grc")] = ("Illiade", "Ἰλιάς")
            >>> print(a["fre"], a["grc"]) # Illiade, Ἰλιάς

            >>> a[("ger", "dut")] = "Iliade"
            >>> print(a["ger"], a["dut"]) # Iliade, Iliade
        """

        if isinstance(key, tuple):
            if not isinstance(value, (tuple, list)):
                value = [value]*len(key)
            if len(value) < len(key):
                raise ValueError("Less values than keys detected")
            for i in range(0, len(key)):
                self[key[i]] = value[i]
        elif not isinstance(key, basestring):
            raise TypeError(
                "Only basestring or tuple instances are accepted as key")
        else:
            self.children[key] = value
            if self.default is None:
                self.default = key

    def setDefault(self, key):
        """ Set a default key when a field does not exist

        :param key: An existing key of the instance
        :type key: basestring
        :returns: Default key
        :raises: `ValueError` If key is not registered

        :Example: 
            >>>    a = Metadatum(name="label", [("lat", "Amores"), ("fre", "Les Amours")])
            >>>    a.setDefault("fre")
            >>>    print(a["eng"]) # == "Les Amours"

        """
        if key not in self.children:
            raise ValueError("Can not set a default to an unknown key")
        else:
            self.default = key
        return self.default

    def __iter__(self):
        """ Iter method of Metadatum

        :Example:
            >>> a = Metadata(name="label", [("lat", "Amores"), ("fre", "Les Amours")])
            >>> for key, value in a:
            >>>     print(key, value) # Print ("lat", "Amores") and then ("fre", "Les Amours")
        """
        i = 0
        for key in self.children:
            yield (key, self.children[key])
            i += 1

    def __len__(self):
        """ Get the length of the current Metadatum object

        :return: Number of variant of the metadatum
        :rtype: int

        :Example:
            >>> a = Metadata(name="label", [("lat", "Amores"), ("fre", "Les Amours")])
            >>> len(a) == 2
        """
        return len(self.children)


class Metadata(object):
    """ 
        A metadatum aggregation object provided to centralize metadata
        
        :param key: A metadata field name
        :type key: List.<basestring>

        :ivar metadata: Dictionary of metadatum

        .. automethod:: __getitem__
        .. automethod:: __setitem__
        .. automethod:: __iter__
        .. automethod:: __len__
        .. automethod:: __add__
    """
    def __init__(self, keys=None):
        """ Initiate the object
        """
        self.metadata = defaultdict(Metadatum)
        self.__keys = []
        if keys is not None:
            for key in keys:
                self[key] = Metadatum(name=key)

    def __getitem__(self, key):
        """ Add a quick access system through getitem on the instance
        
        :param key: Index key representing a set of metadatum
        :type key: basestring, int, tuple
        :returns: An element of children whose index is key
        :raises: `KeyError` If key is not registered or recognized

        :Example:
            >>>    a = Metadata()
            >>>    m1 = Metadatum(name="title", [("lat", "Amores"), ("fre", "Les Amours")])
            >>>    m2 = Metadatum(name="author", [("lat", "Ovidius"), ("fre", "Ovide")])
            >>>    a[("title", "author")] = (m1, m2)

            >>>    a["title"] == m1
            >>>    a[0] == m1
            >>>    a[("title", "author")] == (m1, m2)


        """
        if isinstance(key, int):
            if key + 1 > len(self.__keys):
                raise KeyError()
            else:
                key = self.__keys[key]
        elif isinstance(key, tuple):
            return tuple([self[k] for k in key])

        if key not in self.metadata:
            raise KeyError()
        else:
            return self.metadata[key]

    def __setitem__(self, key, value):
        """ Set a new metadata field
        
        :param key: Name of metadatum field
        :type key: basestring, tuple
        :param value: Metadum dictionary
        :type value: Metadatum
        :returns: An element of children whose index is key

        :raises: `TypeError` if key is not basestring or tuple of basestring
        :raises: `ValueError` if key and value are list and are not the same size

        :Example:
            >>>    a = Metadata()

            >>>    a["title"] = Metadatum(name="title", [("lat", "Amores"), ("fre", "Les Amours")])
            >>>    print(a["title"]["lat"]) # Amores

            >>>    a[("title", "author")] = (
            >>>         Metadatum(name="title", [("lat", "Amores"), ("fre", "Les Amours")]),
            >>>         Metadatum(name="author", [("lat", "Ovidius"), ("fre", "Ovide")])
            >>>     )
            >>>    print(a["title"]["lat"], a["author"]["fre"]) # Amores, Ovide

        """
        if isinstance(key, tuple):
            if len(value) < len(key):
                raise ValueError("Less values than keys detected")
            for i in range(0, len(key)):
                self[key[i]] = value[i]
        elif not isinstance(key, basestring):
            raise TypeError(
                "Only basestring or tuple instances are accepted as key")
        else:
            if not isinstance(value, Metadatum) and isinstance(value, list):
                self.metadata[key] = Metadatum(key, value)
            elif isinstance(value, Metadatum):
                self.metadata[key] = value

            if key in self.metadata and key not in self.__keys:
                self.__keys.append(key)

    def __iter__(self):
        """ Iter method of Metadata

        :Example:
            >>> a = Metadata(("title", "desc", "author"))
            >>> for key, value in a:
            >>>     print(key, value) # Print ("title", "<Metadatum object>") then ("desc", "<Metadatum object>")...
        """
        i = 0
        for key in self.__keys:
            yield (key, self.metadata[key])
            i += 1

    def __add__(self, other):
        """ Merge Metadata objects together

        :param other: Metadata object to merge with the current one
        :type other: Metadata
        :returns: The merge result of both metadata object
        :rtype: Metadata

        :Example:
            >>> a = Metadata(name="label")
            >>> b = Metadata(name="title")
            >>> a + b == Metadata(name=["label", "title"])
        """
        result = copy(self)
        for metadata_key, metadatum in other:
            if metadata_key in self.__keys:
                for key, value in metadatum:
                    result[metadata_key][key] = value
            else:
                result[metadata_key] = metadatum
        return result

    def __len__(self):
        """ Returns the number of Metadatum registered in the object

        :rtype: int
        :returns: Number of metadatum objects

        :Example:
            >>>    a = Metadata(("title", "description", "author"))
            >>>    print(len(a)) # 3
        """
        return len(
            [
                k
                for k in self.__keys
                if isinstance(self.metadata[k], Metadatum)
            ]
        )
