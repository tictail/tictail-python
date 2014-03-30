"""
tictail.resource.definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Definitions for all API endpoints and their corresponding instances.

"""

from .base import (Collection,
                   Instance,
                   Listable,
                   Creatable,
                   Deletable)


class Follower(Instance, Deletable):
    pass


class Followers(Collection, Creatable, Deletable):
    endpoint = 'followers'
    instance = Follower


class Product(Instance):
    pass


class Products(Collection, Listable):
    endpoint = 'products'
    instance = Product


class Card(Instance):
    pass


class Cards(Collection, Creatable):
    endpoint = 'cards'
    instance = Card


class Customer(Instance):
    pass


class Customers(Collection, Listable):
    endpoint = 'customers'
    instance = Customer


class Order(Instance):
    pass


class Orders(Collection, Listable):
    endpoint = 'orders'
    instance = Order


class Store(Instance):
    subresources = [
        Cards,
        Products,
        Customers,
        Followers,
        Orders
    ]


class Stores(Collection):
    endpoint = 'stores'
    instance = Store


class Me(Collection):
    """This is a convenient alias to the /stores collection that returns the
    currently authenticated store without needing an identifier.

    """
    endpoint = 'me'
    instance = Store

    def get(self):
        return self.request('GET', self.uri)


__all__ = [
    'Follower', 'Followers', 'Product', 'Products', 'Card', 'Cards',
    'Customer', 'Customers', 'Order', 'Orders', 'Store', 'Stores', 'Me'
]
