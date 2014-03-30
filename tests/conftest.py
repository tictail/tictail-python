import os
import sys

# Set up the path for tests.
here = os.path.join(os.path.dirname(__file__))
package = os.path.join(here, '..')
sys.path.insert(0, os.path.abspath(package))