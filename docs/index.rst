.. Slicer Package Manager documentation master file, created by
   sphinx-quickstart on Mon Feb 12 16:59:31 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Slicer Package Manager's documentation!
====================================================

The **Slicer Package Manager** is a Girder plugin that allows you to manage Slicer package and extension within Girder.
It provides a simple API to Upload and Download extensions or packages, create new applications,
and manage releases of your applications.

What is Girder?
---------------

Girder is a free and open source web-based **data management platform** developed by Kitware_.
What does that mean? Girder is both a standalone application and a platform for building new web services.
To know more about Girder let's take a look at the documentation_.

.. _documentation: http://girder.readthedocs.io

.. _Kitware: https://www.kitware.com

What is a Slicer Extension?
---------------------------

An extension could be seen as a delivery package bundling together one or more Slicer modules.
After installing an extension, the associated modules will be presented to the user as built-in ones
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
   server
   python_client

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
