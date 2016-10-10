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


"""Module tests."""

from __future__ import absolute_import, print_function

import json
import os

import mock
import pytest
from flask import Flask
from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonschema import ref_resolver_factory
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from invenio_jsonschemas import InvenioJSONSchemas
from invenio_jsonschemas.config import JSONSCHEMAS_URL_SCHEME
from invenio_jsonschemas.errors import JSONSchemaDuplicate, JSONSchemaNotFound


def test_version():
    """Test version import."""
    from invenio_jsonschemas import __version__
    assert __version__


def test_init():
    """Test extension initialization."""
    app = Flask('testapp')
    ext = InvenioJSONSchemas(app)
    assert 'invenio-jsonschemas' in app.extensions

    app = Flask('testapp')
    ext = InvenioJSONSchemas()
    assert 'invenio-jsonschemas' not in app.extensions
    ext.init_app(app)
    assert 'invenio-jsonschemas' in app.extensions


schema_template = """{{
    "type": "object",
    "properties": {{
        "{}":      {{ "type": "number" }}
    }}
}}"""


def build_schemas(id):
    """Generate a dictionary of "file path" -> "JSON schema"."""
    return {
        'rootschema_{}.json'.format(id):
        schema_template.format('rootschema_{}'.format(id)),
        'sub1/subschema_{}.json'.format(id):
        schema_template.format('subschema_1_{}'.format(id)),
        'sub2/subschema_{}.json'.format(id):
        schema_template.format('subschema_2_{}'.format(id)),
        'sub3/subschema_{}.json'.format(id):
        schema_template.format('subschema_3_{}'.format(id)),
    }


def test_api(app, dir_factory):
    """Test API."""
    ext = InvenioJSONSchemas(app, entry_point_group=None)
    schema_files = build_schemas(1)
    with dir_factory(schema_files) as directory:
        ext.register_schemas_dir(directory)
        for path in schema_files.keys():
            # test get_schema_dir
            assert ext.get_schema_dir(path) == directory
            # test get_schema_path
            assert ext.get_schema_path(path) == \
                os.path.join(directory, path)
            # test get_schema
            assert ext.get_schema(path) == json.loads(schema_files[path])
        # test list_schemas
        assert set(schema_files.keys()) == set(ext.list_schemas())
        # test failure when asking for non existing schemas fails
        with pytest.raises(JSONSchemaNotFound) as exc_info:
            ext.get_schema('not_existing_schema.json')
        assert exc_info.value.schema == 'not_existing_schema.json'
        # test failure when asking for non existing schemas' path
        with pytest.raises(JSONSchemaNotFound) as exc_info:
            ext.get_schema_path('not_existing_schema.json')
        assert exc_info.value.schema == 'not_existing_schema.json'


class mock_open(object):
    """Mock the builtin 'open' and count the file requests."""

    counter = 0

    def __init__(self, path):
        """Initialize the open with a path."""
        self.path = path

    def __enter__(self, *args, **kwargs):
        """Context enter."""
        self.f = open(self.path)
        mock_open.counter += 1
        return self.f

    def __exit__(self, *args, **kwargs):
        """Context exit."""
        self.f.close()


def test_cache(app, dir_factory):
    """Test cached schema loading."""
    m = mock_open
    with mock.patch('invenio_jsonschemas.ext.open', m):
        ext = InvenioJSONSchemas(app, entry_point_group=None)
        schema_files = build_schemas(1)

        with dir_factory(schema_files) as directory:
            ext.register_schemas_dir(directory)
            assert m.counter == 0
            ext.get_schema('rootschema_1.json')
            assert m.counter == 1
            ext.get_schema('rootschema_1.json')
            ext.get_schema('rootschema_1.json')
            assert m.counter == 1
            ext.get_schema('sub1/subschema_1.json')
            assert m.counter == 2
            ext.get_schema('sub1/subschema_1.json')
            assert m.counter == 2


