# SPDX-FileCopyrightText: 2017-2018 CERN.
# SPDX-License-Identifier: MIT

"""Helper proxy to the state object."""

from __future__ import absolute_import, print_function

from flask import current_app
from werkzeug.local import LocalProxy

current_jsonschemas = LocalProxy(lambda: current_app.extensions["invenio-jsonschemas"])
"""Helper proxy to access state object."""

current_refresolver_store = LocalProxy(
    lambda: current_app.extensions["invenio-jsonschemas"].refresolver_store()
)
"""Current JSONSchema ref resolver store."""
