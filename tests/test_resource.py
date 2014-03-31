# -*- coding: utf-8 -*-
import pytest
from mock import MagicMock

from tictail.resource.base import (Resource,
                                   Collection,
                                   Instance,
                                   Retrievable,
                                   Listable,
                                   Creatable,
                                   Deletable)


class TestResource(object):

    @pytest.mark.parametrize('input', [
        ('test', 200, {}),
        ('error', 500, {'params': 'foo', 'data': {'foo': 'bar'}})
    ])
    def test_request(self, monkeypatch, transport, input):
        exp_resp, exp_status, kwargs = input

        resource = Resource(transport)
        assert resource.transport is transport

        mock = MagicMock(return_value=(exp_resp, exp_status))
        monkeypatch.setattr(resource.transport, 'get', mock)

        resp, status = resource.request('GET', '/foo', **kwargs)
        assert resp == exp_resp
        assert status == exp_status
        mock.assert_called_with('/foo', **kwargs)

    @pytest.mark.parametrize('input,expected', [
        ('test', 'test'),
        ('/test', 'test'),
        ('test/', 'test'),
        ('/test/', 'test'),
        ('', ''),
        (None, None)
    ])
    def test_remove_slashes(self, transport, input, expected):
        resource = Resource(transport)
        assert resource._remove_slashes(input) == expected


class TestCollection(object):

    @pytest.mark.parametrize('input,expected', [
        (('test', None), '/test'),
        (('/test', None), '/test'),
        (('test/', None), '/test'),
        (('test', '/prefix'), '/prefix/test'),
        (('test', 'prefix/'), '/prefix/test'),
        (('test', 'prefix'), '/prefix/test')
    ])
    def test_uri(self, transport, input, expected):
        endpoint, prefix = input
        collection = Collection(transport)
        collection.endpoint = endpoint
        collection.prefix = prefix
        assert collection.uri == expected

    def test_make_instance(self, transport):
        collection = Collection(transport)
        collection.endpoint = 'test'
        collection.instance = Instance

        rv = collection.make_instance(dict(foo='bar'))
        assert isinstance(rv, Instance)
        rv.foo == 'bar'

        rv = collection.make_instance([
            dict(foo='bar'),
            dict(fooz='barz')
        ])
        assert isinstance(rv, list)
        assert isinstance(rv[0], Instance)
        assert isinstance(rv[1], Instance)
        assert rv[0].foo == 'bar'
        assert rv[1].fooz == 'barz'


class TestInstance(object):

    @pytest.mark.parametrize('input,expected', [
        (({}, 'parent'), ([], 'parent')),
        ((None, 'parent'), ([], 'parent')),
        (({'foo': 'bar'}, '/parent'), (['foo'], '/parent'))
    ])
    def test_construction(self, transport, input, expected):
        data, parent_uri = input
        exp_keys, exp_parent_uri = expected
        instance = Instance(data, parent_uri, transport)
        assert instance._data_keys == set(exp_keys)
        assert instance.parent_uri == exp_parent_uri
        for k, v in (data or {}).items():
            assert getattr(instance, k) == v

    def test_construction_with_subresources(self, transport):
        # Use these two collections as subresources.
        class Posts(Collection):
            pass
        class Comments(Collection):
            pass

        data = {'id': 1}
        instance = Instance(data, 'parent', transport)
        instance.subresources = [Posts, Comments]
        instance.instantiate_subresources()

        # Check that subresources were instantiated and named correctly.
        assert isinstance(instance.posts, Posts)
        assert isinstance(instance.comments, Comments)

        # Check that all other properties are correct.
        assert instance._data_keys == set(['id'])
        assert instance.parent_uri == 'parent'
        for k, v in data.items():
            assert getattr(instance, k) == v

        # Check that the subresources are included in the internal attributes.
        assert 'posts' in instance._internal_attrs
        assert 'comments' in instance._internal_attrs

        # Check that we are not exposing any internal attributes.
        to_dict = instance.to_dict()
        for attr in instance._internal_attrs:
            assert attr not in to_dict

    @pytest.mark.parametrize('input,expected', [
        ('parent', '/parent/1'),
        ('parent/1', '/parent/1/1'),
        ('/parent/1', '/parent/1/1'),
        ('/parent/1/', '/parent/1/1')
    ])
    def test_uri(self, transport, input, expected):
        data = {'id': 1}
        instance = Instance(data, input, transport)
        assert instance.uri == expected

    def test_pk(self, transport):
        data = {'id': 1}
        instance = Instance(data, 'parent', transport)
        assert instance.pk == 1

        data = {'foo': 1}
        instance = Instance(data, 'parent', transport)
        instance.identifier = 'foo'
        assert instance.pk == 1

        data = {'foo': 1}
        instance = Instance(data, 'parent', transport)
        with pytest.raises(ValueError):
            assert instance.pk == 1

    def test_helpers(self, transport):
        data = {
            'id': 1,
            'height': 10,
            'width': 25
        }
        instance = Instance(data, 'parent', transport)
        assert instance.keys() == data.keys()
        assert instance.values() == data.values()
        assert instance.items() == data.items()
        assert list(instance.iteritems()) == list(data.iteritems())
        assert instance.to_dict() == data


