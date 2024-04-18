=============
Release Notes
=============

This is the list of **Slicer Package Manager** changes between each release. For full
details, see the commit logs at https://github.com/girder/slicer_package_manager

Next Release
============

Bug fixes
---------

* Prevent incompatibility pinning version of `girder`, `girder-hashsum-download`,
  `girder_client` and `pytest-girder` to be `>=3.1.20` and `<3.2`.

Tests
-----

* Improve PackageMetadataChecksumUpdate tests to check extensions package.

Internal
--------

* Fix documentation build adding `.readthedocs.yml`

* Switch server plugin Python wheel build-system to `pyproject.toml`.

* Require Python ``>= 3.8`` for the server and update Girder test Docker to use image
  `girder/girder_test:py38-node14 <https://hub.docker.com/r/girder/girder_test/tags>`_ built
  from `girder/.circleci/Dockerfile <https://github.com/girder/girder/blob/v3.2.3/.circleci/Dockerfile>`_.


0.8.0
=====

New Features
------------

Server
^^^^^^

* Associate application & extension package item with checksum.

   * After uploading an application or extension package, the item metadata will include `sha512` metadata entry.

   * After uploading additional files, the item metadata remains unchanged.

   * After removing the second to last files, the `sha512` item metadata is updated to match the checksum of the
     last file.

   * After removing all the files, the `sha512` item metadata is set to an empty string.

Documentation
-------------

* Remove obsolete ``cleanNightly.sh`` script and update faq.

* Update developer installation instructions to use Girder 3.x commands.

Bug fixes
---------

Python Client
^^^^^^^^^^^^^

* Fix python client test requirements adding "pytest" and "pytest-girder".

* Attempting to install the python client using Python ``< 3.7`` will now report an error message.

Server
^^^^^^

* Update extension & package delete endpoints

  * Explicitly check that user can access the associated application folder.

  * Return a confirmation message.

Internal
--------

* Require Python ``>= 3.6`` for the server. This is consistent with the version associated with the Girder test Docker
  image `girder/girder_test:latest <https://hub.docker.com/r/girder/girder_test/tags>`_ built
  from `girder/.circleci/Dockerfile <https://github.com/girder/girder/blob/d994d93a00257a17eeeab7e0b6fa4a54f5658550/.circleci/Dockerfile>`_.

* The required version previously set to "3.7" in version "0.7.0" for both client and server but it
  was not enforced due to an incorrect setup parameter. It should have been specified as ``python_requires``
  instead of ``python_require`` (as defined in PEP 440).

* Re-factor and simplify code based on the newly introduced pre-commit hooks and ruff checks (``codespell``, ``pyupgrade`` and ``ruff``).

* Add type annotations to python client CLI.

Tests
-----

* Add GitHub Actions workflow to run `pre-commit <https://github.com/pre-commit/pre-commit-hooks#hooks-available>`_ hooks.

  * Add "codespell" pre-commit hook and fix typos.

  * Add `pyupgrade <https://github.com/asottile/pyupgrade>`_ pre-commit hook specifying "--py36-plus"
    and updates codes accordingly.

  * Add `ruff <https://beta.ruff.rs/docs/usage/#pre-commit>`_ pre-commit hook enabling the following checks:
    ::

      "A",           # flake8-builtins
      "ARG",         # flake8-unused-arguments
      "B",           # flake8-bugbear
      "BLE",         # flake8-blind-except
      "C4",          # flake8-comprehensions
      "COM",         # flake8-commas
      "D",           # pydocstyle (aka flake8-docstrings)
      "E", "F", "W", # flake8
      "EXE",         # flake8-executable
      "EM",          # flake8-errmsg
      "G",           # flake8-logging-format
      "ICN",         # flake8-import-conventions
      "ISC",         # flake8-implicit-str-concat
      "N",           # pep8-naming
      "PIE",         # flake8-pie
      "PGH",         # pygrep-hooks
      "PL",          # pylint
      "PT",          # flake8-pytest-style
      "Q",           # flake8-quotes
      "RSE",         # flake8-raise
      "RUF",         # Ruff-specific
      "S",           # flake8-bandit
      "SIM",         # flake8-simplify
      "SLF",         # flake8-self
      "YTT",         # flake8-2020


0.7.1
=====

Bug fixes
---------

Python Client
^^^^^^^^^^^^^

* Fix wheel ensuring ``_vendor.bson`` package is distributed.


0.7.0
=====

