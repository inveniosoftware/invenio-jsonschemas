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

from __future__ import print_function, unicode_literals


class TestUtils:
    def test_urljoin(self):
        from invenio_jsonschemas.utils import urljoin

        assert urljoin('http://test.org') == 'http://test.org', 'touches normal URL'

        assert urljoin('http://test.org', 'foo') == 'http://test.org/foo', 'cannot do a simple append'

        assert urljoin('http://test.org', 'foo/') == 'http://test.org/foo/', 'does not respect trailing slash'

        assert urljoin('http://test.org/', 'foo') == 'http://test.org/foo', 'does not handle trailing slash in first component correctly'

        assert urljoin('http://test.org', '/foo') == 'http://test.org/foo', 'does not handle leading slash in second component correctly'

        assert urljoin('http://test.org/', '/foo') == 'http://test.org/foo', 'does not handle trailing + leading slash correctly'

        assert urljoin('http://test.org/', 'foo', 'bar') == 'http://test.org/foo/bar', 'does not handle 3 components'

        assert urljoin('http://test.org/', 'foo', 'bar', 'x', 'y', 'z') == 'http://test.org/foo/bar/x/y/z', 'does not handle 6 components'

        assert urljoin() == '', 'does not handle zero components'

        assert urljoin('http://test.org/', '/foo?p=1') == 'http://test.org/foo?p=1', 'does not handle query parameters correctly'

        assert urljoin('http://test.org/', '/foo#bar') == 'http://test.org/foo#bar', 'does not handle fragments correctly'

    def test_splitpath(self):
        from invenio_jsonschemas.utils import split_path

        assert split_path('foo/bars') == ['foo', 'bars'], 'does not handle simple case'
        assert split_path('foo') == ['foo'], 'does not handle 1-part case'
        assert split_path('x/y/zz') == ['x', 'y', 'zz'], 'does not handle 3-part case'
        assert split_path('x/x/x') == ['x', 'x', 'x'], 'does not handle case with repititions'
        assert split_path('') == [], 'does not output empty array for empty string'
        assert split_path(' foo / bar / foo ') == [' foo ', ' bar ', ' foo '], 'seems to alter whitespaces'
        assert split_path('x/' * 10000 + 'x') == ['x'] * 10001, 'has problems with very long strings'

    def test_treeinsert(self):
        from invenio_jsonschemas.utils import tree_insert

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
        path1 = ['src', 'lib', 'xx']
        tree_insert(tree, path1, element1)
        assert tree == {
            '.': ['README.md', 'LICENSE'],
            'src': {
                '.': ['Makefile'],
                'lib': {
                    'xx': {
                        '.': ['foo.c', 'bar.c']
                    }
                }
            },
            'doc': {
                '.': ['changelog.md']
            }
        }, 'does not append to existing dir correctly'


        element2 = 'hello.c'
        path2 = ['src', 'cmd', 'manage']
        tree_insert(tree, path2, element2)
        assert tree == {
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
        }, 'does not create new path correctly'

    def test_treesort(self):
        from collections import OrderedDict
        from invenio_jsonschemas.utils import tree_sort

        tree1 = {
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

        otree1 = tree_sort(tree1)

        assert otree1 == OrderedDict([
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
        ]), 'does not sort tree correctly'


        tree2 = {
            '.': [
                {'name': 'README.md', 'id': 1},
                'LICENSE',
                {'attr': 0x22, 'size': 1.222, 'name': 'a'}
            ],
        }

        otree2 = tree_sort(tree2)

        assert otree2 == OrderedDict([
            ('.', [
                {'attr': 0x22, 'size': 1.222, 'name': 'a'},
                'LICENSE',
                {'name': 'README.md', 'id': 1}
            ])
        ]), 'does not handle dict+`name` instead of strings'
