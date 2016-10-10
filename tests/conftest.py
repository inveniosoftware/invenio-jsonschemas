# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
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


"""Pytest configuration."""

from __future__ import absolute_import, print_function

import os
import shutil
import sys
import tempfile
from contextlib import contextmanager

import pytest
from flask import Flask
from mock import patch
from pkg_resources import EntryPoint


@pytest.fixture()
def app():
    """Flask application fixture."""
    app = Flask('testapp')
    app.config.update(
        JSONSCHEMAS_LOADER_CLS='helpers:LOADER_CLS',
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
            raise Exception('Path {} cannot be absolute'.format(path))
        dir_path = os.path.join(root_dir_path, os.path.dirname(path))
        file_path = os.path.join(root_dir_path, path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        elif os.path.isfile(file_path):
            raise Exception('Path {} is a directory'.format(file_path))
        with open(file_path, 'w') as f:
            f.write(content)


@pytest.fixture()
def dir_factory(tmpdir_factory):
    """Provide a contextmanager enabling the creation of temporary directories.
    """
    @contextmanager
    def dir_builder(files):
        root_dir_path = str(tmpdir_factory.mktemp('test', numbered=True))
        create_file_hierarchy(root_dir_path, files)
        try:
            yield os.path.abspath(root_dir_path)
        finally:
            shutil.rmtree(root_dir_path)

    return dir_builder


@pytest.yield_fixture
def pkg_factory(tmpdir_factory):
    """Provide a contextmanager enabling the creation of temporary modules.
    """
    modules_path = str(tmpdir_factory.mktemp('test_modules', numbered=True))

    @contextmanager
    def pkg_builder(files):
        mod_path = tempfile.mkdtemp(dir=modules_path)
        create_file_hierarchy(mod_path, files)
        # create __init__.py file
        with open(os.path.join(mod_path, '__init__.py'), 'a'):
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


class MockEntryPoint(EntryPoint):
    """Mocking of entrypoint."""

    def load(self):
        """Mock load entry point."""
        return __import__(self.module_name)


@pytest.yield_fixture
def mock_entry_points():
    entry_points = dict()

    class EntryPointBuilder(object):
        """Manipulate mock Entrypoints."""
        def add(self, group, name, module_name):
            """Register additional entrypoints."""
            group_entry_points = entry_points.setdefault(group, [])
            # entrypoint = EntryPoint.parse(
            #     '{name}={module}'.format(name=name, module=module_name)
            # )
            group_entry_points.append(MockEntryPoint(name, module_name))
            # group_entry_points.append(entrypoint)

    def mock_entry_points(group):
        groups = entry_points.keys() if group is None else [group]
        for key in groups:
            for entry_point in entry_points[key]:
                yield entry_point

    with patch('pkg_resources.iter_entry_points', mock_entry_points):
        yield EntryPointBuilder()