Documentation
-------------

* Re-organize and simplify documentation.

Internal
--------

* Require Python >= 3.7 for both python client and server.

* Update development status to ``Production/Stable``.

* Vendorize ``bson.objectid`` from PyMongo to support installing the client alongside the server
  and workaround incompatibilities between standalone ``bson`` package and the one provided by PyMongo.

Python Client
^^^^^^^^^^^^^

* Support publishing python client sdist and wheel named ``slicer-package-manager-client``.

0.6.0
=====

New Features
------------

* Support listing extension with a ``query`` parameter specifying the text expected
  to be found in the extension name or description.

Bug fixes
---------

Server
^^^^^^

* Fix creation of extension in private application.

* Ensure user or administrator errors associated with API endpoints are displayed and associated
  with HTTP error code 400 by raising a :exc:`RestException` instead of a generic :exc:`Exception`.

* Update API endpoint `GET /app/{app_id}/extension` to always check user credentials.

0.5.0
=====

New Features
------------

* Require version information to be specified when uploading application packages. See :issue:`97`.

* Add application package ``build_date`` metadata. User may specify a custom value formatted as a datetime string
  using the API endpoint or the python client. Default is set to current date and time.

Server
^^^^^^

* Automatically update ``release`` metadata when packages are moved (or copied) between draft and release folders.

* Add convenience functions :func:`slicer_package_manager.utilities.isApplicationFolder`,
  :func:`slicer_package_manager.utilities.isReleaseFolder` and :func:`slicer_package_manager.utilities.isDraftReleaseFolder`.

* Add :func:`slicer_package_manager.utilities.getReleaseFolder` and simplify update of ``downloadStats``
  release metadata to use the new function.

Bug fixes
---------

* Remove partially implemented ``codebase`` metadata.

* Remove support for unused ``packagetype`` metadata.

Tests
-----

* ExternalData:

  * Fix re-download of files if checksum does not match.

  * Re-factor fixture introducing ``downloadExternals``.


0.4.0
=====

New Features
------------

* Support querying application packages given a release name. See :issue:`96`.

Bug fixes
---------

Server
^^^^^^

* Ensure permissions are consistently checked in API endpoints implementation. See :issue:`95`.

* Fix support for unauthenticated use of public API endpoints. See :issue:`95`.


0.3.0
=====

Bug fixes
---------

Server
^^^^^^

* Update implementation of ``GET /app/:app_id/package`` endpoint to properly handle
  ``limit=0`` parameter. See :issue:`94`.

Documentation
-------------

* Add documentation to :func:`slicer_package_manager.utilities.getOrCreateReleaseFolder`.


0.2.0
=====

Bug fixes
---------

Server
^^^^^^

* Update access level of API endpoints. See :issue:`89`.

  * Creating or updating packages now always require credentials.

  * Retrieving list of applications, releases and packages are now public.
    Note that credentials are still required to retrieve data associated with private
    applications.

Python Client
^^^^^^^^^^^^^

* Fix handling of ``--public``, ``--all`` and ``--pre_release`` flags. See :issue:`85`.

* Update ``draft list`` command to support ``--limit`` argument. See :issue:`82`.

Documentation
-------------

* Add maintainer documentation along with :doc:`/make_a_release` section.

* Improve description of ``limit`` in :func:`slicer_package_manager_client.SlicerPackageClient.listExtension`
  and :func:`slicer_package_manager_client.SlicerPackageClient.listApplicationPackage`. See :issue:`84`.

Tests
-----

* Simplify and refactor python client tests to facilitate maintenance. See :issue:`83` and :issue:`88`.


0.1.0
=====

New Features
------------

* Transition server plugin from Girder 2.x to Girder 3.x. See :issue:`88`.


Initial version
===============

Developed by :user:`Pierre-Assemat` during his internship at Kitware in 2018.

Features
--------

* Girder plugin implementing REST API endpoints.

* CLI `slicer_package_manager_client`

* Python client class :class:`SlicerPackageClient`.

Documentation
-------------

* Administrator, user and developer documentation written in reStructuredText (RST),
  generated using sphinx and published at https://slicer-package-manager.readthedocs.io

Tests
-----

* Continuous integration (CI) configured to run on CircleCI.

* Girder plugin tests.

* CLI and Python client tests leveraging `pytest-vcr <https://pytest-vcr.readthedocs.io>`_.

Provisioning
------------

* Dockerfile and docker-compose files for provisioning a demo server.
