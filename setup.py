# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for building and serving JSONSchemas."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.2.2',
    'jsonschema>=2.5.1',
    'pydocstyle>=2.0.0',
    'pytest-cov>=1.8.0',
    'pytest-pep8>=1.0.6',
    'pytest>=4.0.0,<5.0.0',
    'mock>=1.3.0',
]

extras_require = {
    ':python_version=="2.7"': [
        'functools32>=3.2.3.post2',
    ],
    'docs': [
        'Sphinx>=1.6.2',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name[0] == ':':
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'pytest-runner>=2.6.2',
]

install_requires = [
    'Flask>=0.11.1',
    'jsonref>=0.1',
    'jsonresolver>=0.2.1,<0.3.0',
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_jsonschemas', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-jsonschemas',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio json schema jsonschema',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-jsonschemas',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'invenio_base.apps': [
            'invenio_jsonschemas = invenio_jsonschemas:InvenioJSONSchemasUI',
        ],
        'invenio_base.api_apps': [
            'invenio_jsonschemas = invenio_jsonschemas:InvenioJSONSchemasAPI',
        ],
        'invenio_records.jsonresolver': [
            'invenio_jsonschemas = invenio_jsonschemas.jsonresolver',
        ]
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Development Status :: 5 - Production/Stable',
    ],
)
