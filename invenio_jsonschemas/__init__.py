# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016, 2017 CERN.
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

"""Invenio module for building and serving JSONSchemas.

Note on storing absolute URLs
-----------------------------
As discussed in this issue_, it is not recommended to store and expose
absolute URLs in the `$ref`, as they can change in the future. One should
instead try to use DOI/EPIC or other kind of identifiers with the certitude
that they will never change, to avoid broken references.

.. _issue: https://github.com/inveniosoftware/invenio-jsonschemas/issues/23
"""

from __future__ import absolute_import, print_function

from .ext import InvenioJSONSchemas
from .proxies import current_jsonschemas
from .version import __version__

__all__ = ('__version__', 'InvenioJSONSchemas', 'current_jsonschemas')
