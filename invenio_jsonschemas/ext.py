# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module for building and serving JSONSchemas."""

from __future__ import absolute_import, print_function

import json
import os
from urllib.parse import urljoin

import pkg_resources
import six
from flask import request
from jsonref import JsonRef
from six.moves.urllib.parse import urlsplit
from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.utils import cached_property, import_string

from . import config
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
        self.url_map = Map([Rule(
            '{0}/<path:path>'.format(self.app.config['JSONSCHEMAS_ENDPOINT']),
            endpoint='schema',
            host=self.app.config['JSONSCHEMAS_HOST'],
        )], host_matching=True)

    def register_schemas_dir(self, directory):
        """Recursively register all json-schemas in a directory.

        :param directory: directory path.
        """
        for root, dirs, files in os.walk(directory):
            dir_path = os.path.relpath(root, directory)
            if dir_path == '.':
                dir_path = ''
            for file_ in files:
                if file_.lower().endswith(('.json')):
                    schema_name = os.path.join(dir_path, file_)
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

        :param path: Schema path, relative to the directory where it was
            registered.
        :raises invenio_jsonschemas.errors.JSONSchemaNotFound: If no schema
            was found in the specified path.
        :returns: The schema directory.
        """
        if path not in self.schemas:
            raise JSONSchemaNotFound(path)
        return self.schemas[path]

    def get_schema_path(self, path):
        """Compute the schema's absolute path from a schema relative path.

        :param path: relative path of the schema.
        :raises invenio_jsonschemas.errors.JSONSchemaNotFound: If no schema
            was found in the specified path.
        :returns: The absolute path.
        """
        if path not in self.schemas:
            raise JSONSchemaNotFound(path)
        return os.path.join(self.schemas[path], path)

    @lru_cache(maxsize=1000)
    def get_schema(self, path, with_refs=False, resolved=False):
        """Retrieve a schema.

        :param path: schema's relative path.
        :param with_refs: replace $refs in the schema.
        :param resolved: resolve schema using the resolver
            :py:const:`invenio_jsonschemas.config.JSONSCHEMAS_RESOLVER_CLS`
        :raises invenio_jsonschemas.errors.JSONSchemaNotFound: If no schema
            was found in the specified path.
        :returns: The schema in a dictionary form.
        """
        if path not in self.schemas:
            raise JSONSchemaNotFound(path)
        with open(os.path.join(self.schemas[path], path)) as file_:
            schema = json.load(file_)
            if with_refs:
                schema = JsonRef.replace_refs(
                    schema,
                    base_uri=request.base_url,
                    loader=self.loader_cls() if self.loader_cls else None,
                )
            if resolved:
                schema = self.resolver_cls(schema)
            return schema

    def list_schemas(self):
        """List all JSON-schema names.

        :returns: list of schema names.
        :rtype: list
        """
        return self.schemas.keys()

    def url_to_path(self, url):
        """Convert schema URL to path.

        :param url: The schema URL.
        :returns: The schema path or ``None`` if the schema can't be resolved.
        """
        parts = urlsplit(url)
        try:
            loader, args = self.url_map.bind(parts.netloc).match(parts.path)
            path = args.get('path')
            if loader == 'schema' and path in self.schemas:
                return path
        except HTTPException:
            return None

    def path_to_url(self, path):
        """Build URL from a path.

        :param path: relative path of the schema.
        :returns: The schema complete URL or ``None`` if not found.
        """
        if path not in self.schemas:
            return None
        return self.url_map.bind(
            self.app.config['JSONSCHEMAS_HOST'],
            url_scheme=self.app.config['JSONSCHEMAS_URL_SCHEME']
        ).build(
            'schema', values={'path': path}, force_external=True)

    @cached_property
    def loader_cls(self):
        """Loader class used in `JsonRef.replace_refs`."""
        cls = self.app.config['JSONSCHEMAS_LOADER_CLS']
        if isinstance(cls, six.string_types):
            return import_string(cls)
        return cls

    @cached_property
    def resolver_cls(self):
        """Loader to resolve the schema."""
        cls = self.app.config['JSONSCHEMAS_RESOLVER_CLS']
        if isinstance(cls, six.string_types):
            return import_string(cls)
        return cls

    def refresolver_store(self):
        """Builds a local ref resolver store with aliased local references.

        Abstracts configurations such as URI scheme and hostname under
        the configured non-standard URI scheme.
        """
        store = {}
        local_refresolver_uri_scheme = uri_scheme = self.app.config.get(
            "JSONSCHEMAS_LOCAL_REFRESOLVER_URI_SCHEME")
        for schema_uri, schema in self.schemas.items():
            schema = self.get_schema(schema_uri)
            schema_uri = "{uri_scheme}{schema_path}".format(
                uri_scheme=local_refresolver_uri_scheme,
                schema_path=schema_uri.lstrip("/"),
            )
            if schema.get("$id"):
                assert schema.get("$id") == schema_uri

            store[schema_uri] = schema

        return store


class InvenioJSONSchemas(object):
    """Invenio-JSONSchemas extension.

    Register blueprint serving registered schemas and can be used as an api
    to register those schemas.

    .. note::

        JSON schemas are served as static files. Thus their "id" and "$ref"
        fields might not match the Flask application's host and port.
    """

    def __init__(self, app=None, **kwargs):
        """Extension initialization.

        :param app: The Flask application. (Default: ``None``)
        """
        self.kwargs = kwargs
        if app:
            self.init_app(app, **kwargs)

    def init_app(self, app, entry_point_group=None, register_blueprint=True,
                 register_config_blueprint=None):
        """Flask application initialization.

        :param app: The Flask application.
        :param entry_point_group: The group entry point to load extensions.
            (Default: ``invenio_jsonschemas.schemas``)
        :param register_blueprint: Register the blueprints.
        :param register_config_blueprint: Register blueprint for the specific
            app from a config variable.
        """
        self.init_config(app)

        if not entry_point_group:
            entry_point_group = self.kwargs['entry_point_group'] \
                if 'entry_point_group' in self.kwargs \
                else 'invenio_jsonschemas.schemas'

        state = InvenioJSONSchemasState(app)

        # Load the json-schemas from extension points.
        if entry_point_group:
            whitelisted_entries = app.config['JSONSCHEMAS_SCHEMAS']
            for base_entry in pkg_resources.iter_entry_points(
                    entry_point_group):
                if whitelisted_entries is None or \
                        base_entry.name in whitelisted_entries:
                    directory = os.path.dirname(base_entry.load().__file__)
                    state.register_schemas_dir(directory)

        # Init blueprints
        _register_blueprint = app.config.get(register_config_blueprint)
        if _register_blueprint is not None:
            register_blueprint = _register_blueprint

        if register_blueprint:
            app.register_blueprint(
                create_blueprint(state),
                url_prefix=app.config['JSONSCHEMAS_ENDPOINT']
            )

        self._state = app.extensions['invenio-jsonschemas'] = state
        return state

    def init_config(self, app):
        """Initialize configuration."""
        for k in dir(config):
            if k.startswith('JSONSCHEMAS_'):
                app.config.setdefault(k, getattr(config, k))

        host_setting = app.config['JSONSCHEMAS_HOST']
        if not host_setting or host_setting == 'localhost':
            app.logger.warning('JSONSCHEMAS_HOST is set to {0}'.format(
                host_setting))

    def __getattr__(self, name):
        """Proxy to state object."""
        return getattr(self._state, name, None)


class InvenioJSONSchemasUI(InvenioJSONSchemas):
    """Invenio-JSONSchemas extension for UI."""

    def init_app(self, app):
        """Flask application initialization.

        :param app: The Flask application.
        """
        return super(InvenioJSONSchemasUI, self).init_app(
            app,
            register_config_blueprint='JSONSCHEMAS_REGISTER_ENDPOINTS_UI'
        )


class InvenioJSONSchemasAPI(InvenioJSONSchemas):
    """Invenio-JSONSchemas extension for API."""

    def init_app(self, app):
        """Flask application initialization.

        :param app: The Flask application.
        """
        return super(InvenioJSONSchemasAPI, self).init_app(
            app,
            register_config_blueprint='JSONSCHEMAS_REGISTER_ENDPOINTS_API'
        )
