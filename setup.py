#!/usr/bin/env python

from distutils.core import setup


OPERATORS = ('<', '>', '==', '<=', '>=', '!=')


def _format_requirement(req):
    for op in OPERATORS:
        tokens = map(str.strip, req.split(op))
        if len(tokens) == 2:
            break
    else:
        return req
    name, version = tokens
    return '%s (%s%s)' % (name, op, version)


with open('requirements.txt') as fd:
    requires = map(_format_requirement, fd.read().split())


with open('tictail/version.py') as fd:
    version = fd.read().split('=')[1].strip()


setup(
    name='tictail',
    version=version,
    packages=['tictail', 'tictail.resource'],
    license='MIT',
    author='Tictail AB',
    author_email='tech@tictail.com',
    url='https://github.com/tictail/tictail-python',
    download_url='https://github.com/tictail/tictail-python/releases',
    description='Python bindings for the Tictail API',
    keywords=['tictail', 'rest', 'api'],
    requires=requires
)