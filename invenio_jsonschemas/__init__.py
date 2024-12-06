# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2024 Graz University of Technology.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-JSONSchemas is a module for building and serving JSON Schemas.

Using this module one can:

- Define JSON Schemas and expose them under a ``/schemas`` endpoint.
- Validate data using locally defined and/or external JSON Schemas.
- Resolve complex schemas and expand their references (``$ref``) or ``allOf``
  tags for usage with other libraries that do not support them.

JSON Schema basics
------------------

Using JSON Schemas is a popular way to define and make publicly available the
internal structure of complex entities being used inside an application. Since
Invenio is a digital library framework, dealing with entities that contain
complex metadata, like for example bibliographic records, is common and if not
handled properly can lead to data inconsistencies.

We will not attempt to explain in detail how JSON Schemas are defined and work,
since there are much more thorough resources available in the official `JSON
Schema website <http://json-schema.org>`_. Having a basic knowledge of them
though is recommended in order to understand what this module provides on top
of them.

Here is a basic JSON Schema defining the structure of a bibliographic record
with a ``title``, an optional ``description``, a list of ``creators`` and a
``publication_year``:

.. code-block:: json

    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "id": "https://myapp.org/schemas/record.json",
        "type": "object",
        "properties": {
            "title": { "type": "string" },
            "description": { "type": "string" },
            "creators": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": { "type": "string" }
                    },
                    "required": ["name"]
                }
            },
            "publication_year": { "type": "integer" }
        },
        "required": ["title", "creators", "publication_year"]
    }


A valid record for this JSON Schema would be the following:

.. code-block:: json

    {
        "title": "This is a record title",
        "creators": [ { "name": "Doe, John"}, { "name": "Roe, Jane" } ],
        "publication_year": 2018
    }


Initialization
--------------

First create a Flask application:

>>> from flask import Flask
>>> app = Flask(__name__)

Configuration
~~~~~~~~~~~~~

Before we initialize the ``InvenioJSONSchemas`` extension, we need to
configure which is our application's host. This will help with automatically
skipping additional HTTP requests when fetching locally defined JSON Schemas.
More about how this works is described in
:ref:`composable-schemas-with-jsonref`.

>>> # If your website's host is e.g. "myapp.org"
>>> app.config['JSONSCHEMAS_HOST'] = 'myapp.org'

Last, but not least, let's initialize the extension:

>>> from invenio_jsonschemas import InvenioJSONSchemas
>>> ext = InvenioJSONSchemas(app)

Setuptools integration
~~~~~~~~~~~~~~~~~~~~~~

The above steps didn't actually register any JSON Schemas. In order for your
JSON Schemas to be registered you must specify in your package's ``setup.py``
an entry point item in the ``invenio_jsonschemas.schemas`` group, pointing to
a Python module where the actual JSON Schema ``.json`` files are placed.
Invenio-JSONSchemas then takes care of loading them automatically during
application initialization.

By default the extension loads from entrypoint group name
``invenio_jsonschemas.schemas`` but you can change that as shown below:

.. code-block:: python

    ext = InvenioJSONSchemas(app, entry_point_group=<entrypoint_group_name>)


Registering JSON Schemas
------------------------

Here is a directory structure containing two
JSON Schemas, ``biology/animal_record_schema.json`` and ``record_schema.json``,
taken from this module's example application:

.. code-block:: console

    $ tree --dirsfirst invenio-jsonschemas/examples/samplepkg

    invenio-jsonschemas/examples/samplepkg
    ├── samplepkg
    │   ├── jsonschemas
    │   │   ├── biology
    │   │   │   └── animal_record_schema.json
    │   │   ├── __init__.py
    │   │   └── record_schema.json
    │   └── __init__.py
    └── setup.py

The first thing in order to use ``invenio_jsonschemas`` is to register your
folder that holds your schemas. To do so you have to include the entrypoint
to your package that points to your schema folder as shown below:

.. code-block:: python
    :emphasize-lines: 4-6

    # invenio-jsonschemas/examples/samplepkg/setup.py
    ...
    entry_points={
        'invenio_jsonschemas.schemas': [
            'samplepkg = samplepkg.jsonschemas'  # path to your schema folder
        ],
    },
    ...

After registering your schemas folder the extension knows where to find your
schemas and how to load them. The extension loads every schema that is under
``{JSONSCHEMAS_HOST}/{JSONSCHEMAS_ENDPOINT}`` by fetching it locally and not
making a network request. This means that reads directly the file of your
schema. Also, the same happens if you have inside of your schema a ``$ref``
field pointing to the same url format. You can see the function called when the
schema url is requested :source:`here <invenio_jsonschemas/views.py#L35>`.


Exposing JSON Schemas
---------------------

You can enable/disable the endpoint that serves your schemas during the
initialization of ``InvenioJsonSchemas`` extension by passing the parameter
``register_config_blueprint``. This parameter points to your configuration
variable that controls the serving of the schemas. So, if you want to disable
the schemas serving you can do it as shown below:

