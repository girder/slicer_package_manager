.. _installation:

==========
Deployment
==========

The section below describes a convenient way to setup a server for evaluation purpose.

For production deployment, read more details in the ``Administrator Documentation`` section
at https://girder.readthedocs.io.

Run via Docker
--------------

First, install Docker and Docker compose follow the instruction on the official website.
The community edition (CE) is sufficient for using this plugin. See https://docs.docker.com/install/
and https://docs.docker.com/compose/install/.

Then, assuming the sources are available in ``slicer_package_manager`` folder, you may run
the server running the following commands::

    $ cd slicer_package_manager
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
