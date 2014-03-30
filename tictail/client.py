"""
tictail.client
~~~~~~~~~~~~~~

"""
import copy

from .transport import RequestsHttpTransport
from .resource import (Followers,
                       Cards,
                       Customers,
                       Products,
                       Orders,
                       Stores,
                       Me)


# API version supported by these bindings.
VERSION = 1

# Default HTTP protocol to use.
DEFAULT_PROTOCOL = 'https'

# Base API URL.
BASE = 'api.tictail.com'

# Whether `requests` should verify SSL certificates.
VERIFY_SSL_CERTS = True

# Default socket timeout.
DEFAULT_TIMEOUT = 10

# Defauly applied configuration.
DEFAULT_CONFIG = {
    'version': VERSION,
    'protocol': DEFAULT_PROTOCOL,
    'base': BASE,
    'verify_ssl_certs': VERIFY_SSL_CERTS,
    'timeout': DEFAULT_TIMEOUT
}


class Client(object):

    def __init__(self, access_token, config=None, transport=None):
        self.access_token = access_token
        self.config = self._make_config(config)

        if transport is None:
            transport = self._make_transport()

        self.transport = transport

    def _make_config(self, config_override):
        config = copy.deepcopy(DEFAULT_CONFIG)
        if config_override:
            config.update(config_override)
        return config

    def _make_transport(self):
        return RequestsHttpTransport(self.access_token, self.config)

    def _make_shortcut(self, resource_cls, store_id):
        if store_id is None:
            raise ValueError('`store_id` cannot be None')
        prefix = "{}/{}".format(Stores.endpoint, store_id)
        return resource_cls(self.transport, endpoint_prefix=prefix)

    # ====== Root Endpoints ====== #

    @property
    def stores(self):
        return Stores(self.transport)

    @property
    def me(self):
        return Me(self.transport)

    # ====== Shortcuts ======= #

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
