# -*- coding: utf-8 -*-
from datetime import datetime

import pytest
from mock import MagicMock

from tictail.resource.base import (ApiObject,
                                   Resource,
                                   Collection,
                                   Get,
                                   GetById,
                                   List,
                                   Create,
                                   Delete,
                                   DeleteById,
                                   transform_attr_value)


class MockResource(Resource):
    endpoint = 'mocks'


class MockCollection(Collection):
    resource = MockResource


class TestTransforms(object):
    def test_transform_attr_value_simple(self):
        assert transform_attr_value('foo', 'bar') == 'bar'

        isodate = '2012-05-01T00:47:16'
        expected = datetime(2012, 5, 1, 0, 47, 16)

        assert transform_attr_value('created_at', isodate) == expected
        assert transform_attr_value('modified_at', isodate) == expected
        assert transform_attr_value('modified_at', None) is None

    def test_transform_attr_value_list_of_simple(self):
        value = ['foo', 'bar']
        assert transform_attr_value('foo', value) == value

    def test_transform_attr_value_dict(self):
        simple_dict = {
            'foo': 'bar',
            'created_at': '2012-05-01T00:47:16',
            'modified_at': '2012-05-01T00:47:16'
        }

        transformed = {
            'foo': 'bar',
            'created_at': datetime(2012, 5, 1, 0, 47, 16),
            'modified_at': datetime(2012, 5, 1, 0, 47, 16)
        }

        assert transform_attr_value('foo', simple_dict) == transformed

        nested_dict = {
            'foo': {
                'created_at': '2012-05-01T00:47:16',
                'modified_at': '2012-05-01T00:47:16'
            }
        }

        transformed = {
            'foo': {
                'created_at': datetime(2012, 5, 1, 0, 47, 16),
                'modified_at': datetime(2012, 5, 1, 0, 47, 16)
            }
        }

        assert transform_attr_value('foo', nested_dict) == transformed

    def test_transform_attr_value_list_of_dicts(self):
        list_of_dicts = [{
            'foo': 'bar',
            'created_at': '2012-05-01T00:47:16',
            'modified_at': '2012-05-01T00:47:16'
        }]

        transformed = [{
            'foo': 'bar',
            'created_at': datetime(2012, 5, 1, 0, 47, 16),
            'modified_at': datetime(2012, 5, 1, 0, 47, 16)
        }]

        assert transform_attr_value('foo', list_of_dicts) == transformed

        list_of_nested_dicts = [{
            'foo': {
                'created_at': '2012-05-01T00:47:16',
                'modified_at': '2012-05-01T00:47:16'
            }
        }]

        transformed = [{
            'foo': {
                'created_at': datetime(2012, 5, 1, 0, 47, 16),
                'modified_at': datetime(2012, 5, 1, 0, 47, 16)
            }
        }]

        assert transform_attr_value('foo', list_of_nested_dicts) == transformed


class TestApiObject(object):

    @pytest.mark.parametrize('input', [
        ('test', 200, {}),
        ('error', 500, {'params': 'foo', 'data': {'foo': 'bar'}})
    ])
    def test_request(self, monkeypatch, transport, input):
        exp_resp, exp_status, kwargs = input

        api_object = ApiObject(transport)
        assert api_object.transport is transport

        mock = MagicMock(return_value=(exp_resp, exp_status))
        monkeypatch.setattr(api_object.transport, 'get', mock)

        resp, status = api_object.request('GET', '/foo', **kwargs)
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
        api_object = ApiObject(transport)
        assert api_object._remove_slashes(input) == expected


class TestCollection(object):

    @pytest.mark.parametrize('parent,expected', [
        (None, '/mocks'),
        ('parent/', '/parent/mocks'),
        ('parent', '/parent/mocks'),
        ('parent/', '/parent/mocks'),
        ('parent', '/parent/mocks')
    ])
    def test_uri(self, transport, parent, expected):
        collection = MockCollection(transport, parent=parent)
        assert collection.uri == expected

    def test_instantiate_from_data(self, transport):
        collection = MockCollection(transport)

        rv = collection.instantiate_from_data(dict(foo='bar'))
        assert isinstance(rv, MockResource)
        rv.foo == 'bar'

        rv = collection.instantiate_from_data([
            dict(foo='bar'),
            dict(fooz='barz')
        ])
        assert isinstance(rv, list)
        assert isinstance(rv[0], MockResource)
        assert isinstance(rv[1], MockResource)
        assert rv[0].foo == 'bar'
        assert rv[1].fooz == 'barz'


