# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2016-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test helpers."""

from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonref import json_loader_factory

LOADER_CLS = json_loader_factory(
    JSONResolver(plugins=["invenio_jsonschemas.jsonresolver"])
)
"""Test loader class."""
