"""
tictail.client
~~~~~~~~~~~~~~

"""

import copy

from .transport import RequestsHttpTransport
from .resource import (Store,
                       Followers,
                       Cards,
                       Customers,
                       Products,
                       Orders,
                       Stores,
                       Theme,
                       Categories,
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
DEFAULT_TIMEOUT = 20

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

    def _make_store_subresource(self, resource_cls, store_id):
        if store_id is None:
            raise ValueError('`store_id` cannot be None')
        parent = "{0}/{1}".format(Store.endpoint, store_id)
        return resource_cls(self.transport, parent=parent)

    def me(self):
        """Alias for getting the store for which the access token you are using
        is valid.

        >>> tt = Tictail('token')
        >>> tt.me()
        Store({...})

        """
        return Me(self.transport).get()

    # ====== Resource factories ======= #

    def stores(self):
        """Returns a `Stores` collection."""
        return Stores(self.transport)

    def followers(self, store=None):
        """Returns a `Followers` collection.

        :param store: A store id.

        """
        return self._make_store_subresource(Followers, store)

    def cards(self, store=None):
        """Returns a `Cards` collection.

        :param store: A store id.

        """
        return self._make_store_subresource(Cards, store)

    def customers(self, store=None):
        """Returns a `Customers` collection.

        :param store: A store id.

        """
        return self._make_store_subresource(Customers, store)

    def products(self, store=None):
        """Returns a `Products` collection.

        :param store: A store id.

        """
        return self._make_store_subresource(Products, store)

    def orders(self, store=None):
        """Returns an `Orders` collection.

        :param store: A store id.

        """
        return self._make_store_subresource(Orders, store)

    def theme(self, store=None):
        """Returns a `Theme` resource.

        :param store: A store id.

        """
        return self._make_store_subresource(Theme, store)

    def categories(self, store=None):
        """Returns a `Categories` collection.

        :param store: A store id.

        """
        return self._make_store_subresource(Categories, store)
