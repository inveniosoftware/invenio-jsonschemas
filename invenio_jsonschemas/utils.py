# -*- coding: utf-8 -*-
#
# This file is part of Invenio-JSONSchemas.
# Copyright (C) 2015 CERN.
#
# Invenio-JSONSchemas is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio-JSONSchemas is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio-JSONSchemas; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""Different utils for JSON handling."""

import os
import os.path
import urlparse

from collections import OrderedDict


def urljoin(*args):
    """Join parts of a URL together, similar to `os.path.join`."""
    def _add_trailing_slash(s):
        if s.endswith('/'):
            return s
        else:
            return s + '/'

    if len(args) > 1:
        result = reduce(urlparse.urljoin, map(_add_trailing_slash, args[:-1]))
    else:
        result = ''

    if args:
        result = urlparse.urljoin(
            result,
            args[-1]
        )

    return result


def split_path(string):
    """Split path string into an array.

    The result depends on `os.path.split`.
    """
    result = []
    while string:
        head, tail = os.path.split(string)
        result.insert(0, tail)
        string = head
    return result


def tree_insert(tree, path, element):
    """Add element into a dict tree.

    After finding and creating the path and node that is the target of
    this operation, the element will be inserted into a list that is
    located in the `'.'` subkey. Example:

    .. code:: python

        tree = {
            '.': ['README.md', 'LICENSE'],
            'src': {
                '.': ['Makefile'],
                'lib': {
                    'xx': {
                        '.': ['foo.c']
                    }
                }
            },
            'doc': {
                '.': ['changelog.md']
            }
        }
        element1 = 'bar.c'
        element2 = 'hello.c'
        path1 = ['src', 'lib', 'xx']
        path2 = ['src', 'cmd', 'manage']
        tree_insert(tree, path1, element1)
        tree_insert(tree, path2, element2)

        tree == {
            '.': ['README.md', 'LICENSE'],
            'src': {
                '.': ['Makefile'],
                'lib': {
                    'xx': {
                        '.': ['foo.c', 'bar.c']
                    }
                },
                'cmd': {
                    'manage': {
                        '.': ['hello.c']
                    }
                }
            },
            'doc': {
                '.': ['changelog.md']
            }
        }

    Note that dicts in python are not ordered.

    :param tree: the root of the dict tree
    :param path: a list representing the path in the tree
    :param element: element that should be inserted.
    """
    if path:
        current = path.pop(0)
        if current not in tree:
            tree[current] = dict()
        tree_insert(tree[current], path, element)
    else:
        if '.' not in tree:
            tree['.'] = list()
        tree['.'].append(element)


def tree_sort(tree):
    """Sort dict tree and the list in `'.'` nodes.

    Dicts will be converted into `OrderedDict`. `'.'` will be before all
    other nodes. The comparison is done on lowercase strings.

    Example:

    .. code:: python

        tree = {
            '.': ['README.md', 'LICENSE'],
            'src': {
                '.': ['Makefile'],
                'lib': {
                    'xx': {
                        '.': ['foo.c', 'bar.c']
                    }
                },
                'cmd': {
                    'manage': {
                        '.': ['hello.c']
                    }
                }
            },
            'doc': {
                '.': ['changelog.md']
            }
        }

        otree = tree_sort(tree)

        otree == OrderedDict([
            ('.', ['LICENSE', 'README.md']),
            ('doc', OrderedDict([
                ('.', ['changelog.md'])
            ])),
            ('src', OrderedDict([
                ('.', ['Makefile']),
                ('cmd', OrderedDict([
                    ('manage', OrderedDict([
                        ('.', ['hello.c'])
                    ]))
                ])),
                ('lib', OrderedDict([
                    ('xx', OrderedDict([
                        ('.', ['bar.c', 'foo.c'])
                    ]))
                ]))
            ]))
        ])

    .. note::
        if the entries of the lists are dicts and contains a `name` attribute,
        the value for that key will be used for sorting.
    """
    result = OrderedDict()
    if '.' in tree:
        sub = tree.pop('.')
        result['.'] = list(sorted(
            sub,
            key=lambda e: e['name'].lower()
            if 'name' in e
            else (e.lower() if isinstance(e, basestring) else e)
        ))
    for k in sorted(tree.iterkeys()):
        result[k] = tree_sort(tree[k])
    return result
