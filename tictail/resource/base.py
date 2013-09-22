"""
tictail.resource.base
~~~~~~~~~~~~~~~~~~~~~

Base definitions for `Resource` and `Instance`. The prior follow a hierarchical
and recursive structure with `Resource` being the parent and `Instance` the child.

`Instance` can include other `Resource` objects as subresources, which in turn
are parents for `Instance` objects. Just like Inception.

"""

from itertools import izip


class ResourceBase(object):
    def __init__(self, transport):
        """Initializes the base class.

        :param transport: an instance of the transport strategy.

        """
        self.transport = transport

    def request(self, method, uri, **kwargs):
        method = method.lower()
        http_method = getattr(self.transport, method)
        data, status_code = http_method(uri, **kwargs)
        return data, status_code


class Resource(ResourceBase):
    def __init__(self, transport, endpoint_prefix=''):
        """Initializes an API resource.

        :param transport: an instance of the transport strategy.
        :param endpoint_prefix: an optiona prefix to be attached to the `endpoint`.

        """
        super(Resource, self).__init__(transport)
        self.endpoint_prefix = endpoint_prefix

    @property
    def uri(self):
        if self.endpoint_prefix:
            return "{}/{}".format(self.endpoint_prefix, self.endpoint)
        else:
            return self.endpoint

    def make_instance(self, data):
        if isinstance(data, list):
            return [self.instance(d, self.uri, self.transport) for d in data]
        else:
            return self.instance(data, self.uri, self.transport)

    def get(self, id):
        """Returns an `Instance` of this resource by `id`.

        :param id: the primary key of the instance to fetch.

        """
        data, _ = self.request('GET', "{}/{}".format(self.uri, id))
        return self.make_instance(data)


class ListableResource(Resource):
    def list(self):
        data, _ = self.request('GET', self.uri)
        return self.make_instance(data)


class CreatableResource(Resource):
    def create(self, body):
        data, _ = self.request('POST', self.uri, data=body)
        return self.make_instance(data)


class DeletableResource(Resource):
    def delete(self):
        data, status = self.request('DELETE', self.uri)
        return status == 204


class Instance(ResourceBase):
    """A single instance of an API resource."""

    # a set of attributes that should not be included in this instance's data.
    # note: `transport` is inherited from `ResourceBase`.
    _internal_attrs = set(['transport', 'parent_uri', '_keys', '_subnames'])

    # a list of `Resource` objects, that will be instantiated as subresources.
    subresources = []

    def __init__(self, data, parent_uri, transport):
        """Initializes this instance.

        :param data: a dict of data for this instance.
        :param parent_uri: this instance's parent resource uri.

        """
        self._keys = set()
        self._subnames = set()
        self.parent_uri = parent_uri

        super(Instance, self).__init__(transport)

        if data is None:
            data = {}

        for k, v in data.iteritems():
            self.__setattr__(k, v)

        self.instantiate_subresources()

    def __setattr__(self, k, v):
        self.__dict__[k] = v
        if k not in self._internal_attrs:
            self._keys.add(k)

    def __getattr__(self, k):
        try:
            return self.__dict__[k]
        except KeyError as ke:
            raise AttributeError(ke.message)

    def instantiate_subresources(self):
        for sub in self.subresources:
            inst = sub(self.transport, endpoint_prefix=self.uri)
            name = inst.__class__.__name__.lower()
            self._subnames.add(name)
            self.__setattr__(name, inst)

    @property
    def uri(self):
        return "{}/{}".format(self.parent_uri, self.id)

    def keys(self):
        return list(self._keys)

    def values(self):
        return [self.__getattr__(k) for k in self.keys()]

    def items(self):
        return zip(self.keys(), self.values())

    def iteritems(self):
        return izip(self.keys(), self.values())

    def to_dict(self):
        d = {}
        for k, v in self.items():
            d[k] = v
        return d

    def __repr__(self):
        import pprint
        name = self.__class__.__name__
        return "{}({})".format(name, pprint.pformat(self.to_dict()))


class DeletableInstance(Instance):
    def delete(self):
        data, status = self.request('DELETE', self.uri)
        return status == 204


__all__ = [
    'Resource', 'ListableResource', 'DeletableResource',
    'CreatableResource', 'Instance', 'DeletableInstance'
]
