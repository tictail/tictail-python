import pytest

from tictail import Tictail
from tictail.client import DEFAULT_CONFIG
from tictail.resource import Cards


class TestClient(object):

    @property
    def client(self):
        return Tictail('test')

    def test_construction(self):
        assert self.client.access_token == 'test'
        assert self.client.transport is not None
        assert self.client.config is not None
        assert self.client.config == DEFAULT_CONFIG

    def test_make_config(self):
        config = self.client._make_config({
            'api_version': 2,
            'base_url': 'test.foo.bar'
        })
        assert config['api_version'] == 2
        assert config['base_url'] == 'test.foo.bar'

        config = self.client._make_config(None)
        assert config == DEFAULT_CONFIG

    def test_config_override_via_constructor(self):
        client = Tictail('test', {
            'api_version': 2
        })
        assert client.config['api_version'] == 2
        assert client.config['base_url'] == DEFAULT_CONFIG['base_url']

    def test_make_shortcut(self):
        with pytest.raises(ValueError):
            self.client._make_shortcut(Cards, None)

        resource = self.client._make_shortcut(Cards, 1)
        assert resource.uri == 'stores/1/cards'

    @pytest.mark.parametrize('method,expected_uri', [
        ('followers', 'stores/1/followers'),
        ('cards', 'stores/1/cards'),
        ('customers', 'stores/1/customers'),
        ('products', 'stores/1/products'),
        ('orders', 'stores/1/orders'),
    ])
    def test_default_shortcuts(self, method, expected_uri):
        shortcut = getattr(self.client, method)
        resource = shortcut(1)
        assert resource.uri == expected_uri
