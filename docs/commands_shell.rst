.. _commands_shell:

==============
Commands shell
==============

Installation
------------

To install the latest version of the ``slicer_extension_manager_client``::

    $ cd web_python_client

then::

    $ pip install .

or::

    $ pip install -e .

for development

Use
---

There are few solutions to authenticate on your Girder instance when using the client:

* Using your login and your password::

    $ slicer_extension_manager_client --username admin --password adminadmin

* Generating an API-KEY see the documentation_ for more details::

    $ slicer_extension_manager_client --api-key EKTb15LjqD4Q7jJuAVPuUSuW8N7s3dmuAekpRGLD

or by using the ``GIRDER_API_KEY`` environment variable::

    $ export GIRDER_API_KEY=EKTb15LjqD4Q7jJuAVPuUSuW8N7s3dmuAekpRGLD

.. warning::
    *The API-KEY is given as an example, follow the documentation on* api-key_ *to create one.*

Then you can start using the API that allow you to easily create applications, manage releases,
upload and download extensions, see :ref:`slicer_extension_manager_client` documentation for more details.

.. note::
    Once you've created an API-KEY, you can easily create an alias with both the ``slicer_extension_manager_client``
    command and the API-KEY to use the client more efficiency.

.. _api-key: http://girder.readthedocs.io/en/latest/user-guide.html#api-keys
.. _documentation: http://girder.readthedocs.io/en/latest/user-guide.html#api-keys

.. _slicer_extension_manager_client:

Slicer Extension Manager Client
-------------------------------

The command ``slicer_extension_manager_client`` allows to use a simplified API to interact with the Python Client API.
There are 3 different commands that can be used to manage models:

* Application
* Release
* Extension

To use this client you will need to authenticate with an admin user on the Girder instance.
Let's read the :doc:`commands_shell` documentation first.

Application
-----------

Use ``slicer_extension_manager_client app`` to manage applications, this command allow to create, list and delete them


Create & Initialized a new application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    slicer_extension_manager_client app create NAME [OPTIONS]

Arguments:

* ``NAME`` - The name of the new application

Options:

* ``--desc`` - The description of the new application

List all the application in the default collection 'Applications'
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    slicer_extension_manager_client app list


Delete an application
^^^^^^^^^^^^^^^^^^^^^

::

    slicer_extension_manager_client app delete NAME

Arguments:

* ``NAME`` - The name of the application which will be deleted


Release
-------

Use ``slicer_extension_manager_client release`` to manage releases: create, list and delete them.

Create a new release
^^^^^^^^^^^^^^^^^^^^

::

    slicer_extension_manager_client release create APP_NAME [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application

Options:

* ``--name`` - The name of the new release
* ``--revision`` - The revision of the application corresponding to this release
* ``--desc`` - The description of the new application

List all the release from an application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    slicer_extension_manager_client release list APP_NAME

Arguments:

* ``APP_NAME`` - The name of the application


Delete a release
^^^^^^^^^^^^^^^^

::

    slicer_extension_manager_client release delete APP_NAME NAME

Arguments:

* ``APP_NAME`` - The name of the application
* ``NAME`` - The name of the release which will be deleted

Extension
---------

Use ``slicer_extension_manager_client extension`` to upload, download or just list extensions

Upload a new extension
^^^^^^^^^^^^^^^^^^^^^^

Give the ``FILE_PATH`` argument to be able to upload an extension. The extension will then automatically
be added to the release which has the same revision than the ``--app_revision`` value. If any release correspond to the
given revision, the extension will be uploaded in the `Nightly` folder, by default.

The final name of the extension will depend of the ``extensionNameTemplate`` set as metadata on the application folder.
The default name is ``{app_revision}_{os}_{arch}_{baseName}_{revision}``. It can be change at any time on the
application setting page.

::

    slicer_extension_manager_client extension upload APP_NAME FILE_PATH [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application
* ``FILE_PATH`` - The path to the extension file to upload

Options:

* ``--os`` - The target operating system of the package
* ``--arch`` - Architecture that is supported by the extension
* ``--name`` - The basename of the new extension
* ``--repo_type`` - The repository type of the extension
* ``--repo_url`` - The repository URL of the extension
* ``--revision`` - The revision of the extension
* ``--app_revision`` - The revision of the application corresponding to this release
* ``--packagetype`` - Type of the package (Installer, data...)
* ``--codebase`` - The codebase baseName
* ``--desc`` - The description of the new application

List extensions
^^^^^^^^^^^^^^^

Use options to filter the listed extensions. By default, the command will list all the extension from the
'Nightly' release. It is possible to use the ``--release`` option to list the extension from a particular release.
Or use the flag ``--all`` to list all the extension present in the application. It is also possible to get only
one extension by providing the ``--fullname`` option of an extension.

::

    slicer_extension_manager_client extension list APP_NAME [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application

Options:

* ``--os`` - The target operating system of the package
* ``--arch`` - Architecture that is supported by the extension
* ``--app_revision`` - The revision of the application
* ``--release`` - The release within list all the extension
* ``--limit`` - Limit on the number of listed extension
* ``--all`` - Flag to list all the extension from all the release
* ``--fullname`` - Fullname of an extension


Download an extension
^^^^^^^^^^^^^^^^^^^^^

::

    slicer_extension_manager_client extension download APP_NAME ID_OR_NAME [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application
* ``ID_OR_NAME`` - The ID or name of the extension which will be downloaded

Options:

* ``--dir_path`` - Path where will be save the extension after the download


Delete an extension
^^^^^^^^^^^^^^^^^^^

Provide either the ID or the name of the extension to delete it.

::

    slicer_extension_manager_client extension delete APP_NAME ID_OR_NAME

Arguments:

* ``APP_NAME`` - The name of the application
* ``ID_OR_NAME`` - The ID or name of the extension which will be deleted

