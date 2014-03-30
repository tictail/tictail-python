# -*- coding: utf-8 -*-

from tictail.errors import ApiError


class TestErrors(object):

    def test_construction(self):
        error = ApiError('test', 500, 'body')
        assert error.message == 'test'
        assert error.status == 500
        assert error.response == 'body'
        assert str(error) == 'test (500): body'