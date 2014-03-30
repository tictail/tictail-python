"""
tictail.importer
~~~~~~~~~~~~~~~~

Imports various needed dependencies with fallbacks. Provides some help with
installing missing dependencies.

Dependencies:
  * json/simplejson
  * requests

"""

def raise_import_error_with_hint(dep):
    """Raises an import error and gives a helpful message for installing the
    missing dependency.

    :param dep: the missing dependency.

    """
    raise ImportError(("`{0}` is required. "
                       "Install it with `pip install {0}` or "
                       "`easy_install {0}` if you are not using pip. "
                       "For more details, visit http://pip-installer.org.")
                       .format(dep))


# Try to import `requests`.
try:
    import requests
except ImportError:
    raise_import_error_with_hint('requests')


# Try to import `json` and fallback to `simplejson` if not available.
try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        raise_import_error_with_hint('simplejson')
