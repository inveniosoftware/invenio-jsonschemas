# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
            "Schema {schema} not found".format(schema=schema), *args, **kwargs
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
            "Schema {schema} defined in multiple ".format(schema=schema)
            + "directories: {first} and {second}".format(
                first=first_dir, second=second_dir
            ),
            *args,
            **kwargs
        )
