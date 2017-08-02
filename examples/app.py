# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Minimal Flask application example for development.

SPHINX-START

Run example development server:

.. code-block:: console

    $ pip install -e .[all]
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
app.config['JSONSCHEMAS_ENDPOINT'] = '/schemas'

# Initialize the application with the InvenioJSONSchema extension.
# This registers the jsonschemas from examples/samplepkg/jsonschemas as
# samplepkg's setup.py has the "invenio_jsonschemas.schemas" entrypoint.
ext = InvenioJSONSchemas(app)

# list all registered schemas
print('SCHEMAS >> {}'.format(ext.list_schemas()))
for schema in ext.list_schemas():
    print('=' * 50)
    print('SCHEMA {}'.format(schema))
    # retrieve the schema content
    print(json.dumps(ext.get_schema(schema), indent=4))

# InvenioJSONSchemas registers a blueprint serving the JSON schemas
print('>> You can retrieve the schemas using the url in their "id".')

if __name__ == "__main__":
    app.run()
