import os
import sys

import pytest

# Set up the path for tests.
here = os.path.join(os.path.dirname(__file__))
package = os.path.join(here, '..')
sys.path.insert(0, os.path.abspath(package))

from tictail import Tictail


@pytest.fixture(scope='function')
def client():
    return Tictail('test')


@pytest.fixture(scope='function')
def transport(client):
    return client.transport