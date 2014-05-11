"""
tictail.errors
~~~~~~~~~~~~~~

Custom exception classes.

"""
from tictail.importer import json


class ApiConnectionError(Exception):
    """Thrown if there was a problem with connecting to the API."""
    pass


class ApiError(Exception):
    """Base class for all HTTP errors."""
    def __init__(self, message, status, raw, json=None):
        """Initializes the base `ApiError`.

        :param message: The error message.
        :param status: The HTTP status code.
        :param raw: The raw body of the response.
        :param json: An optional dict if the error could be decoded into JSON.

        """
        super(ApiError, self).__init__(message)
        self.status = status
        self.raw = raw
        self.json = json

    def __repr__(self):
        try:
            content = json.dumps(self.json, indent=2) if self.json else self.raw
        except ValueError:
            content = self.raw
        return "{0} ({1}): {2}".format(self.message, self.status, content)

    def __str__(self):
        return repr(self)


class Forbidden(ApiError):
    """Thrown for 403 errors, i.e auth issues."""
    pass


class NotFound(ApiError):
    """Thrown for 404 errors."""
    pass


class BadRequest(ApiError):
    """Thrown for 400 errors."""
    pass


class ServerError(ApiError):
    """Thrown for all errors apart from 400, 403, 404 and 422."""
    pass


__all__ = [
    'ApiError', 'ApiConnectionError', 'Forbidden', 'NotFound',
    'BadRequest', 'ServerError'
]
