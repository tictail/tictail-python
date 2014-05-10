"""
tictail.resource.definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Definitions for all API endpoints and their corresponding instances.

"""

from .base import (Collection,
                   Resource,
                   Get,
                   GetById,
                   List,
                   Create,
                   Delete,
                   DeleteById)


class Follower(Resource, Delete):
    endpoint = 'followers'


class Followers(Collection, List, Create, DeleteById):
    resource = Follower


class Product(Resource, Get):
    endpoint = 'products'


class Products(Collection, GetById, List):
    resource = Product

    def format_params(self, **params):
        if 'categories' in params:
            params['categories'] = ','.join(params['categories'])
        return params


class Card(Resource):
    endpoint = 'cards'


class Cards(Collection, Create):
    resource = Card


class Customer(Resource, Get):
    endpoint = 'customers'


class Customers(Collection, GetById, List):
    resource = Customer


class Order(Resource, GetById):
    endpoint = 'orders'


class Orders(Collection, GetById, List):
    resource = Order

    def format_params(self, **params):
        if 'modified_before' in params:
            params['modified_before'] = params['modified_before'].isoformat()
        if 'modified_after' in params:
            params['modified_after'] = params['modified_after'].isoformat()
        return params


class Theme(Resource, Get):
    endpoint = 'theme'
    singleton = True


class Category(Resource):
    endpoint = 'categories'


class Categories(Collection, List):
    resource = Category


class Store(Resource, Get):
    endpoint = 'stores'
    subresources = [
        Cards,
        Products,
        Customers,
        Followers,
        Orders,
        Theme,
        Categories
    ]


class Stores(Collection, GetById):
    resource = Store


class Me(Store, Get):
    endpoint = 'me'
    singleton = True

    def instantiate_from_data(self, data):
        return Store(self.transport, data=data)


__all__ = [
    'Follower', 'Followers', 'Product', 'Products', 'Card', 'Cards',
    'Customer', 'Customers', 'Order', 'Orders', 'Theme', 'Category',
    'Categories', 'Store', 'Stores', 'Me'
]
