..
    This file is part of Invenio.
    Copyright (C) 2015-2018 CERN.
    Copyright (C) 2024 Graz University of Technology.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Changes
=======

Version 2.0.0 (release 2024-12-05)

- setup: bump major dependencies

Version 1.1.5 (release 2024-11-30)

- fix: SphinxWarning
- global: remove examples directory
- global: remove six usage
- setup: change to reusable workflows
- setup: pin dependencies
- fix extlinks warning of compatibility with version 6
- global: clean test infrastructure
- increase minimal python version to 3.7
- move check_manifest configuration to setup.cfg.
- fix docs compatibilty problem with Sphinx>=5.0.0
- add .git-blame-ignore-revs
- migrate to use black as opinionated auto formater
- migrate setup.py to setup.cfg

Version 1.1.4 (released 2022-02-28)

- Changes from pkg_resources to importlib for entry points iteration.

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
