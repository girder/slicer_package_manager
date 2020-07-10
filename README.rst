======================
Slicer Package Manager
======================

|CircleCI| |Documentation|

.. |CircleCI| image:: https://circleci.com/gh/girder/slicer_package_manager.svg?style=svg
    :target: https://circleci.com/gh/girder/slicer_package_manager
    :alt: Build Status

.. |Documentation| image:: https://readthedocs.org/projects/slicer-package-manager/badge/?version=latest
    :target: https://slicer-package-manager.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

The ``Slicer Package Manager`` includes a REST API service and CLI built on `Girder`_ for downloading, uploading
and organizing application and extension packages for both `3D Slicer`_ and `3D Slicer-based`_ applications.

.. _Girder: https://github.com/girder/girder
.. _3D Slicer: https://slicer.org
.. _3D Slicer-based: https://github.com/KitwareMedical/SlicerCustomAppTemplate

Documentation is available at https://slicer-package-manager.readthedocs.io

In a nutshell:

* `Data model`_ specific to this project is implemented by organizing data using standard
  Girder constructs (collection, folder and item) and by associating metadata.

* By default, a top-level collection named ``Applications`` is created with a ``packages`` folder
  organizing the different application.

* Each application folder contain a ``draft`` folder where unreleased packages are uploaded and one or multiple
  release folders (e.g 1.0, 2.0, ...).

* Each release folder contain application packages (installers for the different platforms), and an ``extensions``
  folder containing a flat list of extension packages.

* Each extension packages is associated with metadata like application revision, extension revision, operating system
  and architecture.

.. _Data Model: https://slicer-package-manager.readthedocs.io/en/latest/user_guide.html#concepts

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
