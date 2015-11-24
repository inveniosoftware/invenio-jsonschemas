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

"""Invenio-JSONSchemas errors."""

from __future__ import absolute_import, print_function


class JSONSchemaError(Exception):
    """Base class for errors in Invenio-JSONSchemas module."""


class JSONSchemaNotFound(JSONSchemaError):
    """Exception raised when a requested JSONSchema is not found."""

    def __init__(self, schema, *args, **kwargs):
        """Constructor.

        :param schema: path of the requested schema which was not found.
        """
        self.schema = schema
        super(JSONSchemaNotFound, self).__init__(
            'Schema "{}" not found'.format(schema), *args, **kwargs
        )


class JSONSchemaDuplicate(JSONSchemaError):
    """Exception raised when multiple schemas match the same path."""

    def __init__(self, schema, first_dir, second_dir, *args, **kwargs):
        """Constructor.

        :param schema: duplicate schema path.
        :param first_dir: first directory where the schema was found.
        :param second_dir: second directory where the schema was found.
        """
        self.schema = schema
        super(JSONSchemaDuplicate, self).__init__(
            'Schema "{schema}" defined in multiple ' +
            'directories: "{first}" and "{second}"'.format(
                schema=schema,
                first=first_dir,
                second=second_dir),
            *args, **kwargs)