class TestResource(object):

    @pytest.mark.parametrize('input,expected', [
        (({}, 'parent'), ({}, 'parent')),
        ((None, 'parent'), ({}, 'parent')),
        (({'foo': 'bar'}, '/parent'), ({'foo': 'bar'}, '/parent'))
    ])
    def test_construction(self, transport, input, expected):
        data, parent = input
        exp_data, exp_parent = expected
        instance = MockResource(transport, data=data, parent=parent)

        assert instance._data == exp_data
        assert instance.parent == exp_parent

        for k, v in (data or {}).items():
            assert getattr(instance, k) == v
            assert instance[k] == v

    def test_property_set_get(self, transport):
        data = {
            'id': 1,
            'nested': {
                'foo': 'bar'
            }
        }
        instance = MockResource(transport, data=data, parent='/parent')

        # Test constructor data properties.
        assert instance.id == 1
        assert instance['id'] == 1
        assert instance.nested == {'foo': 'bar'}
        assert instance['nested'] == {'foo': 'bar'}

        # Test instance properties.
        assert instance.uri == '/parent/mocks/1'
        with pytest.raises(KeyError):
            assert instance['uri']
        with pytest.raises(AttributeError):
            assert instance.unknown

        # Set and get data properties.
        instance['baz'] = 2
        assert instance.baz == 2
        assert instance['baz'] == 2

    def test_constructor_with_transformations(self, transport):
        data = {
            'foo': 'bar',
            'created_at': '2012-05-01T00:47:16',
            'modified_at': '2012-05-01T00:47:16',
            'nested_list': [{
                'created_at': '2012-05-01T00:47:16',
                'nested_object': {
                    'modified_at': '2012-05-01T00:47:16'
                }
            }]
        }

        instance = MockResource(transport, data=data, parent='/parent')

        assert instance.foo == 'bar'
        assert instance.created_at == datetime(2012, 5, 1, 0, 47, 16)
        assert instance.modified_at == datetime(2012, 5, 1, 0, 47, 16)
        assert instance.nested_list == [{
            'created_at': datetime(2012, 5, 1, 0, 47, 16),
            'nested_object': {
                'modified_at': datetime(2012, 5, 1, 0, 47, 16)
            }
        }]

    def test_construction_with_subresources(self, transport):
        # Use a collection and a resource as subresources.
        class Posts(Collection):
            pass
        class Comment(Resource):
            pass

        data = {'id': 1}
        instance = MockResource(transport, data=data, parent='parent')
        instance.subresources = [Posts, Comment]
        instance.instantiate_subresources()

        # Check that subresources were instantiated and named correctly.
        assert isinstance(instance.posts, Posts)
        assert isinstance(instance.comment, Comment)

        # Check that all other properties are correct.
        assert instance._data == {'id': 1}
        assert instance.parent == 'parent'
        for k, v in data.items():
            assert getattr(instance, k) == v

        # Check that the subresources are not included in the data.
        with pytest.raises(KeyError):
            assert instance['posts']
        with pytest.raises(KeyError):
            assert instance['comment']

    @pytest.mark.parametrize('input,expected', [
        (('parent', False), '/parent/mocks/1'),
        (('parent', True), '/parent/mocks'),

        (('parent/1', False), '/parent/1/mocks/1'),
        (('/parent/1', True), '/parent/1/mocks'),

        (('/parent/1/', False), '/parent/1/mocks/1'),
        (('/parent/1/', True), '/parent/1/mocks'),

        ((None, False), '/mocks/1'),
        ((None, True), '/mocks')
    ])
    def test_uri(self, transport, input, expected):
        parent, singleton = input
        data = {'id': 1}
        instance = MockResource(transport, data=data, parent=parent)
        instance.singleton = singleton
        assert instance.uri == expected

    def test_pk(self, transport):
        data = {'id': 1}
        instance = MockResource(transport, data=data, parent='parent')
        assert instance.pk == 1

        data = {'foo': 1}
        instance = MockResource(transport, data=data, parent='parent')
        instance.identifier = 'foo'
        assert instance.pk == 1

        data = {'foo': 1}
        instance = MockResource(transport, data=data, parent='parent')
        with pytest.raises(ValueError):
            assert instance.pk == 1

    def test_instantiate_with_data(self, transport):
        resource = MockResource(transport, parent='/parent')
        instance = resource.instantiate_from_data({'id': 1})
        assert isinstance(instance, MockResource)
        assert instance.pk == 1
        assert instance.parent == '/parent'

    def test_helpers(self, transport):
        data = {
            'id': 1,
            'height': 10,
            'width': 25
        }
        instance = MockResource(transport, data=data, parent='parent')
        assert instance.data_keys() == data.keys()
        assert instance.data_values() == data.values()
        assert instance.data_items() == data.items()
        assert instance.to_dict() == data


