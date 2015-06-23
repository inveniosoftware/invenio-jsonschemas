# This file is part of Invenio-JSONSchemas.
# Copyright (C) 2015 CERN.
#
# Invenio-JSONSchemas is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio-JSONSchemas is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio-JSONSchemas; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

# based on the right Invenio base image
FROM invenio:latest

# get root rights again
USER root

# add content
ADD . /code-module
WORKDIR /code-module

# install additional dependencies
RUN pip install -e .

# install sample package
RUN pip install -e ./examples/samplepkg

# step back
# in general code should not be writeable, especially because we are using
# `pip install -e`
RUN mkdir -p /code-module/src && \
    chown -R invenio:invenio /code-module && \
    chown -R root:root /code-module/invenio_jsonschemas && \
    chown -R root:root /code-module/setup.* && \
    chown -R root:root /code-module/src

# add volumes
# do this AFTER `chown`, because otherwise directory permissions are not
# preserved
VOLUME /code-module

# add module config
ENV INVENIO_ADD_CONFIG "$INVENIO_ADD_CONFIG /code-module/examples/example_config.txt"

# finally step back again
USER invenio