class TestRetrievable(object):
    class FooCollection(Collection, Retrievable):
        endpoint = 'foo'
        instance = Instance

    def test_get(self, monkeypatch, transport):
        collection = self.FooCollection(transport)
        rv = ({'id': 1, 'foo': 'bar'}, 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        instance = collection.get(1)
        assert isinstance(instance, Instance)
        assert instance.foo == 'bar'
        mock.assert_called_with('GET', '/foo/1')

class TestListable(object):
    class FooCollection(Collection, Listable):
        endpoint = 'foo'
        instance = Instance

    def test_all(self, monkeypatch, transport):
        collection = self.FooCollection(transport)
        rv = ([{'id': 1, 'foo': 'bar'}], 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        instances = collection.all()
        assert isinstance(instances, list)
        assert len(instances) == 1
        assert instances[0].foo == 'bar'
        mock.assert_called_with('GET', '/foo', params={})

    def test_all_with_params(self, monkeypatch, transport):
        collection = self.FooCollection(transport)
        rv = ([{'id': 1, 'foo': 'bar'}], 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        instances = collection.all(limit=10, after=25)
        assert isinstance(instances, list)
        assert len(instances) == 1
        assert instances[0].foo == 'bar'
        mock.assert_called_with('GET', '/foo', params={'limit': 10, 'after': 25})


class TestCreatable(object):
    class FooCollection(Collection, Creatable):
        endpoint = 'foo'
        instance = Instance

    def test_create(self, monkeypatch, transport):
        collection = self.FooCollection(transport)
        rv = ({'id': 1, 'foo': 'bar'}, 201)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        body = {'foo': 'bar'}
        instance = collection.create(body)
        assert isinstance(instance, Instance)
        assert instance.foo == 'bar'
        assert instance.id == 1
        mock.assert_called_with('POST', '/foo', data=body)


class TestDeletable(object):
    class FooCollection(Collection, Retrievable, Deletable):
        class FooInstance(Instance, Deletable):
            pass
        endpoint = 'foo'
        instance = FooInstance

    def test_delete_on_collection(self, monkeypatch, transport):
        collection = self.FooCollection(transport)
        rv = ({}, 204)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        assert collection.delete() is True
        mock.assert_called_with('DELETE', '/foo')

    def test_delete_on_instance(self, monkeypatch, transport):
        collection = self.FooCollection(transport)
        rv = ({'id': 1, 'foo': 'bar'}, 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        instance = collection.get(1)
        assert isinstance(instance, Instance)
        assert instance.foo == 'bar'
        mock.assert_called_with('GET', '/foo/1')

        rv = ({}, 204)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(instance, 'request', mock)

        assert instance.delete() is True
        mock.assert_called_with('DELETE', '/foo/1')
