# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015 CERN.
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

import pkg_resources

from .errors import JSONSchemaDuplicate, JSONSchemaNotFound
from .views import create_blueprint

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache


class InvenioJSONSchemasState(object):
    """InvenioJSONSchemas state and api."""

    def __init__(self, app):
        """Constructor.

        :param app: application registering this state
        """
        self.app = app
        self.schemas = {}

    def register_schemas_dir(self, directory):
        """Recursively register all json-schemas in a directory.

        :param directory: directory path.
        """
        for root, dirs, files in os.walk(directory):
            dir_path = os.path.relpath(root, directory)
            if dir_path == '.':
                dir_path = ''
            for file in files:
                if file.lower().endswith((".json")):
                    schema_name = os.path.join(dir_path, file)
                    if schema_name in self.schemas:
                        raise JSONSchemaDuplicate(
                            schema_name,
                            self.schemas[schema_name],
                            directory
                        )
                    self.schemas[schema_name] = os.path.abspath(directory)

    def register_schema(self, directory, path):
        """Register a json-schema.

        :param directory: root directory path.
        :param path: schema path, relative to the root directory.
        """
        self.schemas[path] = os.path.abspath(directory)

    def get_schema_dir(self, path):
        """Retrieve the directory containing the given schema.

        :param path: schema path, relative to the directory when it was
        registered.
        """
        if path not in self.schemas:
            raise JSONSchemaNotFound(path)
        return self.schemas[path]

    def get_schema_path(self, path):
        """Compute the schema's absolute path from a schema relative path.

        :param path: relative path of the schema.
        """
        if path not in self.schemas:
            raise JSONSchemaNotFound(path)
        return os.path.join(self.schemas[path], path)

    @lru_cache(maxsize=1000)
    def get_schema(self, path):
        """Retrieve a schema.

        :param path: schema's relative path.
        """
        if path not in self.schemas:
            raise JSONSchemaNotFound(path)
        with open(os.path.join(self.schemas[path], path)) as file:
            return json.load(file)

    def list_schemas(self):
        """List all JSON-schema names.

        :Return: list of schema names.
        :rtype: list
        """
        return self.schemas.keys()


class InvenioJSONSchemas(object):
    """Invenio-JSONSchemas extension.

    Register blueprint serving registered schemas and can be used as an api
    to register those schemas.

    Note: JSON schemas are served as static files. Thus their "id" and "$ref"
    fields might not match the Flask application's host and port.
    """

    CONFIG_ENDPOINT = 'JSONSCHEMAS_ENDPOINT'

    def __init__(self, app=None, **kwargs):
        """Extension initialization."""
        self.kwargs = kwargs
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, entry_point_group=None):
        """Flask application initialization."""
        self.init_config(app)

        if not entry_point_group:
            entry_point_group = self.kwargs['entry_point_group'] \
                if 'entry_point_group' in self.kwargs \
                else 'invenio_jsonschemas.schemas'

        state = InvenioJSONSchemasState(app)

        # Load the json-schemas from extension points.
        if entry_point_group:
            for base_entry in pkg_resources.iter_entry_points(
                    entry_point_group):
                directory = os.path.dirname(base_entry.load().__file__)
                state.register_schemas_dir(directory)

        app.register_blueprint(
            create_blueprint(state),
            url_prefix=app.config[InvenioJSONSchemas.CONFIG_ENDPOINT]
        )

        self._state = app.extensions['invenio-jsonschemas'] = state
        return state

    def init_config(self, app):
        """Initialize configuration."""
        app.config.setdefault(InvenioJSONSchemas.CONFIG_ENDPOINT,
                              '/schemas')
        app.config.setdefault('JSONSCHEMAS_HOST', 'http://localhost')

    def __getattr__(self, name):
        """Proxy to state object."""
        return getattr(self._state, name, None)
