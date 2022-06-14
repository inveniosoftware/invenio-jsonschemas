# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Minimal Flask application example for development.

SPHINX-START

Run example development server:

.. code-block:: console

    $ pip install -e .[all]
    $ cd examples
    $ ./app-setup.sh
    $ python app.py

Open the schema from web:

.. code-block:: console

    $ curl http://localhost:5000/schemas/record_schema.json
    $ curl http://localhost:5000/schemas/biology/animal_record_schema.json

Teardown the application:

.. code-block:: console

    $ ./app-teardown.sh

SPHINX-END
"""

from __future__ import absolute_import, print_function

import json

from flask import Flask

from invenio_jsonschemas import InvenioJSONSchemas

# Create Flask application
app = Flask(__name__)

# set the endpoint serving the JSON schemas
app.config["JSONSCHEMAS_ENDPOINT"] = "/schemas"

# Initialize the application with the InvenioJSONSchema extension.
# This registers the jsonschemas from examples/samplepkg/jsonschemas as
# samplepkg's setup.py has the "invenio_jsonschemas.schemas" entrypoint.
ext = InvenioJSONSchemas(app)

# list all registered schemas
print("SCHEMAS >> {}".format(ext.list_schemas()))
for schema in ext.list_schemas():
    print("=" * 50)
    print("SCHEMA {}".format(schema))
    # retrieve the schema content
    print(json.dumps(ext.get_schema(schema), indent=4))

# InvenioJSONSchemas registers a blueprint serving the JSON schemas
print('>> You can retrieve the schemas using the url in their "id".')

if __name__ == "__main__":
    app.run()
