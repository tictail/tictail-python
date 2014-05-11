# -*- coding: utf-8 -*-
from datetime import datetime
import pytest

from tictail import Tictail
from tictail.resource import (Store,
                              Product,
                              Follower,
                              Theme,
                              Category,
                              Order,
                              Customer)


@pytest.fixture(scope='module')
def me(test_token):
    # We need to recreate the client here since we need a broader session than
    # the `client` fixture (module vs function).
    client = Tictail(test_token)
    return client.me()


class TestStore(object):

    def test_me(self, me):
        assert isinstance(me, Store)
        assert me.id == 'KGu'
        assert me.name == 'Tictail Python'

    def test_get_store_by_id(self, client):
        collection = client.stores()
        store = collection.get('KGu')
        assert isinstance(store, Store)
        assert store.id == 'KGu'
        assert store.name == 'Tictail Python'

        assert 'name' in store.data_keys()
        assert 'Tictail Python' in store.data_values()


class TestProduct(object):

    def test_get(self, client, me):
        collection = client.products(store='KGu')
        product = collection.get('9cVh')
        assert isinstance(product, Product)
        assert product.id == '9cVh'
        assert product.title == 'Tictail Python Test Product'

        product = me.products.get('9cVh')
        assert isinstance(product, Product)
        assert product.id == '9cVh'
        assert product.title == 'Tictail Python Test Product'

        assert 'title' in product.data_keys()
        assert 'Tictail Python Test Product' in product.data_values()

    def test_get_all(self, client, me):
        collection = client.products(store='KGu')
        products = collection.all()
        assert len(products) == 1

        products = me.products.all()
        assert len(products) == 1

        product = products[0]
        assert isinstance(product, Product)
        assert product.id == '9cVh'
        assert product.title == 'Tictail Python Test Product'

    def test_get_all_from_category(self, me):
        products = me.products.all(categories=['47dv'])
        assert len(products) == 1

        product = products[0]
        assert isinstance(product, Product)
        assert product.id == '9cVh'
        assert product.title == 'Tictail Python Test Product'

    def test_get_all_from_non_existing_category(self, me):
        products = me.products.all(categories=['47du'])
        assert len(products) == 0


class TestFollower(object):

    def test_create_and_delete(self, client, me):
        collection = client.followers(store='KGu')
        follower = collection.create({'email': 'm8r-fixc0m@mailinator.com'})
        assert isinstance(follower, Follower)
        assert follower.email == 'm8r-fixc0m@mailinator.com'
        assert collection.delete(follower.id)

        follower = me.followers.create({'email': 'm8r-fixc0m@mailinator.com'})
        assert isinstance(follower, Follower)
        assert follower.email == 'm8r-fixc0m@mailinator.com'
        assert collection.delete(follower.id)

    def test_get_all(self, client, me):
        collection = client.followers(store='KGu')
        followers = collection.all()
        assert len(followers) == 1

        followers = me.followers.all()
        assert len(followers) == 1

        follower = followers[0]
        assert isinstance(follower, Follower)
        assert follower.email == 'tictailpython@mailinator.com'

    def test_get_all_after(self, me):
        followers = me.followers.all(after='4EaL')
        assert not followers

    def test_get_all_before(self, me):
        followers = me.followers.all(before='4EaL')
        assert not followers


class TestTheme(object):

    def test_get(self, client, me):
        resource = client.theme(store='KGu')
        theme = resource.get()
        assert isinstance(theme, Theme)
        assert theme.id == 'ueg'

        theme = me.theme.get()
        assert isinstance(theme, Theme)
        assert theme.id == 'ueg'


class TestCategory(object):

    def test_get_all(self, client, me):
        collection = client.categories(store='KGu')
        categories = collection.all()
        assert len(categories) == 2

        categories = me.categories.all()
        assert len(categories) == 2

        first = categories[0]
        assert isinstance(first, Category)
        assert first.id == '47dv'
        assert first.title == 'Test Products'

        second = categories[1]
        assert isinstance(second, Category)
        assert second.id == '47dw'
        assert second.title == 'Nice Test Products'
        assert second.parent_id == first.id


class TestOrder(object):

    def test_get(self, client, me):
        collection = client.orders(store='KGu')
        order = collection.get('aFQX')
        assert isinstance(order, Order)
        assert order.id == 'aFQX'
        assert order.price == 0
        assert order.transaction['status'] == 'paid'

    def test_get_all(self, client, me):
        collection = client.orders(store='KGu')
        orders = collection.all()
        assert len(orders) == 1

        orders = me.orders.all()
        assert len(orders) == 1

        order = orders[0]
        assert isinstance(order, Order)
        assert order.id == 'aFQX'
        assert order.price == 0
        assert order.transaction['status'] == 'paid'

    def test_get_all_before(self, me):
        orders = me.orders.all(after='aFQX')
        assert len(orders) == 0

    def test_get_all_after(self, me):
        orders = me.orders.all(before='aFQX')
        assert len(orders) == 0

    def test_get_all_modified_before(self, me):
        orders = me.orders.all(modified_before='2014-06-10T23:07:49.674233')
        assert len(orders) == 1
        assert orders[0].id == 'aFQX'

    def test_get_all_modified_after(self, me):
        orders = me.orders.all(modified_after='2014-04-10T23:07:49.674233')
        assert len(orders) == 1
        assert orders[0].id == 'aFQX'

    def test_get_all_modified_before_as_datetime(self, me):
        orders = me.orders.all(modified_before=datetime.utcnow())
        assert len(orders) == 1
        assert orders[0].id == 'aFQX'


class TestCustomer(object):

    def test_get(self, client, me):
        collection = client.customers(store='KGu')
        customer = collection.get('4EbF')
        assert isinstance(customer, Customer)
        assert customer.id == '4EbF'
        assert customer.email == 'BubGnome@mailinator.com'

        customer = me.customers.get('4EbF')
        assert isinstance(customer, Customer)
        assert customer.id == '4EbF'
        assert customer.email == 'BubGnome@mailinator.com'

    def test_get_all(self, client, me):
        collection = client.customers(store='KGu')
        customers = collection.all()
        assert len(customers) == 1

        customers = me.customers.all()
        assert len(customers) == 1

        customer = customers[0]
        assert isinstance(customer, Customer)
        assert customer.id == '4EbF'
        assert customer.email == 'BubGnome@mailinator.com'

    def get_all_before(self):
        customers = me.customers.get(before='4EbF')
        assert len(customers) == 0

    def get_all_after(self):
        customers = me.customers.get(after='4EbF')
        assert len(customers) == 0
