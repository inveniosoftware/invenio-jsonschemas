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

"""Schema registry.

This collects JSON schemas of all modules. These should be located in the
`jsonschemas` directory relative to the module root.

.. warning::
    Do **NOT** use this module as an API, because it might not provide you all
    schemas (e.g. virtual schemas are missing).
"""

import os

from flask_registry import PkgResourcesDirDiscoveryRegistry, RegistryProxy
from werkzeug.local import LocalProxy


class RecursiveDirDiscoveryRegistry(PkgResourcesDirDiscoveryRegistry):

    """Discover files in paths."""

    def register(self, path):
        """Register path."""
        prefix, filename = path.rsplit(os.path.sep, 1)
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    subpath = os.path.join(root, f)
                    subfile = os.path.join(filename, f)
                    super(RecursiveDirDiscoveryRegistry, self).register(
                        (subfile, subpath)
                    )
        else:
            return super(RecursiveDirDiscoveryRegistry, self).register(
                (filename, path)
            )

json_schemas = RegistryProxy(
    'jsonschemas',
    RecursiveDirDiscoveryRegistry,
    'jsonschemas'
)


json_schemas_mapping = LocalProxy(lambda: dict(json_schemas))
"""Return dict of schema files that are registered and their filepath.

This does NOT include virtual/generated files, so it might not be
use to list all available schemas.
"""
