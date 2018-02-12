.. _installation:

============
Installation
============

Install from source
-------------------

To install from the latest source, first obtain the source code

* Using HTTPS::

    $ git clone https://github.com/girder/slicer_extension_manager.git

* Or using SSH::

    $ git clone git@github.com:girder/slicer_extension_manager.git

Then::

    $ cd slicer_extension_manager

Run via Docker
--------------

If you do not have all required system packages installed let's read the :doc:`prerequisites`.

Then to build and start the `Girder` and `mongo` containers::

    $ docker-compose up -d

The application should then be running at http://localhost:8080/ and be already configured:

* Creation of an **Admin user** (*username: admin*, *password: adminadmin*)
* Creation of an **Assetstore** (*/slicer_extension_manager/assetstore*)
