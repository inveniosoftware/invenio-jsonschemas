..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 1.1.3 (released 2021-06-17)

- Fix string interpolation on error messages.

Version 1.1.2 (released 2021-04-06)

- Adds method to build a ref resolver store from the registry with a local
  URI scheme (e.g. local://).

Version 1.1.1 (released 2020-12-09)

- Migrates CI to GitHub actions.
- Fixes issue related to nested `allOf` being ignored, and added tests for it.

Version 1.1.0 (released 2020-03-12)

- Removes support for Python 2.7
- Changes Flask dependency to centrally managed by invenio-base

Version 1.0.1 (released 2019-09-04)

- Adds config ``JSONSCHEMAS_SCHEMAS`` to whitelist entrypoint names

Version 1.0.0 (released 2018-03-23)

- Initial public release.
