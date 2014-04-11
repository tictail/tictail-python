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


class Theme(Instance):
    pass


class Themes(Collection, Retrievable):
    endpoint = 'theme'
    instance = Theme

    @property
    def _name(self):
        # Themes are exposed as a singleton collection on a store, under the
        # `theme` property.
        return 'theme'


class Category(Instance):
    pass


class Categories(Collection, Listable):
    endpoint = 'categories'
    instance = Category


class Store(Instance):
    subresources = [
        Cards,
        Products,
        Customers,
        Followers,
        Orders,
        Themes,
        Categories
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
    'Customer', 'Customers', 'Order', 'Orders', 'Theme', 'Themes',
    'Category', 'Categories', 'Store', 'Stores', 'Me'
]
