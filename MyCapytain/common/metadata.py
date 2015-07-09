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


class Metadatum(object):

    """ Metadatum object represent a single field of metadata """
        

    def __init__(self, name, children=None):
        """ Initiate a Metadatum object
        
        :param name: Name of the field
        :type name: basestring
        :param children: List.tuple
        :type children: dict
        """
        self.name = name
        self.children = OrderedDict()
        self.default = None

        if children is not None and isinstance(children, list):
            for tup in children:
                self[tup[0]] = tup[1]

    def __getitem__(self, key):
        """ Add an iterable access method
        
        :param key:
        :type key:
        :returns: An element of children whose index is key
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
        """ Add an iterable access method
        
        :param key:
        :type key:
        :param value:
        :type value:
        :returns: An element of children whose index is key
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
        if key not in self.children:
            raise ValueError("Can not set a default to an unknown key")
        else:
            self.default = key
        return self.default

    def __iter__(self):
        i = 0
        for key in self.children:
            yield (key, self.children[key])
            i += 1


class Metadata(object):
    """ 
        A metadatum aggregation object provided to centralize metadata
    """
    def __init__(self, keys=None):
        """ Initiate the object
        
        :param key: A metadata field name
        :type key: List.<basestring>
        """
        self.metadata = defaultdict(Metadatum)
        self.__keys = []
        if keys is not None:
            for key in keys:
                self[key] = Metadatum(name=key)

    def __getitem__(self, key):
        """ Add an iterable access method
        
        :param key:
        :type key:
        :returns: An element of children whose index is key
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
        """ Add an iterable access method
        
        :param key:
        :type key:
        :param value:
        :type value:
        :returns: An element of children whose index is key
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
        i = 0
        for key in self.__keys:
            yield (key, self.metadata[key])
            i += 1

    def __len__(self):
        return len(
            [
                k
                for k in self.__keys
                if isinstance(self.metadata[k], Metadatum)
            ]
        )
