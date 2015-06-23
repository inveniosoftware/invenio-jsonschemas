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

"""Bundles for Invenio-JSONSchemas."""

from __future__ import unicode_literals

from invenio.base.bundles import invenio as _invenio_js, \
    jquery as _j
from invenio.ext.assets import Bundle, RequireJSFilter

schema_js = Bundle(
    "js/jsonschemas/schema.js",
    output='jsonschema.js',
    filters=RequireJSFilter(
        exclude=[_j, _invenio_js],
    ),
    bower={
        'renderjson': 'latest',
    }
)

schema_css = Bundle(
    "less/jsonschemas/schema.less",
    output='jsonschema.css',
    filters="less,cleancss",
)
