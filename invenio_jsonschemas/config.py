# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

JSONSCHEMAS_HOST = 'localhost'
"""Default json schema host."""

JSONSCHEMAS_ENDPOINT = '/schemas'
"""Default schema endpoint."""

JSONSCHEMAS_URL_SCHEME = 'https'
"""Default url scheme for schemas."""

JSONSCHEMAS_REPLACE_REFS = False
"""Whether to resolve $ref before serving a schema."""

JSONSCHEMAS_RESOLVE_SCHEMA = False
"""Whether to resolve schema using the Resolver Class.

If is ``True``, will replace $ref and run the
:py:const:`invenio_jsonschemas.config.JSONSCHEMAS_RESOLVER_CLS` class
before serving a schema.
"""

JSONSCHEMAS_LOADER_CLS = None
"""Loader class used in ``JSONRef`` when replacing ``$ref``."""

JSONSCHEMAS_RESOLVER_CLS = 'invenio_jsonschemas.utils.resolve_schema'
"""Resolver used to resolve the schema.

if :py:const:`invenio_jsonschemas.config.JSONSCHEMAS_RESOLVE_SCHEMA` is
``True`` or there is ``?resolved=1`` parameter on the request the resolver
will run over the schema. This can be used for custom schemas resolver.
"""

JSONSCHEMAS_REGISTER_ENDPOINTS_API = True
"""Register the endpoints on the API app."""

JSONSCHEMAS_REGISTER_ENDPOINTS_UI = True
"""Register the endpoints on the UI app."""

JSONSCHEMAS_SCHEMAS = None  # loads all JSON Schemas
"""List of entrypoint names to register JSON Schemas for.

If `None`, all JSON Schemas defined through the ``invenio_jsonschemas.schemas``
entry point in setup.py will be registered.
If ``[]``, no JSON Schemas will be registered.

For example, if you only want to register `foo` and skip `bar` schemas:

.. code-block:: python

    # in your `setup.py` you would specify:
    entry_points={
        'invenio_jsonschemas.schemas': [
            'foo = invenio_foo.schemas',
            'bar = invenio_bar.schemas',
        ],
    }
    # and in your config.py
    JSONSCHEMAS_SCHEMAS = ['foo']
"""