.. code block:: console

    app.config['SCHEMA_ENABLE_VARIABLE'] = False
    ext = InvenioJSONSchemas(
            app, register_config_blueprint='SCHEMA_ENABLE_VARIABLE'
          )

Also by default the schema endpoint will be prefixed by ``/schemas``. If you
want to change that you can change the ``JSONSCHEMAS_ENDPOINT`` configuration
variable.
For more available configuration options see the :doc:`configuration`.

For the above example the two schemas would we available under:

- ``https://myapp.org/schemas/record_schema.json``, and
- ``https://myapp.org/schemas/biology/animal_record_schema.json``


.. _composable-schemas-with-jsonref:

Composable schemas with JSONRef
-------------------------------

A JSON Schema can be a fully fleshed out schema, composed of only the
"primitive" types provided in the specification, but usually this is
impractical when there are sub-entities that are repeated throughout the
schema. For that reason JSON Schema provides ``$ref`` fields which can point
to internal or external schemas. See such an example below:

.. code-block:: json
    :emphasize-lines: 17,18

    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "id": "https://myapp.org/schemas/record.json",
        "definitions": {
            "location": {
                "type": "object",
                "properties": {
                    "city": { "stype": "string" },
                    "country": { "stype": "string" },
                    "address": { "stype": "string" }
                }
            }
        },
        "type": "object",
        "properties": {
            "title": { "type": "string" },
            "creator": { "$ref": "https://foo.org/schemas/person.json" },
            "origin": { "$ref": "#/definitions/location" }
        }
    }

Invenio-JSONSchemas provides the ability to serve the fully resolved schema or
the compact version including one or many ``$ref`` fields. The way to tell
the extension to serve the resolved schema is either by passing the
querystring parameter ``refs=1`` when fetching a schema or by setting the
``JSONSCHEMAS_REPLACE_REFS`` configuration variable to ``True``. Internally the
module uses the `JsonRef <http://jsonref.readthedocs.io/en/stable/>`_ package
for resolving the references in the schema.

If you make a request to ``GET https://myapp.org/schemas/record.json?refs=1``,
you will get something similar to:

.. code-block:: javascript
    :emphasize-lines: 12-19

    {
        "$schema": "http://json-schema.org/draft-04/schema#",
        "id": "https://myapp.org/schemas/record.json",
        "definitions": { ... },
        "type": "object",
        "properties": {
            "title": { "type": "string" },
            "creator": {
                // person.json schema will be fetched and expanded here
                ...
             },
            "origin": {
                "type": "object",
                "properties": {
                    "city": { "stype": "string" },
                    "country": { "stype": "string" },
                    "address": { "stype": "string" }
                }
            }
        }
    }

The module also expands the ``allOf`` tags when the ``resolved=1`` querystring
parameter is passed or the ``JSONSCHEMAS_RESOLVE_SCHEMA`` configuration
variable is set to ``True``. A schema example that includes the ``allOf`` tag
can be shown below:

.. code-block:: javascript

    ...
    "id": "https://myapp.org/schemas/record.json",
    "allOf": [
        { "properties": { "title": { "type": "string" } } },
        { "properties": { "status": { "enum": [ "published", "draft" ] } } }
    ]
    ...

If you make a request to
``GET https://myapp.org/schemas/record.json?resolved=1``
you would get a response in the following format:

.. code-block:: javascript

    ...
    // The "allOf" items have been merged in a single object
    "properties": {
        "title": { "type": "string" },
        "status": { "enum": [ "published", "draft" ] }
    }
    ...


Note on storing absolute URLs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As discussed in this issue_, it is not recommended to store and expose
absolute URLs in the ``$ref``, as they can change in the future. One should
instead try to use DOI/EPIC or other kind of identifiers with the certitude
that they will never change, to avoid broken references.

.. _issue: https://github.com/inveniosoftware/invenio-jsonschemas/issues/23

Using with Invenio-Records
--------------------------

Invenio-JSONSchemas includes an ``invenio_records.jsonresolver`` entry point
item which registers a JSONResolver plugin for Invenio-Records. This basically
means that records that are being validated against schemas that include
``$ref`` s to locally defined schemas won't do an HTTP request to fetch these
schemas, and resolve them locally. You can read more about record validation
in the documentation of `Invenio-Records
<http://invenio-records.readthedocs.io/en/latest/usage.html#record-validation>`_.
"""

from __future__ import absolute_import, print_function

from .ext import InvenioJSONSchemas, InvenioJSONSchemasAPI, InvenioJSONSchemasUI
from .proxies import current_jsonschemas

__version__ = "2.0.0"

__all__ = (
    "__version__",
    "InvenioJSONSchemas",
    "InvenioJSONSchemasUI",
    "InvenioJSONSchemasAPI",
    "current_jsonschemas",
)
