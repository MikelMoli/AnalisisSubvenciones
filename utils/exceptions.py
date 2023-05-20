class IncorrectAPIResponseException(Exception):
    """If API response code is not 200 then this error will be risen"""


class NoTotalItemsCountAttributeException(Exception):
    """API response has no 'totalItemsCount' attribute."""


class MaxRetriesReachesException(Exception):
    """ Request have been retried the specified times and haven't succeed """
