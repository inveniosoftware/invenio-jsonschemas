# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016, 2017 CERN.
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
        __name__,
    )

    @blueprint.route('/<path:schema_path>')
    def get_schema(schema_path):
        """Retrieve a schema."""
        try:
            schema_dir = state.get_schema_dir(schema_path)
        except JSONSchemaNotFound:
            abort(404)

        resolved = request.args.get(
            'resolved',
            current_app.config.get('JSONSCHEMAS_RESOLVE_SCHEMA'),
            type=int
        )

        with_refs = request.args.get(
            'refs',
            current_app.config.get('JSONSCHEMAS_REPLACE_REFS'),
            type=int
        ) or resolved

        if resolved or with_refs:
            schema = state.get_schema(
                schema_path,
                with_refs=with_refs,
                resolved=resolved
            )
            return jsonify(schema)
        else:
            return send_from_directory(schema_dir, schema_path)

    return blueprint
