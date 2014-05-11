# -*- coding: utf-8 -*-
import pytest

from tictail import Tictail
from tictail.client import DEFAULT_CONFIG
from tictail.resource import Cards


class TestClient(object):

    def test_construction(self, test_token, client):
        assert client.access_token == test_token
        assert client.transport is not None
        assert client.config is not None
        assert client.config == DEFAULT_CONFIG

    def test_make_transport(self, test_token, client):
        transport = client._make_transport()
        assert transport.config == DEFAULT_CONFIG
        assert transport.access_token == test_token

    def test_make_config(self, client):
        config = client._make_config({
            'version': 2,
            'base': 'test.foo.bar'
        })
        assert config['version'] == 2
        assert config['base'] == 'test.foo.bar'

        config = client._make_config(None)
        assert config == DEFAULT_CONFIG

    def test_config_override_via_constructor(self):
        client = Tictail('test', {
            'version': 2
        })
        assert client.config['version'] == 2
        assert client.config['base'] == DEFAULT_CONFIG['base']

    def test_make_store_subresource(self, client):
        with pytest.raises(ValueError):
            client._make_store_subresource(Cards, None)

        resource = client._make_store_subresource(Cards, 1)
        assert resource.uri == '/stores/1/cards'

    @pytest.mark.parametrize('method,expected_uri', [
        ('followers', '/stores/1/followers'),
        ('cards', '/stores/1/cards'),
        ('customers', '/stores/1/customers'),
        ('products', '/stores/1/products'),
        ('orders', '/stores/1/orders'),
    ])
    def test_default_factories(self, client, method, expected_uri):
        shortcut = getattr(client, method)
        resource = shortcut(1)
        assert resource.uri == expected_uri
