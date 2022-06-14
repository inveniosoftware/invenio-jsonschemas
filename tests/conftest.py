# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015-2018 CERN.
# Copyright (C) 2022 RERO.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import sys
import tempfile
from contextlib import contextmanager

import pytest
from flask import Flask
from importlib_metadata import EntryPoint
from mock import patch
from werkzeug.utils import import_string


@pytest.fixture()
def app():
    """Flask application fixture."""
    app = Flask("testapp")
    app.config.update(
        JSONSCHEMAS_LOADER_CLS="helpers:LOADER_CLS",
        JSONSCHEMAS_REGISTER_ENDPOINTS_UI=True,
        TESTING=True,
    )
    return app


def create_file_hierarchy(root_dir_path, files):
    """Create a hierarchy of files in a directory.

    :param root_dir_path: directory in which all files will be created
    :param files: dict of <relative file path> -> <file content>
    """
    for path, content in files.items():
        if os.path.isabs(path):
            raise Exception("Path {} cannot be absolute".format(path))
        dir_path = os.path.join(root_dir_path, os.path.dirname(path))
        file_path = os.path.join(root_dir_path, path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        elif os.path.isfile(file_path):
            raise Exception("Path {} is a directory".format(file_path))
        with open(file_path, "w") as f:
            f.write(content)


@pytest.fixture()
def dir_factory(tmpdir_factory):
    """Context manager enabling the creation of temporary directories."""

    @contextmanager
    def dir_builder(files):
        root_dir_path = str(tmpdir_factory.mktemp("test", numbered=True))
        create_file_hierarchy(root_dir_path, files)
        try:
            yield os.path.abspath(root_dir_path)
        finally:
            shutil.rmtree(root_dir_path)

    return dir_builder


@pytest.yield_fixture
def pkg_factory(tmpdir_factory):
    """Context manager enabling the creation of temporary modules."""
    modules_path = str(tmpdir_factory.mktemp("test_modules", numbered=True))

    @contextmanager
    def pkg_builder(files):
        mod_path = tempfile.mkdtemp(dir=modules_path)
        create_file_hierarchy(mod_path, files)
        # create __init__.py file
        with open(os.path.join(mod_path, "__init__.py"), "a"):
            pass
        # return the module name
        try:
            yield os.path.split(mod_path)[1]
        finally:
            shutil.rmtree(mod_path)

    sys.path.append(modules_path)
    try:
        yield pkg_builder
    finally:
        sys.path.remove(modules_path)


# class MockEntryPoint(EntryPoint):
#     """Mocking of entrypoint."""

#     def load(self):
#         """Mock load entry point."""
#         if self.name == 'importfail':
#             raise ImportError()
#         else:
#             return import_string(self.name)


class MockEntryPoint(EntryPoint):
    """Mocking of entrypoint."""

    def load(self):
        """Mock load entry point."""
        return __import__(self.module)


@pytest.yield_fixture
def mock_entry_points():
    """Mock of the JSONSchemas entry points."""
    entry_points = {}

    class EntryPointBuilder(object):
        """Manipulate mock Entrypoints."""

        def add(self, group, name, module):
            """Register additional entrypoints."""
            entry_points[name] = [MockEntryPoint(name=name, value=module, group=group)]

    def fn(group=None):
        if group:
            entry_points_group = []
            for eps in entry_points.values():
                for ep in eps:
                    if ep.group == group:
                        entry_points_group.append(ep)
            return entry_points_group
        return entry_points

    with patch("importlib_metadata.entry_points", fn):
        yield EntryPointBuilder()
