# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio JSONSchemas utils."""

from __future__ import absolute_import, print_function

from copy import deepcopy


def resolve_schema(schema):
    """Transform JSON schemas "allOf".

    This is the default schema resolver.

    This function was created because some javascript JSON Schema libraries
    don't support "allOf". We recommend to use this function only in this
    specific case.

    This function is transforming the JSON Schema by removing "allOf" keywords.
    It recursively merges the sub-schemas as dictionaries. The process is
    completely custom and works only for simple JSON Schemas which use basic
    types (object, string, number, ...). Optional structures like "schema
    dependencies" or "oneOf" keywords are not supported.

    :param dict schema: the schema to resolve.
    :returns: the resolved schema

    .. note::

        The schema should have the ``$ref`` already resolved before running
        this method.
    """
    def traverse(schema):
        if isinstance(schema, dict):
            if 'allOf' in schema:
                for x in schema.pop('allOf'):
                    sub_schema = x
                    sub_schema.pop('title', None)
                    schema = _merge_dicts(schema, sub_schema)
                schema = traverse(schema)
            elif 'properties' in schema:
                for x in schema.get('properties', []):
                    schema['properties'][x] = traverse(
                        schema['properties'][x])
            elif 'items' in schema:
                schema['items'] = traverse(schema['items'])
        return schema
    return traverse(schema)


def _merge_dicts(first, second):
    """Merge the 'second' multiple-dictionary into the 'first' one."""
    new = deepcopy(first)
    for k, v in second.items():
        if isinstance(v, dict) and v:
            ret = _merge_dicts(new.get(k, dict()), v)
            new[k] = ret
        else:
            new[k] = second[k]
    return new
