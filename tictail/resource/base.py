"""
tictail.resource.base
~~~~~~~~~~~~~~~~~~~~~

Definitions for `Resource` and `Collection` with their corresponding capability
mixins.

"""
from dateutil.parser import parse


def parse_datetime(iso8601_string):
    """Parses an ISO 8601 datetime string and returns a `datetime.datetime`.

    :param iso8601_string: The string to parse.

    """
    return parse(iso8601_string)


def transform_attr_value(attr, value):
    """Transforms the value of the given attribute to a different representation
    For example, `modified_at` will be transformed to a `datetime` object.

    If a transformation cannot be found, and `value` is a list or a dict we
    apply this function recursively to transform nested keys. Otherwise, the
    original value is returned.

    :param attr: The attribute to transform.
    :param value: The value of the attribute to transform.

    """
    transforms = {
        'modified_at': parse_datetime,
        'created_at': parse_datetime
    }

    def _transform_dict(value):
        transformed = {}
        for key, nested_value in value.iteritems():
            transformed[key] = transform_attr_value(key, nested_value)
        return transformed

    if value is None:
        return value

    transform = transforms.get(attr)

    if transform:
        # If we've found a transform at this level then return the transformed
        # value.
        transformed = transform(value)
    else:
        # Otherwise, if this is a dict or a list of dicts, we recursively apply
        # the function in an attempt to transform nested keys.
        if isinstance(value, dict):
            transformed = _transform_dict(value)
        elif isinstance(value, list):
            try:
                transformed = map(_transform_dict, value)
            except (AttributeError, TypeError):
                transformed = value
        else:
            transformed = value

    return transformed


class ApiObject(object):
    def __init__(self, transport, parent=None):
        """Initializes the base `ApiObject` class.

        :param transport: An instance of the transport strategy.

        """
        self.transport = transport

    @property
    def attr_name(self):
        """Returns a string used when attaching this `ApiObject` as a property
        on another object.

        """
        return self.__class__.__name__.lower()

    def _remove_slashes(self, url):
        """Removes leading and trailing slashes from the url `fragment`.

        :param url: A url string.

        """
        if not url:
            return url
        start = 1 if url[0] == '/' else None
        end = -1 if url[-1] == '/' else None
        return url[start:end]

    def request(self, method, uri, **kwargs):
        """Performs an HTTP request using the underlying transport.

        :param method: The HTTP method.
        :param uri: The resource uri.
        :param kwargs: Pass-through parameters to the transport method.

        """
        method = method.lower()
        http_method = getattr(self.transport, method)
        return http_method(uri, **kwargs)


# =================
# Basic API objects
# =================


class Resource(ApiObject):
    """Describes an API resource."""

    # A list of `Resource` objects, that will be instantiated as subresources.
    subresources = []

    # The name of the primary key for this instance.
    identifier = 'id'

    # The endpoint of this resource.
    endpoint = None

    # Marks this resource as singleton. A singleton resource can be fetched
    # without a primary key e.g /stores/1/theme.
    singleton = False

    def __init__(self, transport, data=None, parent=None):
        """Initializes this resource.

        :param transport: An instance of the transport strategy.
        :param data: A optional dict of data for this resource.
        :param parent: An optional parent prefix to be attached to this
        resource's uri.

        """
        self._data = dict()
        self.parent = parent

        super(Resource, self).__init__(transport)

        if data is None:
            data = {}

        for k, v in data.iteritems():
            self[k] = v

        self.instantiate_subresources()

    def __getitem__(self, k):
        return self._data[k]

    def __setitem__(self, k, v):
        v = transform_attr_value(k, v)
        self._data[k] = v

    def __delitem__(self, k):
        raise TypeError('Deleting properties is not supported.')

    def __getattr__(self, k):
        try:
            return self[k]
        except KeyError:
            raise AttributeError(k)

    def __setattr__(self, k, v):
        if k == '_data' or k not in self._data:
            super(Resource, self).__setattr__(k, v)
        else:
            self[k] = v

    def __delattr__(self, k):
        self.__delitem__(k)

    def __repr__(self):
        import pprint
        name = self.__class__.__name__
        return "{0}({1})".format(name, pprint.pformat(self.to_dict()))

    @property
    def pk(self):
        identifier = self.identifier
        if not hasattr(self, identifier):
            raise ValueError(
                "This instance does not have a property '{0}' for primary key."
                .format(identifier)
            )
        return getattr(self, identifier)

    @property
    def uri(self):
        uri = ''

        if self.parent:
            parent = self._remove_slashes(self.parent)
            uri += "/{0}".format(parent)

        uri += "/{0}".format(self.endpoint)

        if not self.singleton:
            uri += "/{0}".format(self.pk)

        return uri

    def instantiate_subresources(self):
        """Instantiates all subresources which are attached as properties."""
        for sub in self.subresources:
            inst = sub(self.transport, parent=self.uri)
            setattr(self, inst.attr_name, inst)

    def instantiate_from_data(self, data):
        """Returns an instance of this `Resource` with the given `data`.

        :param data: A data dictionary.

        """
        return self.__class__(self.transport, data=data, parent=self.parent)

    def data_keys(self):
        return self._data.keys()

    def data_values(self):
        return self._data.values()

    def data_items(self):
        return self._data.items()

    def to_dict(self):
        return self._data


class Collection(ApiObject):
    """Represents a collection of resources."""

    # The Resource class for this collection.
    resource = None

    def __init__(self, transport, parent=None):
        """Initializes an API collection resource.

        :param transport: An instance of the transport strategy.
        :param parent: An optional parent prefix to be attached to this
        collection's uri.

        """
        super(Collection, self).__init__(transport)
        self.parent = parent

    @property
    def uri(self):
        endpoint = self._remove_slashes(self.resource.endpoint)
        if not self.parent:
            return "/{0}".format(endpoint)
        parent = self._remove_slashes(self.parent)
        return "/{0}/{1}".format(parent, endpoint)

    def instantiate_from_data(self, data):
        """Returns an instance or list of instances of the `Resource` class for
        this collection.

        :param data: A data dictionary or a list of data dictionaries.

        """
        maker = lambda d: self.resource(self.transport, data=d, parent=self.parent)
        return map(maker, data) if isinstance(data, list) else maker(data)


# ============
# Capabilities
# ============


class Get(object):
    def get(self):
        data, _ = self.request('GET', self.uri)
        return self.instantiate_from_data(data)


class GetById(object):
    def get(self, id):
        uri = "{0}/{1}".format(self.uri, id)
        data, _ = self.request('GET', uri)
        return self.instantiate_from_data(data)


class List(object):
    def format_params(self, **params):
        return params

    def all(self, **params):
        params = self.format_params(**params)
        data, _ = self.request('GET', self.uri, params=params)
        return self.instantiate_from_data(data)


class Create(object):
    def create(self, body):
        data, _ = self.request('POST', self.uri, data=body)
        return self.instantiate_from_data(data)


class Delete(object):
    def delete(self):
        data, status = self.request('DELETE', self.uri)
        return status == 204


class DeleteById(object):
    def delete(self, id):
        uri = "{0}/{1}".format(self.uri, id)
        data, status = self.request('DELETE', uri)
        return status == 204


__all__ = [
    'ApiObject', 'Resource', 'Collection', 'Get', 'GetById', 'List', 'Create',
    'Delete', 'DeleteById'
]
