tictail-python
==============

[![Build Status](https://travis-ci.org/tictail/tictail-python.svg?branch=master)](https://travis-ci.org/tictail/tictail-python)

Python bindings for the Tictail API ([API reference](https://tictail.com/developers/documentation/api-reference/)).

### Installation

The easiest way to install `tictail-python` is via `pip`:

```shell
$ pip install tictail
```

Alternatively, you can download the [source](https://github.com/tictail/tictail-python/releases) and then run:

```shell
$ python setup.py install
```

#### Mac OS X

You might get the following error on Mac OS X:

```
clang: error: unknown argument: '-mno-fused-madd' [-Wunused-command-line-argument-hard-error-in-future]
```

This is caused by the latest (5.1) version of Xcode which ships with a compiler
that treats unknown passed parameters as errors. The workaround is to set the
ARCHFLAGS environment variable to treat such errors as warnings:

```shell
$ ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install tictail
```

### Version Support

`tictail-python` supports Python 2.6 and 2.7. Python 3.2+ support is coming soon.

### Dependencies

The following packages will be installed together with `tictail-python`:

- `requests==2.2.1`
- `pyasn1==0.1.6`
- `pyOpenSSL==0.13`
- `ndg-httpsclient==0.3.2`

### Contributing

For bugs and feature requests, please open an [issue](https://github.com/tictail/tictail-python/issues). If you'd like to contribute
to the development of `tictail-python` – a fact of grandiose awesomeness – then clone the repo, install the development dependencies and hack away. Make sure you include tests, update the changelog and add your name to the contributors list.

### Testing

The library uses `pytest` and `coverage` for unit and integration tests. Run `make test` to
run all the tests. Alternatively, you can use the `py.test` binary to run specific tests.

### Quickstart

The Tictail platform uses OAuth 2.0 for authentication so you need to create your application and obtain an access token for a store. The details of how to do that are not in the scope of this document, but the [authentication](https://tictail.com/developers/documentation/authentication/) section of the documentation has a nice set of instructions and best practices.

Once you have an access token you can instantiate the `Tictail` client and get the store associated with the token:

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
```

### Configuration

The `Tictail` client comes preconfigured with sane defaults. If you wish to
override the default configuration, you can supply the constructor with a configuration
dictionary:

```python
from tictail import Tictail

config = {
  'timeout': 40
}
client = Tictail('<access_token>', config=config)
```

See `client.py` for details on what can be overriden.

### Usage & Examples

#### Store

Reference: [Store](https://tictail.com/developers/documentation/api-reference/#Store)

The `Store` resource is the only top-level API object and exposes properties for
all its subresources which are documented further below.

**Retrieving a store**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
```

An example (partial) response:

```python
>>> print store
Store({
  'contact_email': u'thestartupstore@example.com',
  'country': u'SE',
  'currency': u'SEK',
  'dashboard_url': u'https://tictail.com/dashboard/store/thestartupstore',
  'description': u'Support your local Startup! ...',
  'id': u't',
  'language': u'en',
  'logotype': [...],
  'name': u'The Startup Store',
  'sandbox': False,
  'storekeeper_email': u'johndoe@example.com',
  'url': u'http://thestartupstore.tictail.com'
})
```

#### Card

Reference: [Card](https://tictail.com/developers/documentation/api-reference/#Card)

Cards are how you get your content into the feed of the store. The `Card` resource
only allows for creating cards at this point.

**Creating a new card**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
card = store.cards.create({
  'title': 'Check out this amazing site',
  'action': 'http://example.com',
  'card_type': 'media',
  'content': {
    'header': 'You will not regret this'
  }
})
```

An example response:

```python
>>> print card
Card({
  'action': u'http://example.com',
  'card_type': u'media',
  'content': {
    u'header': u'You will not regret this'
  },
  'created_at': u'2014-04-23T20:25:47.745085',
  'id': u'fREx',
  'modified_at': u'2014-04-23T20:25:47.752799',
  'title': u'Check out this amazing site'
})
```

#### Product

Reference: [Product](https://tictail.com/developers/documentation/api-reference/#Product)

Using the `Product` resource you can list all the visible products of a store or get a specific product by id.
Listing products accepts four optional query parameters:

- `limit` for page size
- `before` and `after` for paginating on products created before or after a product with a given id
- `categories` for filtering products on certain categories

**List 50 products created after the product with id '7bxv'**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
products = store.products.all(after='7bxv', limit=50)
```

**List all shirts (id:'aVr') and jeans (id: 'bEt2')**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
products = store.products.all(categories=['aVr', 'bEt2'])
```

**Retrieve a specific product**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
product = store.products.get('7bxv')
```

An example response:

```python
>>> print product
Product({
  'created_at': u'2014-01-29T13:41:43',
  'currency': u'PLN',
  'description': u'',
  'id': u'7bxv',
  'images': [],
  'modified_at': u'2014-01-29T13:41:43',
  'price': 1200,
  'price_includes_tax': True,
  'quantity': None,
  'slug': u'super-duper-tshirt',
  'status': u'published',
  'store_id': u'scV',
  'title': u'super duper tshirt',
  'unlimited': True,
  'variations': []
})
```

#### Customer

Reference: [Customer](https://tictail.com/developers/documentation/api-reference/#Customer)

The `Customer` resource returns all the customers of a store, i.e people that bought
something at least once from that store. Listing customers accepts three optional
query parameters:

- `limit` for page size
- `before` and `after` for paginating on customers created before or after a customers with a given id

**Retrieve a specific customer**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
customer = store.customers.get('7')
```

**List all customers**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
customers = store.customers.all()
```

An example response:

```python
>>> print customer
Customer({
 'country': u'SE',
 'created_at': u'2012-12-10T19:31:07',
 'email': u'johndoe@example.com',
 'id': u'bz21',
 'language': u'en',
 'modified_at': None,
 'name': u'John Doe'
})
```

#### Follower

Reference: [Follower](https://tictail.com/developers/documentation/api-reference/#Follower)

The `Follower` resource returns all the followers of a store. Listing followers accepts three optional
query parameters:

- `limit` for page size
- `before` and `after` for paginating on followers created before or after a follower with a given id

**Create a follower**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
follower = store.followers.create({'email': 'newfollower@example.com'})
```

**Delete a follower**
```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()

# You can either delete a follower from the `Collection`...
deleted = store.followers.delete(7)
assert deleted

# ...or from the `Resource` itself.
follower = store.followers.all()[0]
deleted = follower.delete()
assert deleted
```

**List all followers**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
followers = store.followers.all()
```

**List all followers created before the follower with id '7aN'**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
followers = store.followers.all(before='7aN')
```

An example response:

```python
>>> print follower
Follower({
  'created_at': u'2013-12-10T19:31:07',
  'modified_at': None,
  'email': u'johndoe@example.com',
  'id': u'NZUr'
})
```

#### Order

Reference: [Order](https://tictail.com/developers/documentation/api-reference/#Order)

The `Order` resource returns all the orders of a store. If you wish to get the customers
of the store then use the `Customer` resource instead. Listing orders accepts
five optional query parameters:

- `limit` for page size
- `before` and `after` for for paginating on orders created before or after a orders with a given id
- `modified_before` and `modified_after` for paginating on orders modified before or after a given date (the date
  can be either a string in `ISO 8601` format or a `datetime` object)

**List all orders after a specific id**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
orders = store.orders.all(after='aFQX')
```

**List all orders modified after a date**

```python
from datetime import datetime
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()

# Using a datetime object...
now = datetime.now()
orders = store.orders.all(modified_after=now)

# ...or a string.
orders = store.orders.all(modified_after=now.isoformat())
```

**Retrieve a specific order**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
order = store.orders.get('aFQX')
```

An example (partial) response:

```python
>>> print order
Order({
  'customer': {
    'name': u'John Doe',
    ...
  },
  'transaction': {
    'status': u'paid',
    ...
  },
  'prices_include_vat': True,
  'discounts': [],
  'items': [{
    'currency': u'SEK',
    'price': 0,
    ...
  },
  ...
  ],
  'fullfilment': {
    'status': u'unhandled',
    ...
  },
  'price': 0,
  'id': u'aFQX',
  'vat': {
    'price': 0,
    'rate': u'0.250000'
  }
})
```

#### Theme

Reference: [Theme](https://tictail.com/developers/documentation/api-reference/#Theme)

The `Theme` resource is a singleton resource that returns the currently active
theme of the store.

**Get the theme**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
theme = store.theme.get()
```

An example (partial) response:

```python
>>> print theme
Theme({
 'id': u'Ag',
 'markup': u'<!DOCTYPE html>\n<html lang="en">\n<head>\n...'
})
```

#### Category

Reference: [Category](https://tictail.com/developers/documentation/api-reference/#Category)

The `Category` resource returns the categories which make up the store's navigation.
They are implemented as a classical parent-child hierarchy, limited to one level of depth.

**List all categories**

```python
from tictail import Tictail

client = Tictail('<access_token>')
store = client.me()
categories = store.categories.all()
```

An example (partial) response:

```python
>>> print categories
[
 Category({
  'created_at': u'2012-05-01T00:47:16',
  'id': u'dn',
  'modified_at': u'2012-02-13T16:58:40',
  'parent_id': None,
  'position': 0,
  'title': u'Stickers'
 }),
 Category({
  'created_at': u'2012-10-29T12:02:09',
  'id': u'dA',
  'modified_at': None,
  'parent_id': u'dn',
  'position': 1,
  'title': u'DevAwsmbx'
 })
 ...
]
```
