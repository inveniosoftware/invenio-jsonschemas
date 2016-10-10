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

"""Invenio module for building and serving JSONSchemas."""

from __future__ import absolute_import, print_function

import json
import os

from flask import Blueprint, abort, current_app, jsonify, request, \
    send_from_directory
from jsonref import JsonRef

from .errors import JSONSchemaNotFound


def create_blueprint(state):
    """Create blueprint serving JSON schemas.

    :param state: :class:`invenio_jsonschemas.ext.InvenioJSONSchemasState`
        instance used to retrieve the schemas.
    """
    blueprint = Blueprint(
        'invenio_jsonschemas',
        __name__
    )

    @blueprint.route('/<path:schema_path>')
    def get_schema(schema_path):
        """Retrieve a schema."""
        try:
            schema_dir = state.get_schema_dir(schema_path)
        except JSONSchemaNotFound:
            abort(404)
        if request.args.get('refs',
                            current_app.config.get('JSONSCHEMAS_REPLACE_REFS'),
                            type=int):
            with open(os.path.join(schema_dir, schema_path), 'r') as file_:
                schema = json.load(file_)
            return jsonify(JsonRef.replace_refs(
                schema, base_uri=request.base_url,
                loader=state.loader_cls() if state.loader_cls else None,
            ))
        else:
            return send_from_directory(schema_dir, schema_path)

    return blueprint
