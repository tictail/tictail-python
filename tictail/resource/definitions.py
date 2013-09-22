"""
tictail.resource.definitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Definitions for all API endpoints and their corresponding instances.

"""


from .base import (Resource,
                   ListableResource,
                   DeletableResource,
                   CreatableResource,
                   Instance,
                   DeletableInstance)


class Follower(DeletableInstance):
    pass


class Followers(ListableResource, DeletableResource, CreatableResource):
    endpoint = 'followers'
    instance = Follower


class Product(Instance):
    pass


class Products(ListableResource):
    endpoint = 'products'
    instance = Product


class Card(Instance):
    pass


class Cards(CreatableResource):
    endpoint = 'cards'
    instance = Card


class Customer(Instance):
    pass


class Customers(ListableResource):
    endpoint = 'customers'
    instance = Customer


class Order(Instance):
    pass


class Orders(ListableResource):
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


class Stores(Resource):
    endpoint = 'stores'
    instance = Store


class Me(Resource):
    endpoint = 'me'
    instance = Store

    def get(self):
        return self.request('GET', self.uri)
