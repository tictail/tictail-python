# -*- coding: utf-8 -*-
import pytest
from mock import MagicMock

from tictail.version import __version__
from tictail.importer import json, requests
from tictail.errors import ApiConnectionError, Forbidden, ServerError, ApiError


ConnectionError = requests.exceptions.ConnectionError
HTTPError = requests.exceptions.HTTPError


class TestTransport(object):

    def test_make_abs_url(self, transport):
        base = transport.config['base']
        protocol = transport.config['protocol']
        version = transport.config['version']

        # Leading and trailing slashes should not affect result.
        abs_uri = transport._make_abs_uri('/stores')
        assert abs_uri == '{0}://{1}/v{2}/stores'.format(protocol, base, version)
        abs_uri = transport._make_abs_uri('stores')
        assert abs_uri == '{0}://{1}/v{2}/stores'.format(protocol, base, version)
        abs_uri = transport._make_abs_uri('stores/')
        assert abs_uri == '{0}://{1}/v{2}/stores'.format(protocol, base, version)

    def test_utf8(self, transport):
        value = u'ƃäｃòԉ'
        assert transport._utf8(value) == value.encode('utf-8')
        assert transport._utf8('bacon') == 'bacon'

    @pytest.mark.parametrize('call_params', [
        ('GET', 'foo', {'params': u'Båｃòԉ'}),
        ('POST', 'foo', {'params': 'bar', 'data': {'foo': u'Båｃòԉ'}}),
        ('DELETE', 'foo', {'params': 'bar'}),
        ('PUT', 'foo', {'params': 'bar', 'data': {'foo': 'bar'}})
    ])
    def test_http_methods(self, monkeypatch, transport, call_params):
        mock = MagicMock()
        method, uri, kwargs = call_params

        monkeypatch.setattr(transport, 'handle_request', mock)
        inst_method = getattr(transport, method.lower())
        inst_method(uri, **kwargs)

        mock.assert_called_with(method, uri, **kwargs)

    @pytest.mark.parametrize('call_params', [
        ('GET', 'foo', {'params': u'Båｃòԉ'}),
        ('POST', 'foo', {'params': 'bar', 'data': {'foo': u'Båｃòԉ'}}),
        ('DELETE', 'foo', {'params': 'bar'}),
        ('PUT', 'foo', {'params': 'bar', 'data': {'foo': 'bar'}})
    ])
    def test_handle_request(self, monkeypatch, transport, call_params):
        mock = MagicMock()
        method, uri, kwargs = call_params

        monkeypatch.setattr('tictail.transport.requests.request', mock)

        base = transport.config['base']
        protocol = transport.config['protocol']
        version = transport.config['version']
        headers = {
            'authorization': 'Bearer test',
            'accept': 'application/json;charset=UTF-8',
            'accept-charset': 'UTF-8',
            'content-type': 'application/json',
            'user-agent': "Tictail Python {0}".format(__version__)
        }
        params = kwargs.get('params')
        data = kwargs.get('data')
        if data is not None:
            data = json.dumps(data)

        content, status = transport.handle_request(method, uri, **kwargs)
        mock.assert_called_with(
            method.lower(),
            "{0}://{1}/v{2}/{3}".format(protocol, base, version, uri),
            params=params,
            data=data,
            headers=headers,
            timeout=20,
            verify=True
        )

    @pytest.mark.parametrize('input', [
        (ConnectionError, '_handle_connection_error'),
        (HTTPError, '_handle_http_error'),
        (Exception, '_handle_unexpected_error')
    ])
    def test_handle_request_error(self, monkeypatch, transport, input):
        error_cls, error_handler = input
        error = error_cls()

        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock(side_effect=error)
        error.response = mock_resp

        mock_request = MagicMock(return_value=mock_resp)
        mock_error_handler = MagicMock()

        monkeypatch.setattr(transport, error_handler, mock_error_handler)
        monkeypatch.setattr('tictail.transport.requests.request', mock_request)

        transport.handle_request('GET', 'foo')
        mock_error_handler.assert_called_with(error)

    def test_handle_connection_error(self, transport):
        error = ConnectionError('error message')
        with pytest.raises(ApiConnectionError):
            transport._handle_connection_error(error)

    @pytest.mark.parametrize('input', [
        (403, Forbidden),
        (500, ServerError)
    ])
    def test_handle_http_error(self, transport, input):
        status, error_cls = input

        error_body = {
            'message': 'error message',
            'support_email': 'support@tictail.com'
        }

        mock = MagicMock()
        mock.status_code = status
        mock.json.return_value = error_body

        error = HTTPError('error message', status)
        error.response = mock

        with pytest.raises(error_cls) as excinfo:
            transport._handle_http_error(error)

        err = excinfo.value
        assert err.message == 'error message'
        assert err.status == status
        assert err.response == json.dumps(error_body)

    @pytest.mark.parametrize('input', [
        (502, 'API is unreachable'),
        (509, 'unexpected error')
    ])
    def test_handle_http_error_no_json_response(self, transport, input):
        status, error_string = input

        mock = MagicMock()
        mock.status_code = status
        mock.json.side_effect = ValueError

        error = HTTPError('error message', status)
        error.response = mock

        with pytest.raises(ServerError) as excinfo:
            transport._handle_http_error(error)

        err = excinfo.value
        assert error_string in err.message
        assert err.status == status
        assert err.response is None

    def test_handle_unexpected_error(self, transport):
        mock = MagicMock()
        mock.status_code = 500
        mock.json.side_effect = ValueError
        mock.text = 'text response'
        mock.headers = {'content-type': 'text/html'}

        error = ValueError('No JSON object could be decoded', 500)
        error.response = mock

        with pytest.raises(ApiError) as excinfo:
            transport._handle_unexpected_error(error)

        err = excinfo.value
        assert 'should return JSON' in err.message
        assert 'text/html' in err.message
        assert err.status == 500
        assert err.response is 'text response'
