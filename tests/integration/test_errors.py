# -*- coding: utf-8 -*-
from tictail import Tictail, errors


class TestErrors(object):

    def test_forbidden(self):
        client = Tictail('badkey')
        try:
            client.me()
            assert False, 'Using a bad token, should throw `errors.Forbidden`.'
        except errors.Forbidden as err:
            assert err.status == 403
            assert err.json == {
                'status': 403,
                'message': 'Forbidden',
                'params': {},
                'support_email': 'developers@tictail.com'
            }

    def test_bad_request(self, client):
        try:
            collection = client.followers(store='i-am-a-bad-id')
            collection.all()
            assert False, 'Using a bad id, should throw `errors.BadRequest`.'
        except errors.BadRequest as err:
            assert err.status == 400
            assert err.json == {
                'status': 400,
                'message': 'Bad Request',
                'params': {
                    'id': 'malformed'
                },
                'support_email': 'developers@tictail.com'
            }

    def test_not_found(self, client):
        try:
            collection = client.customers(store='KGu')
            collection.get('4EeL')
            assert False, 'Using a non-existent id, should throw `errors.NotFound`.'
        except errors.NotFound as err:
            assert err.status == 404

    def test_validation_error(self, client):
        try:
            collection = client.followers(store='KGu')
            collection.create({})
            assert False, 'Skipping a required field, should throw `errors.BadRequest`.'
        except errors.BadRequest as err:
            assert err.status == 400
            assert err.json == {
                'status': 400,
                'message': 'Bad Request',
                'params': {
                    'email': 'email is required in json'
                },
                'support_email': 'developers@tictail.com'
            }
