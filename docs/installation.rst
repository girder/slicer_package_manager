.. _installation:

============
Installation
============

Install from source
-------------------

To install from the latest source, first obtain the source code

* Using HTTPS::

    $ git clone https://github.com/girder/slicer_package_manager.git

* Or using SSH::

    $ git clone git@github.com:girder/slicer_package_manager.git

Then::

    $ cd slicer_package_manager

Run via Docker
--------------

If you do not have all required system packages installed let's read the :doc:`prerequisites`.

Then to run the server just use the following command::

    $ docker-compose up -d

.. note::

    The ``-d`` option is running the container in deamon mode. Remove it to display the logs
    on the running containers.

    To rebuild the container after changing the source code use the ``--build`` option when
    you run the command.

.. warning::

    *Run the containers can take few moments, the application will not be ready instantly.*

The Girder application should then be running at http://localhost:8080/ and be already setup:

* Creation of an **Admin User** (username: *admin*, password: *adminadmin*)
* Creation of a local **Assetstore** (in *~/slicer_package_manager/assetstore*),
  let's read the Filesystem_ documentation for more detail about it

.. note::

    You will have the possibility to create more users and/or change the password of
    the **Admin User** via the Girder UI.

.. _Filesystem: https://girder.readthedocs.io/en/latest/user-guide.html#assetstores
