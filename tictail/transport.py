"""
tictail.transport
~~~~~~~~~~~~~~~~~

Strategies for communication with the API. For now, communication is only
done via HTTP via the `requests` library. For documentation on `requests`,
please visit: http://docs.python-requests.org/en/latest/.

"""

from .version import __version__
from .importer import json, requests
from .errors import (ApiConnectionError,
                     ApiError,
                     Forbidden,
                     NotFound,
                     BadRequest,
                     ServerError)


ConnectionError = requests.exceptions.ConnectionError
HTTPError = requests.exceptions.HTTPError


class RequestsHttpTransport(object):
    """Handles communication and data mungling.

    Internally, it uses `requests` to issue http requests to the various
    endpoints, and only speaks JSON.

    """

    def __init__(self, access_token, config):
        self.access_token = access_token
        self.config = config

    def _make_abs_uri(self, uri):
        """Makes an absolute API uri using the API base and protocol.

        :param uri: The URI to absolutize.

        """
        base = self.config['base']
        version = "v{0}".format(self.config['version'])
        protocol = self.config['protocol']
        if uri[0] == '/':
            uri = uri[1:]
        if uri[-1] == '/':
            uri = uri[:-1]
        return "{0}://{1}/{2}/{3}".format(protocol, base, version, uri)

    def _utf8(self, value):
        return value.encode('utf-8') if isinstance(value, unicode) else value

    def _handle_connection_error(self, err):
        raise ApiConnectionError(err.message)

    def _handle_http_error(self, err):
        resp = err.response
        status_code = resp.status_code

        try:
            resp_json = resp.json()
            message = resp_json.get('message')
        except ValueError:
            # If we can't read JSON from the error response, then something is
            # obviously wrong. Check for Bad Gateway errors first, otherwise
            # just show a generic error message and raise a `ServerError`.
            if status_code == 502:
                message = ('It seems that the API is unreachable. Please contact '
                           'Tictail Support if the problem persists.')
            else:
                message = ('An unexpected error occured. Please contact Tictail '
                           'Support if the problem persists.')

            raise ServerError(message, status_code, resp.text)

        # Raise appropriate exception for 400, 403, 404, and a generic error
        # for all other error codes.
        if status_code == 400:
            err_cls = BadRequest
        elif status_code == 403:
            err_cls = Forbidden
        elif status_code == 404:
            err_cls = NotFound
        else:
            err_cls = ServerError

        raise err_cls(message, status_code, resp.text, json=resp_json)

    def _handle_unexpected_error(self, err):
        if isinstance(err, ValueError):
            resp = err.response
            # For a `ValueError` to occur, it might mean that the API did not
            # return valid JSON as expected, even though no HTTP error occured.
            if 'JSON object' in str(err):
                content_type = resp.headers['content-type']
                message = ("The API should return JSON, but there was a problem "
                           "decoding it. The response content-type was: `{0}`."
                           .format(content_type))
                raise ApiError(message, resp.status_code, resp.text)

        # Just raise the exception if we can't handle it in a better way.
        raise err

    def get(self, uri, params=None):
        """Issues a GET request.

        :param uri: The resource URI.
        :param params: Query parameters as dict or bytes.

        """
        return self.handle_request('GET', uri, params=params)

    def post(self, uri, params=None, data=None):
        """Issues a POST request.

        :param uri: The resource URI.
        :param params: Query parameters as dict or bytes.
        :param data: A dictionary representing a JSON body.

        """
        return self.handle_request('POST', uri, params=params, data=data)

    def put(self, uri, params=None, data=None):
        """Issues a PUT request.

        :param uri: The resource URI.
        :param params: Query parameters as dict or bytes.
        :param data: A dictionary representing a JSON body.

        """
        return self.handle_request('PUT', uri, params=params, data=data)

    def delete(self, uri, params=None):
        """Issues a DELETE request.

        :param uri: The resource URI.
        :param params: Query parameters as dict or bytes.

        """
        return self.handle_request('DELETE', uri, params=params)

    def handle_request(self, method, uri, params=None, data=None):
        """The bread and butter of this class. Issues a HTTP requests and takes
        care of all errors. Returns the JSON-decoded data and the status code.

        :param method: The HTTP method to use.
        :param uri: The URI to fetch.
        :param params: Query parameters as dict or bytes.
        :param data: Request body contents.

        """
        method = method.lower()

        if data is not None:
            data = json.dumps(data)

        abs_uri = self._make_abs_uri(uri)
        verify_ssl_certs = self.config['verify_ssl_certs']

        headers = {
            'authorization': "Bearer {0}".format(self.access_token),
            'accept': 'application/json;charset=UTF-8',
            'accept-charset': 'UTF-8',
            'content-type': 'application/json',
            'user-agent': "Tictail Python {0}".format(__version__)
        }

        timeout = self.config['timeout']

        try:
            resp = requests.request(method, abs_uri,
                                    params=params,
                                    data=data,
                                    headers=headers,
                                    timeout=timeout,
                                    verify=verify_ssl_certs)

            # `requests` will store an `HTTPError` if one happened.
            resp.raise_for_status()

            content = resp.json() if resp.text else None
            return content, resp.status_code
        except ConnectionError as ce:
            self._handle_connection_error(ce)
        except HTTPError as he:
            self._handle_http_error(he)
        except Exception as e:
            e.response = resp
            self._handle_unexpected_error(e)
