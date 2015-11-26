

class DuplicateReference(SyntaxWarning):
    """ Error generated when a duplicate is found in Reference
    """

class RefsDeclError(Exception):
    """ Error issued when an the refsDecl does not succeed in xpath (no results)
    """
    pass
