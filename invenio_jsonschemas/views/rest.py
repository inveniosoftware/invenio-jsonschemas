# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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

from flask import Blueprint, abort, jsonify
from flask.views import MethodView

from ..errors import JSONSchemaNotFound


def create_blueprint(state):
    """Create blueprint serving JSON schemas.

    :param state: :class:`invenio_jsonschemas.ext.InvenioJSONSchemasState`
        instance used to retrieve the schemas.
    """
    blueprint = Blueprint(
        'invenio_jsonschemas_rest',
        __name__
    )

    for endpoint, e_item in \
            state.app.config['JSONSCHEMAS_REST_ENDPOINTS'].iteritems():

        blueprint.add_url_rule(
            '/{0}/<path:schema_path>'.format(endpoint),
            view_func=SchemaView.as_view(
                'schema_transform_{0}'.format(endpoint),
                state=state,
                tranform=endpoint
            )
        )

    return blueprint


class SchemaView(MethodView):

    def __init__(self, state=None, tranform=None):

        self.state = state
        self.tranform = tranform

    def get(self, schema_path=None):
        try:
            schema = self.state.get_schema_transformed(
                schema_path, self.tranform)
            return jsonify(schema)
        except JSONSchemaNotFound:
            abort(404)
