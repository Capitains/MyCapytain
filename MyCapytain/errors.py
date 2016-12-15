# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.errors
   :synopsis: MyCapytain errors

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""


class DuplicateReference(SyntaxWarning):
    """ Error generated when a duplicate is found in Reference
    """


class RefsDeclError(Exception):
    """ Error issued when an the refsDecl does not succeed in xpath (no results)
    """
    pass


class InvalidSiblingRequest(Exception):
    """ This error is thrown when one attempts to get previous or next passage on a passage with a range of different
    depth, ex. : 1-2.25
    """
    pass


class InvalidURN(Exception):
    """ This error is thrown when URN are not valid
    """


class MissingAttribute(Exception):
    """ This error is thrown when an attribute is not present in the Object (missing at startup)
    """


class UnknownObjectError(ValueError):
    """ This error is thrown when an object does not exist in an inventory or in an API
    """


class UnknownNamespace(ValueError):
    """ This error is thrown when a namespace is unknown
    """
