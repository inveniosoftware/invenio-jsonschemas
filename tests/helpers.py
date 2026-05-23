# SPDX-FileCopyrightText: 2016-2018 CERN.
# SPDX-License-Identifier: MIT

"""Test helpers."""

from jsonresolver import JSONResolver
from jsonresolver.contrib.jsonref import json_loader_factory

LOADER_CLS = json_loader_factory(
    JSONResolver(plugins=["invenio_jsonschemas.jsonresolver"])
)
"""Test loader class."""
