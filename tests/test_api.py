# -*- coding: utf-8 -*-
#
# This file is part of Invenio-JSONSchemas.
# Copyright (C) 2015 CERN.
#
# Invenio-JSONSchemas is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio-JSONSchemas is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio-JSONSchemas; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

from __future__ import print_function, unicode_literals

import pytest


class AppCfg(object):
    SERVER_NAME = 'test.org'


class TestApi:
    @pytest.fixture
    def app(self):
        from flask import Flask
        app = Flask('testapp')
        app.config.from_object(AppCfg)

        from invenio_jsonschemas.views import blueprint
        app.register_blueprint(blueprint)

        return app

    def test_insecurelocation(self, app):
        from invenio_jsonschemas.api import get_schema_from_uri, InsecureSchemaLocation
        with app.app_context():
            with pytest.raises(InsecureSchemaLocation):
                get_schema_from_uri('https://isnotsecure.org/schema.json')

    def test_internalschemaurl(self, app):
        from invenio_jsonschemas.api import internal_schema_url
        with app.app_context():
            assert internal_schema_url('foo', 'test.json') == 'http://test.org/jsonschemas/foo/test.json', 'does not handle simple case'
            assert internal_schema_url('test.json') == 'http://test.org/jsonschemas/test.json', 'does not handle 1-part case'
            assert internal_schema_url('foo', 'barbar', 'test.json') == 'http://test.org/jsonschemas/foo/barbar/test.json', 'does not handle 3-part case'
            assert internal_schema_url('☺.json') == 'http://test.org/jsonschemas/%E2%98%BA.json', 'does not handle unicode case'
