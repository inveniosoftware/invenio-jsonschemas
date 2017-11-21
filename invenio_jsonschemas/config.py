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

"""Default configuration."""

JSONSCHEMAS_HOST = 'localhost'
"""Default json schema host."""

JSONSCHEMAS_ENDPOINT = '/schemas'
"""Default schema endpoint."""

JSONSCHEMAS_URL_SCHEME = 'https'
"""Default url scheme for schemas."""

JSONSCHEMAS_REPLACE_REFS = False
"""Whether to resolve $ref before serving a schema."""

JSONSCHEMAS_RESOLVE_SCHEMA = False
"""Whether to resolve schema using the Resolver Class.

If is ``True``, will replace $ref and run the
:py:const:`invenio_jsonschemas.config.JSONSCHEMAS_RESOLVER_CLS` class
before serving a schema.
"""

JSONSCHEMAS_LOADER_CLS = None
"""Loader class used in ``JSONRef`` when replacing ``$ref``."""

JSONSCHEMAS_RESOLVER_CLS = 'invenio_jsonschemas.utils.resolve_schema'
"""Resolver used to resolve the schema.

if :py:const:`invenio_jsonschemas.config.JSONSCHEMAS_RESOLVE_SCHEMA` is
``True`` or there is ``?resolved=1`` parameter on the request the resolver
will run over the schema. This can be used for custom schemas resolver.
"""

JSONSCHEMAS_REGISTER_ENDPOINTS_API = True
"""Register the endpoints on the API app."""

JSONSCHEMAS_REGISTER_ENDPOINTS_UI = True
"""Register the endpoints on the UI app."""
