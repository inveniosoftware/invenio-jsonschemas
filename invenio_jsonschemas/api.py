# -*- coding: utf-8 -*-
#
# This file is part of Invenio-JSONSchemas.
# Copyright (C) 2015 CERN.
#
# Invenio-JSONSchemas is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio-JSONSchemas is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio-JSONSchemas; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.

"""Schema API.

This collects JSON schemas of all modules. These should be located in the
`jsonschemas` directory relative to the module root. It also generates schemas
for all entries located under `jsonschemas/forms/*` by doing an `allOf` merge
with the schema configured using `JSONSCHEMAS_BASE_SCHEMA`. The name of the
results are formed by doing the `s|forms|records|` rename operation. No
virtual schemas are generated in case of:

- The target name already exists.
- The base schema is not configured.

.. note::
    Be aware the the schema names do NOT include the `jsonschemas/` prefix.
"""

import copy
import json
import os
import os.path
import urlparse

from flask import current_app, url_for

from jsonpointer import resolve_pointer

import jsonschema

from speaklater import _LazyString

from .registry import json_schemas_mapping as schema_files


class InsecureSchemaLocation(Exception):

    """The try to load a JSON schema from an insecure location."""


def internal_schema_url(*parts):
    """Return the URL to an internal JSON schema."""
    return url_for(
        'jsonschemas.schema',
        path=os.path.join(*parts),
        _external=True
    )


def get_schemas():
    """Return a list of all available schemas.

    This might include virtual/generated schemas.
    """
    schemas = set()
    for f in schema_files.iterkeys():
        schemas.add(f)

        # also add a record for all forms
        if f.startswith('forms' + os.path.sep):
            f2 = f.replace('forms', 'records', 1)
            schemas.add(f2)
    return schemas


def get_schema_data(f, default=None):
    """Return schema data (dict) for a given schema.

    In case the schema does not exist, `default` is returned.
    """
    # try to serve the resource
    if f in schema_files:
        with open(schema_files[f]) as resource:
            return json.load(resource)

    # now try to rewrite records to forms
    base = current_app.config.get('JSONSCHEMAS_BASE_SCHEMA')
    if base and f.startswith('records' + os.path.sep):
        f2 = f.replace('records', 'forms', 1)
        if f2 in schema_files:
            return {
                'allOf': [
                    {'$ref': internal_schema_url(base)},
                    {'$ref': internal_schema_url(f2)}
                ]
            }

    # ok, not found, too bad
    return default


def get_schema_from_uri(uri):
    """Get and parse a JSON schema from the given URI.

    Internal schemas are loaded from the file system. Caching may apply for
    internal and external schemas. JSON pointers given as fragment of the URI
    are supported.
    """
    # split the fragment
    uri_parsed = urlparse.urlparse(uri)

    # 1. interal resource?
    base = url_for('jsonschemas.schema', path='', _external=True)
    base_parsed = urlparse.urlparse(base)
    if base_parsed.scheme == uri_parsed.scheme \
            and base_parsed.netloc == uri_parsed.netloc \
            and uri_parsed.path.startswith(base_parsed.path):
        internal_path = uri_parsed.path.split(base_parsed.path, 1)[1]
        data = get_schema_data(internal_path)

        return resolve_pointer(
            data,
            uri_parsed.fragment
        )

    # 2. external resource
    # FIXME support whitelisting of secure location
    raise InsecureSchemaLocation(
        'Requested schema located on insecure location: ' + uri
    )


def validate_json(json, schema=None, additional_properties=None):
    """Validate JSON against a given schema.

    If no schema is provided, the `$schema` attribute of the JSON object will
    be used. In both cases, schema URIs and parsed schemas are supported.
    """
    # should we get the schema from the JSON itself?
    if not schema:
        schema = json.get('$schema', {})

    # is the schema a link or the parsed schema?
    if isinstance(schema, basestring) or isinstance(schema, _LazyString):
        schema = get_schema_from_uri(schema)

    # allow additional properties?
    if additional_properties is not None:
        schema['additionalProperties'] = additional_properties

    # remove `$schema`, because jsonschema does not handle or ignore it
    # instead it would result in an validation error
    data = copy.deepcopy(json)
    data.pop('$schema', None)

    jsonschema.validate(data, schema)
    return True
