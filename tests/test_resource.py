# -*- coding: utf-8 -*-
import pytest
from mock import MagicMock

from tictail.resource.base import Resource, Collection, Instance


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
        (('test', None), 'test'),
        (('/test', None), 'test'),
        (('test/', None), 'test'),
        (('test', '/prefix'), 'prefix/test'),
        (('test', 'prefix/'), 'prefix/test'),
        (('test', 'prefix'), 'prefix/test')
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
        (({'foo': 'bar'}, '/parent'), (['foo'], 'parent'))
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
