# -*- coding: utf-8 -*-
"""
.. module:: MyCapytain.errors
   :synopsis: MyCapytain errors

.. moduleauthor:: Thibault Clérice <leponteineptique@gmail.com>


"""


class MyCapytainException(BaseException):
    """ Namespacing errors
    """


class DuplicateReference(SyntaxWarning, MyCapytainException):
    """ Error generated when a duplicate is found in Reference
    """


class RefsDeclError(Exception, MyCapytainException):
    """ Error issued when an the refsDecl does not succeed in xpath (no results)
    """
    pass


class InvalidSiblingRequest(Exception, MyCapytainException):
    """ This error is thrown when one attempts to get previous or next passage on a passage with a range of different
    depth, ex. : 1-2.25
    """
    pass


class InvalidURN(Exception, MyCapytainException):
    """ This error is thrown when URN are not valid
    """


class MissingAttribute(Exception, MyCapytainException):
    """ This error is thrown when an attribute is not present in the Object (missing at startup)
    """


class UnknownObjectError(ValueError, MyCapytainException):
    """ This error is thrown when an object does not exist in an inventory or in an API
    """


class UnknownNamespace(ValueError, MyCapytainException):
    """ This error is thrown when a namespace is unknown
    """


class UndispatchedTextError(Exception, MyCapytainException):
    """ This error is thrown when a text has not been dispatched by a dispatcher
    """


class UnknownCollection(KeyError, MyCapytainException):
    """ A collection is unknown to its ancestor
    """


class EmptyReference(SyntaxWarning, MyCapytainException):
    """ Error generated when a duplicate is found in Reference
    """

    
class CitationDepthError(UnknownObjectError, MyCapytainException):
    """ Error generated when the depth of a requested citation is deeper than the citation scheme of the text
    """


class MissingRefsDecl(Exception, MyCapytainException):
    """ A text has no properly encoded refsDecl
    """
