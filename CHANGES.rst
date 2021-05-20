=============
Release Notes
=============

This is the list of **Slicer Package Manager** changes between each release. For full
details, see the commit logs at https://github.com/girder/slicer_package_manager

Next Release
============

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
