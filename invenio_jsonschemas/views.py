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

"""Views provided by Invenio-JSONSchemas."""

import datetime
import time

from wsgiref.handlers import format_date_time

from flask import Blueprint, jsonify, render_template

from flask_babel import lazy_gettext as _

from flask_breadcrumbs import default_breadcrumb_root, register_breadcrumb

try:
    from invenio.ext.cache import cache
except ImportError:
    from flask_cache import Cache
    cache = Cache()

from .api import get_schema_data, get_schemas, internal_schema_url

from .utils import split_path, tree_insert, tree_sort


blueprint = Blueprint(
    'jsonschemas',
    __name__,
    url_prefix='/jsonschemas',
    static_folder='static',
    template_folder='templates',
)

default_breadcrumb_root(blueprint, '.jsonschemas')


@blueprint.route('/', methods=['GET', 'POST'])
@register_breadcrumb(blueprint, '.', _('JSON Schemas'))
def index():
    """Render schema index with all known schema files."""
    tree = dict()
    for name in get_schemas():
        path = split_path(name)
        tree_insert(tree, path[:-1], {
            'name': name,
            'link': internal_schema_url(*path)
        })

    return render_template('jsonschemas/schema.html', tree=tree_sort(tree))


@blueprint.route('/<path:path>')
@cache.memoize(timeout=3600*24*3)
def schema(path):
    """Serve schema file."""
    now = datetime.datetime.now()
    expires_time = now + datetime.timedelta(seconds=3600*24*3)
    response = jsonify(get_schema_data(path))
    response.headers['Cache-Control'] = 'public'
    response.headers['Expires'] = format_date_time(
        time.mktime(expires_time.timetuple())
    )
    return response
