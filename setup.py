#!/usr/bin/env python

from setuptools import setup


with open('requirements.txt') as fd:
    requirements = fd.readlines()


with open('tictail/version.py') as fd:
    version = fd.read().split('=')[1].replace("'", '').strip()


with open('README.md') as fd:
    long_description = fd.read()


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
    install_requires=requirements,
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries",
    ]
)