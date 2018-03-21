
Slicer Package Manager |CircleCI| |Documentation|
===================================================

External plugin of Girder that allow the management of Slicer packages and extensions
(before handled by the data management platform Midas).

The Slicer Package Manager include a CLI allowing you
to manage Slicer packages for Slicer-based applications and associated extensions.

If you need to learn more about the Slicer Package Manager, the documentation is available at
http://slicer-package-manager.readthedocs.io/en/latest/.

And to have a better idea of how is structured the Slicer package manager plugin within Girder, here is a diagram::

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

.. |CircleCI| image:: https://circleci.com/gh/girder/slicer_package_manager.svg?style=svg
    :target: https://circleci.com/gh/girder/slicer_package_manager
    :alt: Build Status

.. |Documentation| image:: https://readthedocs.org/projects/slicer-package-manager/badge/?version=latest
    :target: http://slicer-package-manager.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
