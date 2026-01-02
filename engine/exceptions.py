class SearchException(Exception):
    pass


class InvalidPlatformException(SearchException):
    pass


class InvalidQueryException(SearchException):
    pass


class SearchServiceException(SearchException):
    pass
