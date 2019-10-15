# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.common.utils
   :synopsis: Common useful tools

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""

from ._generic import (
    OrderedDefaultDict, nested_ordered_dictionary, nested_get, nested_set, normalize
)
from ._graph import Subgraph, expand_namespace
from ._http import parse_pagination, parse_uri
from ._json_ld import dict_to_literal, literal_to_dict
