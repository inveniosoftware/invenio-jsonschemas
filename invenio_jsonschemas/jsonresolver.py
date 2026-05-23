# SPDX-FileCopyrightText: 2015-2018 CERN.
# SPDX-License-Identifier: MIT

"""JSON resolver for JSON schemas."""

from __future__ import absolute_import, print_function

import jsonresolver
from werkzeug.routing import Rule


@jsonresolver.hookimpl
def jsonresolver_loader(url_map):
    """JSON resolver plugin that loads the schema endpoint.

    Injected into Invenio-Records JSON resolver.
    """
    from flask import current_app

    from . import current_jsonschemas

    url_map.add(
        Rule(
            "{0}/<path:path>".format(current_app.config["JSONSCHEMAS_ENDPOINT"]),
            endpoint=current_jsonschemas.get_schema,
            host=current_app.config["JSONSCHEMAS_HOST"],
        )
    )
