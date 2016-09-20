

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