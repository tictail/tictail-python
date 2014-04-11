"""
tictail.resource.base
~~~~~~~~~~~~~~~~~~~~~

Base definitions for `Collection` and `Instance`. They follow a hierarchical and
recursive structure with `Collection` being the parent and `Instance` the child.

`Instance` objects can include `Collection` objects as subresources, which in turn
are parents for their own `Instance` objects. Just like Inception.

"""

from itertools import izip


class Resource(object):
    def __init__(self, transport):
        """Initializes the base `Resource` class.

        :param transport: An instance of the transport strategy.

        """
        self.transport = transport

    @property
    def _name(self):
        return self.__class__.__name__.lower()

    def _remove_slashes(self, url):
        """Removes leading and trailing slashes from the url `fragment`."""
        if not url:
            return url
        if url[0] == '/':
            url = url[1:]
        if url[-1] == '/':
            url = url[:-1]
        return url

    def request(self, method, uri, **kwargs):
        method = method.lower()
        http_method = getattr(self.transport, method)
        return http_method(uri, **kwargs)


class Collection(Resource):
    """Represents a collection resource. Expects `endpoint` and `instance` to
    be defined as static properties.

    """
    instance = None
    endpoint = None

    def __init__(self, transport, prefix=''):
        """Initializes an API collection resource.

        :param transport: An instance of the transport strategy.
        :param prefix: An optional prefix to be attached to the `endpoint`.

        """
        super(Collection, self).__init__(transport)
        self.prefix = prefix

    @property
    def uri(self):
        endpoint = self._remove_slashes(self.endpoint)
        if not self.prefix:
            return endpoint
        prefix = self._remove_slashes(self.prefix)
        return "{}/{}".format(prefix, endpoint)

    def make_instance(self, data):
        """Makes an instance (or a list of instances) of this resource from
        the given `data` using the `instance` class property.

        :param data: A dict or list of dicts.

        """
        if isinstance(data, list):
            return [self.instance(d, self.uri, self.transport) for d in data]
        else:
            return self.instance(data, self.uri, self.transport)


class Instance(Resource):
    """A single instance of an API resource."""

    # A set of attributes that should not be included in this instance's data.
    # Note: `transport` is inherited from `Resource`.
    _internal_attrs = set([
        'transport',
        'parent_uri',
        'subresources',
        'identifier',
        '_data_keys'
    ])

    # A list of `Resource` objects, that will be instantiated as subresources.
    subresources = []

    # The name of the primary key for this instance.
    identifier = 'id'

    def __init__(self, data, parent_uri, transport):
        """Initializes this instance.

        :param data: A dict of data for this instance.
        :param parent_uri: This instance's parent resource URI.

        """
        self._data_keys = set()
        self.parent_uri = self._remove_slashes(parent_uri)

        super(Instance, self).__init__(transport)

        if data is None:
            data = {}

        for k, v in data.iteritems():
            setattr(self, k, v)

        self.instantiate_subresources()

    def __setattr__(self, k, v):
        super(Resource, self).__setattr__(k, v)
        if k not in self._internal_attrs:
            self._data_keys.add(k)

    def instantiate_subresources(self):
        """Instantiates all subresources and attaches them as properties on this
        `instance`. For now, only `Collection` subresources are supported.

        """
        for sub in self.subresources:
            inst = sub(self.transport, prefix=self.uri)
            self._internal_attrs.add(inst._name)
            setattr(self, inst._name, inst)

    @property
    def pk(self):
        identifier = self.identifier
        if not hasattr(self, identifier):
            raise ValueError('This instance does not have a primary key value.')
        return getattr(self, identifier)

    @property
    def uri(self):
        return "{}/{}".format(self.parent_uri, self.pk)

    def keys(self):
        return list(self._data_keys)

    def values(self):
        return [getattr(self, k) for k in self.keys()]

    def items(self):
        return zip(self.keys(), self.values())

    def iteritems(self):
        return izip(self.keys(), self.values())

    def to_dict(self):
        return dict(self.items())

    def __repr__(self):
        import pprint
        name = self.__class__.__name__
        return "{}({})".format(name, pprint.pformat(self.to_dict()))


class Retrievable(object):
    """Resource mixin for getting an instance of a resource."""
    def get(self, id=None):
        uri = "{}/{}".format(self.uri, id) if id else self.uri
        data, _ = self.request('GET', uri)
        return self.make_instance(data)


class Listable(object):
    """Resource mixin for getting all instances of a resource."""
    def all(self):
        data, _ = self.request('GET', self.uri)
        return self.make_instance(data)


class Creatable(object):
    """Resource mixin that allows for creating a resource."""
    def create(self, body):
        data, _ = self.request('POST', self.uri, data=body)
        return self.make_instance(data)


class Deletable(object):
    """Resource mixin that allows for deleting a resource."""
    def delete(self):
        data, status = self.request('DELETE', self.uri)
        return status == 204


__all__ = [
    'Resource', 'Collection', 'Instance', 'Retrievable',
    'Listable', 'Creatable', 'Deletable'
]