def test_register_schema(app, dir_factory):
    """Test register schema."""
    ext = InvenioJSONSchemas(app, entry_point_group=None)
    schema_files = build_schemas(1)
    with dir_factory(schema_files) as directory:
        registered_schemas = set(list(schema_files.keys())[:1])
        nonregistered_schema = [s for s in schema_files if s not in
                                registered_schemas]
        for schema in registered_schemas:
            ext.register_schema(directory, schema)
        assert set(ext.list_schemas()) == registered_schemas

        for schema in nonregistered_schema:
            with pytest.raises(JSONSchemaNotFound):
                ext.get_schema(schema)


def test_redefine(app, dir_factory):
    """Test redefine."""
    ext = InvenioJSONSchemas(app, entry_point_group=None)
    schema_files = build_schemas(1)
    with dir_factory(schema_files) as dir1, \
            dir_factory(schema_files) as dir2:
        ext.register_schemas_dir(dir1)
        # register schemas from a directory which have the same relative
        # paths
        with pytest.raises(JSONSchemaDuplicate) as exc_info:
            ext.register_schemas_dir(dir2)
        assert exc_info.value.schema in schema_files.keys()


def test_view(app, pkg_factory, mock_entry_points):
    """Test view."""
    schema_files_1 = build_schemas(1)
    schema_files_2 = build_schemas(2)
    schema_files_3 = build_schemas(3)

    all_schemas = dict()
    all_schemas.update(schema_files_1)
    all_schemas.update(schema_files_2)
    all_schemas.update(schema_files_3)

    entry_point_group = 'invenio_jsonschema_test_entry_point'
    endpoint = '/testschemas'
    app.config['JSONSCHEMAS_ENDPOINT'] = endpoint
    with pkg_factory(schema_files_1) as pkg1, \
            pkg_factory(schema_files_2) as pkg2, \
            pkg_factory(schema_files_3) as pkg3:
        mock_entry_points.add(entry_point_group, 'entry1', pkg1)
        mock_entry_points.add(entry_point_group, 'entry2', pkg2)
        mock_entry_points.add(entry_point_group, 'entry3', pkg3)
        # Test an alternative way of initializing the app
        # with InvenioJSONSchemas
        ext = InvenioJSONSchemas(entry_point_group=entry_point_group)
        ext = ext.init_app(app)
        # Test if all the schemas are correctly found
        assert set(ext.list_schemas()) == set(all_schemas.keys())

        with app.test_client() as client:
            for name, schema in all_schemas.items():
                res = client.get("{0}/{1}".format(endpoint, name))
                assert res.status_code == 200
                assert json.loads(schema) == \
                    json.loads(res.get_data(as_text=True))
            res = client.get("{0}/nonexisting".format(endpoint))
            assert res.status_code == 404


def test_replace_refs_in_view(app, pkg_factory, mock_entry_points):
    """Test replace refs config in view."""
    schemas = {
        'root.json': '{"$ref": "sub/schema.json"}',
        'sub/schema.json': schema_template.format('test')
    }

    entry_point_group = 'invenio_jsonschema_test_entry_point'
    endpoint = '/testschemas'
    app.config['JSONSCHEMAS_ENDPOINT'] = endpoint
    with pkg_factory(schemas) as pkg1:
        mock_entry_points.add(entry_point_group, 'entry1', pkg1)
        ext = InvenioJSONSchemas(entry_point_group=entry_point_group)
        ext = ext.init_app(app)

        with app.test_client() as client:
            res = client.get('{0}/{1}'.format(endpoint, 'root.json'))
            assert res.status_code == 200
            assert json.loads(schemas['root.json']) == \
                json.loads(res.get_data(as_text=True))

            app.config['JSONSCHEMAS_REPLACE_REFS'] = True

            res = client.get('{0}/{1}'.format(endpoint, 'root.json'))
            assert res.status_code == 200
            assert json.loads(schemas['sub/schema.json']) == \
                json.loads(res.get_data(as_text=True))

            app.config['JSONSCHEMAS_REPLACE_REFS'] = False

            res = client.get('{0}/{1}?refs=1'.format(endpoint, 'root.json'))
            assert res.status_code == 200
            assert json.loads(schemas['sub/schema.json']) == \
                json.loads(res.get_data(as_text=True))


