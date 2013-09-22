"""
tictail.transport
~~~~~~~~~~~~~~~~~

Strategies for communication with the API. For now, communication is only
done via HTTP via the `requests` library. For documentation on `requests`,
please visit: http://docs.python-requests.org/en/latest/.

"""

import sys

from .version import __version__
from .importer import json, requests
from .errors import (ApiConnectionError,
                     ApiError,
                     ValidationError,
                     Forbidden,
                     NotFound,
                     BadRequest,
                     ServerError)


class RequestsHttpTransport(object):
    """Handles communication and data mungling.

    Internally, it uses `requests` to issue http requests to the various
    endpoints, and only speaks JSON.

    """
    def __init__(self, access_token, config):
        self.access_token = access_token
        self.config = config

    def _make_abs_uri(self, uri):
        """Makes an absolute API uri using the API base and protocol."""
        api_base_url = self.config.api_base_url
        api_version = "v{}".format(self.config.api_version)
        protocol = self.config.protocol
        return "{}://{}/{}/{}".format(protocol, api_base_url, api_version, uri)

    def _make_auth(self):
        """Returns an oauth2.0 tuple as expected by `requests`."""
        return ('Bearer', self.access_token)

    def _utf8(self, value):
        if isinstance(value, unicode) and sys.version_info < (3, 0):
            return value.encode('utf-8')
        else:
            return value

    def json_encode(self, data):
        return json.dumps(data)

    def get(self, uri, params=None):
        """Issues a GET request.

        :param uri: resource uri.
        :param params: query parameters.

        """
        return self.handle_request('get', uri, params=params)

    def post(self, uri, params=None, data=None):
        """Issues a POST request.

        :param uri: resource uri.
        :param params: query parameters.
        :param data: dictionary representing a JSON body.

        """
        return self.handle_request('post', uri, params=params, data=data)

    def delete(self, uri, params=None):
        """Issues a DELETE request.

        :param uri: resource uri.
        :param params: query parameters.

        """
        return self.handle_request('delete', uri, params=params)

    def handle_request(self, method, uri, params=None, data=None):
        """The bread and butter of this class. Issues a HTTP requests and takes
        care of all errors. Returns the JSON-decoded data and the status code.

        :param method: the HTTP method to use.
        :param uri: the uri to fetch.
        :param params: query parameters.
        :param data: request body contents.

        """
        method = method.lower()

        # make sure we're using an allowed http method.
        allowed_methods = self.config.allowed_http_methods
        assert method in allowed_methods, "`{}` is currently not allowed".format(method)

        data = self.json_encode(data)
        abs_uri = self._make_abs_uri(uri)
        auth = self._make_auth()
        verify_ssl_certs = self.config.verify_ssl_certs
        headers = {
            'accept': 'application/json;charset=UTF-8',
            'accept-charset': 'UTF-8',
            'content-type': 'application/json',
            'user-agent': "Tictail Python {}".format(__version__)
        }
        timeout = self.config.timeout

        try:
            resp = requests.request(method, abs_uri,
                                    params=params,
                                    data=data,
                                    auth=auth,
                                    headers=headers,
                                    timeout=timeout,
                                    verify=verify_ssl_certs)

            # `requests` will store an `HTTPError` if one happened.
            resp.raise_for_status()

            content = resp.json()
            return content, resp.status_code
        except requests.exceptions.ConnectionError as ce:
            self.handle_connection_error(ce)
        except requests.exceptions.HTTPError as he:
            self.handle_http_error(he)
        except ValueError as ve:
            # for a `ValueError` to occur, it means that the API did not return
            # valid JSON as expected, even though no error occured.
            if 'JSON object' in ve.message:
                content_type = resp.headers['content-type']
                message = ("The API should return JSON, but there was a problem "
                           "decoding it. The response content-type was: `{}`. "
                           "Please contact support@tictail.com if the problem "
                           "persists.".format(content_type))
                raise ApiError(message, resp.status_code, resp.text)
            else:
                raise ve

    def handle_connection_error(self, err):
        raise ApiConnectionError(err.message)

    def handle_http_error(self, err):
        resp = err.response
        status_code = resp.status_code
        try:
            json = resp.json()
            message = json.get('message')
            # TODO: this should be fixed in the API, responses should be consistent.
            if message is None:
                message = json.get('error')
        except ValueError:
            # if we can't read JSON from the error response, then something is
            # obviously wrong.
            # check for Bad Gateway errors first, otherwise just show a generic
            # error message.
            if status_code == 502:
                message = ('It seems that the API is unreachable. Please contact '
                           'support@tictail.com if the problem persists.')
            else:
                message = ('An unexpected error occured. Please contact support@tictail.com '
                           'if the problem persists.')

        # raise appropriate exception for 400, 403, 404 and 422, and a generic error for
        # all other error codes.
        if status_code == 400:
            err_cls = BadRequest
        elif status_code == 403:
            err_cls = Forbidden
        elif status_code == 404:
            err_cls = NotFound
        elif status_code == 422:
            err_cls = ValidationError
        else:
            err_cls = ServerError

        raise err_cls(message, status_code, resp.text)