class TestGet(object):
    class GetMockResource(MockResource, Get):
        pass

    @pytest.mark.parametrize('singleton,expected_uri', [
        (False, '/mocks/1'),
        (True, '/mocks')
    ])
    def test_get(self, monkeypatch, transport, singleton, expected_uri):
        resource = self.GetMockResource(transport, data={'id': 1})
        resource.singleton = singleton
        rv = ({'id': 1, 'foo': 'bar'}, 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(resource, 'request', mock)

        resource = resource.get()
        assert isinstance(resource, MockResource)
        assert resource.foo == 'bar'
        mock.assert_called_with('GET', expected_uri)


class TestGetById(object):
    class GetByIdMockCollection(MockCollection, GetById):
        pass

    def test_get_by_id(self, monkeypatch, transport):
        collection = self.GetByIdMockCollection(transport)
        rv = ({'id': 1, 'foo': 'bar'}, 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        resource = collection.get(1)
        assert isinstance(resource, MockResource)
        assert resource.foo == 'bar'
        mock.assert_called_with('GET', '/mocks/1')


class TestList(object):
    class ListMockCollection(MockCollection, List):
        def format_params(self, **params):
            if 'cats' in params:
                params['cats'] = ','.join(params['cats'])
            if 'date' in params:
                params['date'] = params['date'].isoformat()
            return params

    def test_all(self, monkeypatch, transport):
        collection = self.ListMockCollection(transport)
        rv = ([{'id': 1, 'foo': 'bar'}], 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        resources = collection.all()
        assert isinstance(resources, list)
        assert len(resources) == 1
        assert resources[0].foo == 'bar'
        mock.assert_called_with('GET', '/mocks', params={})

    def test_all_with_params(self, monkeypatch, transport):
        collection = self.ListMockCollection(transport)
        rv = ([{'id': 1, 'foo': 'bar'}], 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        resources = collection.all(limit=10, after=25)
        assert isinstance(resources, list)
        assert len(resources) == 1
        assert resources[0].foo == 'bar'
        mock.assert_called_with('GET', '/mocks', params={'limit': 10, 'after': 25})

    def test_all_with_formatted_params(self, monkeypatch, transport):
        collection = self.ListMockCollection(transport)
        rv = ([{'id': 1, 'foo': 'bar'}], 200)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        from datetime import datetime
        now = datetime.utcnow()

        resources = collection.all(cats=['a', 'b'], date=now)
        assert isinstance(resources, list)
        assert len(resources) == 1
        assert resources[0].foo == 'bar'
        mock.assert_called_with(
            'GET',
            '/mocks',
            params={'cats': 'a,b', 'date': now.isoformat()}
        )


class TestCreate(object):
    class CreateMockCollection(MockCollection, Create):
        pass

    def test_create(self, monkeypatch, transport):
        collection = self.CreateMockCollection(transport)
        rv = ({'id': 1, 'foo': 'bar'}, 201)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        body = {'foo': 'bar'}
        resourcd = collection.create(body)
        assert isinstance(resourcd, Resource)
        assert resourcd.foo == 'bar'
        assert resourcd.id == 1
        mock.assert_called_with('POST', '/mocks', data=body)


class TestDelete(object):
    class DeleteMockResource(MockResource, Delete):
        pass

    @pytest.mark.parametrize('singleton,expected_uri', [
        (False, '/mocks/1'),
        (True, '/mocks')
    ])
    def test_delete(self, monkeypatch, transport, singleton, expected_uri):
        resource = self.DeleteMockResource(transport, data={'id': 1})
        resource.singleton = singleton
        rv = ({}, 204)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(resource, 'request', mock)

        assert resource.delete() is True
        mock.assert_called_with('DELETE', expected_uri)


class TestDeleteById(object):
    class DeleteByIdMockCollection(MockCollection, DeleteById):
        pass

    def test_delete(self, monkeypatch, transport):
        collection = self.DeleteByIdMockCollection(transport)
        rv = ({}, 204)
        mock = MagicMock(return_value=rv)
        monkeypatch.setattr(collection, 'request', mock)

        assert collection.delete(1) is True
        mock.assert_called_with('DELETE', '/mocks/1')
