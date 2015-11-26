

class DuplicateReference(Exception):
    """ Error generated when a duplicate is found in Reference
    """
    pass

class RefsDeclError(Exception):
    """ Error issued when an the refsDecl does not succeed in xpath (no results)
    """
    pass