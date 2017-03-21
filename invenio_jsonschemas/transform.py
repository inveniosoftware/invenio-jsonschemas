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

"""JSONSchema transformation methods."""

from copy import deepcopy
from flask import request
from jsonref import JsonRef

from .errors import JSONSchemaNotFound


def transform_all_of(state, schema):
    """Transform schema allOf."""
    def traverse(schema):
        if isinstance(schema, dict):
            if 'allOf' in schema:
                for x in schema['allOf']:
                    sub_schema = x
                    sub_schema.pop('title', None)
                    schema = merge_dicts(schema, sub_schema)
                schema.pop('allOf')
                schema = traverse(schema)
            elif 'properties' in schema:
                for x in schema.get('properties', []):
                    schema['properties'][x] = traverse(
                        schema['properties'][x])
            elif 'items' in schema:
                schema['items'] = traverse(schema['items'])
        return schema

    return traverse(schema)


def transform_refs(state, schema):
    """Transform schema refs."""
    try:
        _schema = JsonRef.replace_refs(
            schema, base_uri=request.base_url,
            loader=state.loader_cls() if state.loader_cls else None,
        )

        return _schema
    except:
        raise JSONSchemaNotFound(schema)


def merge_dicts(first, second):
    """Merge the 'second' multiple-dictionary into the 'first' one."""
    new = deepcopy(first)
    for k, v in second.items():
        if isinstance(v, dict) and v:
            ret = merge_dicts(new.get(k, dict()), v)
            new[k] = ret
        else:
            new[k] = second[k]
    return new
