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

"""JSON Resolver for JSON Schemas."""

from __future__ import absolute_import, print_function

from flask import current_app
from jsonresolver import hookimpl
from werkzeug.routing import Rule


@hookimpl.hookimpl
def jsonresolver_loader(url_map):
    """JSON Resolver plugin.

    Injected into Invenio-Records JSON resolver."""
    url_map.add(Rule(
        "{0}/<path:schema_path>".format(
            current_app.config['JSONSCHEMAS_ENDPOINT']),
        endpoint=schemas_jsonresolver,
        host=current_app.config['JSONSCHEMAS_HOST']))


def schemas_jsonresolver(schema_path):
    """Resolve a JSON Schema."""
    return current_app.extensions['invenio-jsonschemas'].get_schema(
        schema_path)
