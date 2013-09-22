"""
tictail.client
~~~~~~~~~~~~~~

"""

from .transport import RequestsHttpTransport
from .resource.definitions import (Me,
                                   Stores,
                                   Products,
                                   Customers,
                                   Followers,
                                   Cards,
                                   Orders)


# API version supported by these bindings.
API_VERSION = 1

# default HTTP protocol to use.
DEFAULT_PROTOCOL = 'https'

# base API url.
API_BASE_URL = 'api.tictail.com'

# methods we currently allow via the API.
ALLOWED_HTTP_METHODS = frozenset(['get', 'post', 'delete'])

# whether `requests` should verify SSL certificates.
VERIFY_SSL_CERTS = True

# default socket timeout.
DEFAULT_TIMEOUT = 10


default_config = {
    'api_version': API_VERSION,
    'protocol': DEFAULT_PROTOCOL,
    'api_base_url': API_BASE_URL,
    'verify_ssl_certs': VERIFY_SSL_CERTS,
    'timeout': DEFAULT_TIMEOUT,
    'allowed_http_methods': ALLOWED_HTTP_METHODS
}


class Config(dict):
    def __init__(self, d):
        self.__dict__.update(d)

    def update(self, d):
        self.__dict__.update(d)

    def __repr__(self):
        import pprint
        return "Config({})".format(pprint.pformat(self.__dict__))


class Tictail(object):

    def __init__(self, access_token, config=None, transport=None):
        self.access_token = access_token
        self.config = self._make_config(config)

        if transport is None:
            transport = self._make_transport()
        self.transport = transport

        # root endpoints.
        self.stores = Stores(self.transport)

    def _make_config(self, config_override):
        config = Config(default_config)
        if config_override:
            config.update(config_override)
        return config

    def _make_transport(self):
        return RequestsHttpTransport(self.access_token, self.config)

    def _make_shortcut(self, resource_cls, store_id):
        if store_id is None:
            raise Exception('blah')
        prefix = "{}/{}".format(Stores.endpoint, store_id)
        return resource_cls(self.transport, endpoint_prefix=prefix)

    def me(self):
        """Shortcut for getting /me."""
        me = Me(self.transport)
        return me.get()

    def followers(self, store=None):
        return self._make_shortcut(Followers, store)

    def cards(self, store=None):
        return self._make_shortcut(Cards, store)

    def customers(self, store=None):
        return self._make_shortcut(Customers, store)

    def products(self, store=None):
        return self._make_shortcut(Products, store)

    def orders(self, store=None):
        return self._make_shortcut(Orders, store)
