"""
tictail.resource.definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Definitions for all API endpoints and their corresponding instances.

"""

from .base import (Collection,
                   Instance,
                   Retrievable,
                   Listable,
                   Creatable,
                   Deletable)


class Follower(Instance, Deletable):
    pass


class Followers(Collection, Listable, Creatable):
    endpoint = 'followers'
    instance = Follower


class Product(Instance):
    pass


class Products(Collection, Retrievable, Listable):
    endpoint = 'products'
    instance = Product


class Card(Instance):
    pass


class Cards(Collection, Creatable):
    endpoint = 'cards'
    instance = Card


class Customer(Instance):
    pass


class Customers(Collection, Retrievable, Listable):
    endpoint = 'customers'
    instance = Customer


class Order(Instance):
    pass


class Orders(Collection, Retrievable, Listable):
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


class Stores(Collection, Retrievable):
    endpoint = 'stores'
    instance = Store


class Me(Collection, Retrievable):
    """This is a convenient alias to the /stores collection that returns the
    currently authenticated store without needing an identifier.

    """
    endpoint = 'me'
    instance = Store

    def make_instance(self, data):
        return self.instance(data, 'stores', self.transport)


__all__ = [
    'Follower', 'Followers', 'Product', 'Products', 'Card', 'Cards',
    'Customer', 'Customers', 'Order', 'Orders', 'Store', 'Stores', 'Me'
]
