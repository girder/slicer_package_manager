.. Slicer Package Manager documentation master file, created by
   sphinx-quickstart on Mon Feb 12 16:59:31 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Slicer Package Manager's documentation!
====================================================

The ``Slicer Package Manager`` includes a REST API service and CLI built on `Girder`_ for downloading, uploading
and organizing application and extension packages for both `3D Slicer`_ and `3D Slicer-based`_ applications.

.. _Girder: https://github.com/girder/girder
.. _3D Slicer: https://slicer.org
.. _3D Slicer-based: https://github.com/KitwareMedical/SlicerCustomAppTemplate

In a nutshell:

* :ref:`Data model <concepts>` specific to this project is implemented by organizing data using standard
  Girder constructs (collection, folder and item) and by associating metadata.

* By default, a top-level collection named ``Applications`` is created with a ``packages`` folder
  organizing the different application.

* Each application folder contain a ``draft`` folder where unreleased packages are uploaded and one or multiple
  release folders (e.g 1.0, 2.0, ...).

* Each release folder contain application packages (installers for the different platforms), and an ``extensions``
  folder containing a flat list of extension packages.

* Each extension packages is associated with metadata like application revision, extension revision, operating system
  and architecture...

The diagram below represents the organization::

    Applications
       |--- packages
       |        |----- Slicer
       |        |         |----- 1.0
       |        |         |        |---- Slicer-linux.tar.gz
       |        |         |        |---- Slicer-macos.dmg
       |        |         |        |---- Slicer-win.exe
       |        |         |        |---- extensions
       |        |         |        |         |---- Extension1
       |        |         |        |         |---- Extension2
       |        |         |        |         |---- Extension3
       |        |         |        |         |---- Extension4
       .        .         .        .         .
       .        .         .
       |        |         |----- 2.0
       .        .         .        |
       .        .         .
       |        |         |----- draft
       |        |         |        |--- r100
       |        |         |        |      |---- Slicer-linux.tar.gz
       |        |         |        |      |---- Slicer-macos.dmg
       |        |         |        |      |---- Slicer-win.exe
       |        |         |        |      |----- extensions
       |        |         |        |      |          |---- Extension1
       .        .         .        .      .          .
       .        .         .        .
       |        |         |        |--- r101
       .        .         .        .      |
       .        .
       |        |
       |        |------SlicerCustom


What is Girder?
---------------

Girder is a free and open source web-based **data management platform** developed by Kitware_.
What does that mean? Girder is both a standalone application and a platform for building new web services.
To know more about Girder let's take a look at the documentation_.

.. _documentation: https://girder.readthedocs.io

.. _Kitware: https://www.kitware.com

What is a Slicer package?
---------------------------
A slicer package is just an installer package for a specific release of Slicer. There is a specific Slicer package
for each different platform (Windows, MACOSX, Linux).

What is a Slicer Extension?
---------------------------

An extension could be seen as a delivery package bundling together one or more Slicer modules.
After installing an extension, the associated modules will be presented to the user as built-in ones.
To know more about Slicer extension let's take a look at the FAQ_.

.. _FAQ: https://www.slicer.org/wiki/Documentation/Nightly/FAQ/Extensions


Table of Contents
=================

.. toctree::
   :maxdepth: 2
   :caption: Administrator Documentation:

   prerequisites
   installation


.. toctree::
   :maxdepth: 2
   :caption: User Documentation:

   user_guide
   commands_shell
   authors

.. toctree::
   :maxdepth: 1
   :caption: Developer Documentation:

   developer_guide
   slicer_package_manager
   slicer_package_manager_client
   changes

.. toctree::
   :maxdepth: 1
   :caption: Maintainer Documentation:

   make_a_release

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Resources
=========

* Free software: Apache-2.0_
* Source code: https://github.com/girder/slicer_package_manager

.. _Apache-2.0: https://www.apache.org/licenses/LICENSE-2.0
