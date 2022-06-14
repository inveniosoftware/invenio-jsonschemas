# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Sample Package for Testing Invenio-JSONSchemas."""

from setuptools import setup

setup(
    name="samplepkg-invenio-jsonschemas",
    version="0.0.0",
    zip_safe=False,
    include_package_data=True,
    packages=["samplepkg"],
    entry_points={
        "invenio_jsonschemas.schemas": ["samplepkg = samplepkg.jsonschemas"],
    },
)