def test_alternative_entry_point_group_init(app, pkg_factory,
                                            mock_entry_points):
    """Test initializing the entry_point_group after creating the extension."""
    schema_files_1 = build_schemas(1)
    schema_files_2 = build_schemas(2)

    all_schemas = dict()
    all_schemas.update(schema_files_1)
    all_schemas.update(schema_files_2)

    entry_point_group = 'invenio_jsonschema_test_entry_point'
    with pkg_factory(schema_files_1) as pkg1, \
            pkg_factory(schema_files_2) as pkg2:
        mock_entry_points.add(entry_point_group, 'entry1', pkg1)
        mock_entry_points.add(entry_point_group, 'entry2', pkg2)
        # Test an alternative way of initializing the app and entry_point_group
        # with InvenioJSONSchemas
        ext = InvenioJSONSchemas()
        ext = ext.init_app(app, entry_point_group=entry_point_group)
        # Test if all the schemas are correctly found
        assert set(ext.list_schemas()) == set(all_schemas.keys())


def mock_get_schema(self, path):
    """Mock the ``get_schema`` method of InvenioJSONSchemasState."""
    assert path == 'some_schema.json'
    ret_schema = {
        "$schema": "http://json-schema.org/schema#",
        "id": "http://localhost/schemas/some_schema.json",
        "type": "object",
        "properties": {
            "foo": {"type": "string", },
            "bar": {"type": "integer", },
        }
    }
    return ret_schema


@mock.patch('invenio_jsonschemas.ext.InvenioJSONSchemasState.get_schema',
            mock_get_schema)
def test_jsonresolver():
    """Test extension initialization."""
    app = Flask('testapp')
    InvenioJSONSchemas(app)
    assert 'invenio-jsonschemas' in app.extensions
    with app.app_context():
        json_resolver = JSONResolver(
            plugins=['invenio_jsonschemas.jsonresolver', ])
        schema = {'$ref': 'http://localhost/schemas/some_schema.json'}
        resolver_cls = ref_resolver_factory(json_resolver)
        resolver = resolver_cls.from_schema(schema)
        with pytest.raises(ValidationError) as exc_info:
            validate({'foo': 'foo_value', 'bar': "not_an_int"}, schema,
                     resolver=resolver)
        assert exc_info.value.schema == {'type': 'integer'}


@pytest.mark.parametrize('url_scheme', [
    None, 'http', 'https'
])
def test_url_mapping(app, dir_factory, url_scheme):
    """Test register schema."""
    app.config['SERVER_NAME'] = 'example.org'
    app.config['JSONSCHEMAS_HOST'] = 'inveniosoftware.org'
    if url_scheme is not None:
        app.config['JSONSCHEMAS_URL_SCHEME'] = url_scheme
    else:
        # test with default url scheme configuration
        url_scheme = JSONSCHEMAS_URL_SCHEME

    ext = InvenioJSONSchemas(app, entry_point_group=None)
    schema_files = build_schemas(1)

    with dir_factory(schema_files) as directory:
        ext.register_schemas_dir(directory)
        with app.app_context():
            assert 'sub1/subschema_1.json' == ext.url_to_path(
                '{0}://inveniosoftware.org/schemas/sub1/subschema_1.json'
                .format(url_scheme))
            assert ext.url_to_path(
                '{0}://inveniosoftware.org/schemas/invalid.json'
                .format(url_scheme)) is None
            assert ext.url_to_path(
                '{0}://example.org/schemas/sub1/subschema_1.json'
                .format(url_scheme)) is None

            assert (
                '{0}://inveniosoftware.org/schemas/sub1/subschema_1.json'
                .format(url_scheme)
            ) == ext.path_to_url('sub1/subschema_1.json')
            assert ext.path_to_url('invalid.json') is None
