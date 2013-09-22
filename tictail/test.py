from .client import Tictail

tt = Tictail('test', config={'api_base_url': 'api.tictailhq.com'})

store = tt.stores.get('3')
assert store.followers.list() == tt.followers(store='3').list()
assert store.products.list() == tt.products(store='3').list()
assert store.customers.list() == tt.customers(store='3').list()