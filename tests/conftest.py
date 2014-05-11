import os
import sys

import pytest

# Set up the path for tests.
here = os.path.join(os.path.dirname(__file__))
package = os.path.join(here, '..')
sys.path.insert(0, os.path.abspath(package))

from tictail import Tictail


@pytest.fixture(scope='session')
def test_token():
    # This is a real access token to a sandbox store. The store does not accept
    # any payments and is pre-configured for running the integration tests for
    # this library.
    return 'accesstoken_54AL94jiZZQrvnfuxbSJQsImkoOHzs'


@pytest.fixture(scope='function')
def client(test_token):
    return Tictail(test_token)


@pytest.fixture(scope='function')
def transport(client):
    return client.transport
