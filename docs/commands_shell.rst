.. _commands_shell:

==============
Commands shell
==============

Installation
------------

To install the latest version of the ``slicer_package_manager_client``, from the
*slicer_package_manager* directory run::

    $ cd python_client

then::

    $ pip install .

or::

    $ pip install -e .

for development

Use
---

There are few solutions to authenticate on your Girder instance when using the client:

* Using your login and your password::

    $ slicer_package_manager_client --username admin --password adminadmin

* Generating an API-KEY see the documentation_ for more details::

    $ slicer_package_manager_client --api-key EKTb15LjqD4Q7jJuAVPuUSuW8N7s3dmuAekpRGLD

or by using the ``GIRDER_API_KEY`` environment variable::

    $ export GIRDER_API_KEY=EKTb15LjqD4Q7jJuAVPuUSuW8N7s3dmuAekpRGLD

.. warning::
    *The API-KEY is given as an example, follow the documentation on* api-key_ *to create your own.*

.. note::
    If you want to use the client to an external *Slicer package manager* instance, you will need
    to provide the API url by adding the option::

    --api-url http://192.168.100.110/api/v1

    (The IP is given as an example)

Then you can start using the API that allow you to easily create applications, manage releases,
upload and download packages, see :ref:`slicer_package_manager_client` documentation
for more details.

.. _api-key: https://girder.readthedocs.io/en/latest/user-guide.html#api-keys
.. _documentation: https://girder.readthedocs.io/en/latest/user-guide.html#api-keys

.. _slicer_package_manager_client:

Slicer Package Manager Client
-------------------------------

The command ``slicer_package_manager_client`` allows to use a simplified API to interact with
the Python Client API. There are 5 different commands that can be used to manage models:

* Application
* Release
* Draft
* Package
* Extension

To use this client you will need to authenticate with an admin user on the Girder instance.
Let's read the :doc:`commands_shell` documentation first.

.. note::

    To use the **Bash completion** feature you just have to run the following command each time
    you use a new terminal::

    $ eval "$(_SLICER_PACKAGE_MANAGER_CLIENT_COMPLETE=source slicer_package_manager_client)"

    Or you can add it on your ``.bashrc`` file to always have this feature available.

In each command, the optional parameter ``coll_id`` allow to use the Slicer Package Manager
Client within an existing collection and not in the default *Applications* collection.
When this is the case, to avoid repeating this parameter in each command it's also possible
to set an environment variable named ``COLLECTION_ID``.

Application
-----------

Use ``slicer_package_manager_client app`` to manage applications: create, list and delete them.


Create & Initialized a new application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can either choose an existing collection by providing ``coll_id`` or create a specific one
by providing ``coll_name``. If none of this optional parameters are provided, the default
collection *Application* will be got or created if it doesn't exist yet.
This function will also create a top level folder named *packages* organizing the different
application in the collection.

::

    slicer_package_manager_client app create NAME [OPTIONS]

Arguments:

* ``NAME`` - The name of the new application

Options:

* ``--desc`` - The description of the new application
* ``--coll_id`` - ID of an existing collection
* ``--coll_name`` - The name of the new collection
* ``--coll_desc`` - The description of the new collection
* ``--public`` - Whether the collection should be publicly visible

List all the application within a collection
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By providing ``coll_id``, you are able to list all the applications from a specific collection.
By default it will list the applications within the collection *Applications*.

::

    slicer_package_manager_client app list


Delete an application
^^^^^^^^^^^^^^^^^^^^^

::

    slicer_package_manager_client app delete NAME

Arguments:

* ``NAME`` - The name of the application which will be deleted
* ``--coll_id`` - ID of an existing collection


Release
-------

Use ``slicer_package_manager_client release`` to manage releases: create, list and delete them.

Create a new release
^^^^^^^^^^^^^^^^^^^^

::

    slicer_package_manager_client release create APP_NAME NAME REVISION [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application
* ``NAME`` - The name of the new release
* ``REVISION`` - The revision of the application corresponding to this release

Options:


* ``--coll_id`` - ID of an existing collection
* ``--desc`` - The description of the new application

List all the release from an application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    slicer_package_manager_client release list APP_NAME

Arguments:

* ``APP_NAME`` - The name of the application

Options:

* ``--coll_id`` - ID of an existing collection

Delete a release
^^^^^^^^^^^^^^^^

::

    slicer_package_manager_client release delete APP_NAME NAME

Arguments:

* ``APP_NAME`` - The name of the application
* ``NAME`` - The name of the release which will be deleted

Options:

* ``--coll_id`` - ID of an existing collection


Draft
-----

Use ``slicer_package_manager_client draft`` to list and delete draft releases.

List all the draft release within an application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Provide ``revision`` will list only one draft release corresponding to the revision store as
metadata. The ``--offset`` option allow to list only the older draft release.

::

    slicer_package_manager_client draft list APP_NAME [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application

Options:

* ``--revision`` - The revision of a draft release
* ``--offset`` - The offset to list only the older draft release
* ``--coll_id`` - ID of an existing collection

Delete a specific draft release
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

    slicer_package_manager_client draft delete APP_NAME REVISION [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application
* ``REVISION`` - The revision of the draft release

Options:

* ``--coll_id`` - ID of an existing collection


Package
-------

Use ``slicer_package_manager_client package`` to upload, download or just list application
packages.

Upload a new application package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Give the ``FILE_PATH`` argument to be able to upload an application package.
The application package will automatically be added to the release which has the same revision
than the ``--revision`` value. If any release correspond to the given revision,
the application package will be uploaded in the `draft` release, by default.

The final name of the application package will depend of the ``applicationPackageNameTemplate``
set as metadata on the application folder. The default name is
``{baseName}_{arch}_{os}_{revision}``. It can be change at any time on the application
setting page.

The ``--pre_release`` option is used to specify if the uploaded package is ready for distribution
or if it needs extra steps before that. In some cases, the package needs to be signed and then
re-uploaded on the server.

::

    slicer_package_manager_client package upload APP_NAME FILE_PATH [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application
* ``FILE_PATH`` - The path to the application package file to upload

Options:

* ``--os`` - The target operating system of the package
* ``--arch`` - Architecture that is supported by the application package
* ``--name`` - The basename of the new application package
* ``--repo_type`` - The repository type of the application package
* ``--repo_url`` - The repository URL of the application package
* ``--revision`` - The revision of the application package
* ``--coll_id`` - ID of an existing collection
* ``--pre_release`` - Boolean to specify if the package is ready to be distributed
* ``--desc`` - The description of the new application


List application packages
^^^^^^^^^^^^^^^^^^^^^^^^^

Use options to filter the listed application packages. By default, the command will list all
the application packages from the 'draft' release. It is possible to use the ``--release``
option to list the application package from a particular release.

::

    slicer_package_manager_client package list APP_NAME [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application

Options:

* ``--os`` - The target operating system of the package
* ``--arch`` - Architecture that is supported by the application package
* ``--revision`` - The revision of the application
* ``--release`` - The release within list all the application package
* ``--name`` - Basename of an application package
* ``--limit`` - Limit on the number of listed application package
* ``--coll_id`` - ID of an existing collection

Download an application package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default the package will be store in the current folder

::

    slicer_package_manager_client package download APP_NAME ID_OR_NAME [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application
* ``ID_OR_NAME`` - The ID or name of the application package which will be downloaded

Options:

* ``--dir_path`` - Path where will be save the application package after the download
* ``--coll_id`` - ID of an existing collection

Delete an application package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Provide either the ID or the name of the application package to delete it.

::

    slicer_package_manager_client package delete APP_NAME ID_OR_NAME

Arguments:

* ``APP_NAME`` - The name of the application
* ``ID_OR_NAME`` - The ID or name of the application package which will be deleted

Options:

* ``--coll_id`` - ID of an existing collection

Extension
---------

Use ``slicer_package_manager_client extension`` to upload, download or just list extensions

Upload a new extension
^^^^^^^^^^^^^^^^^^^^^^

Give the ``FILE_PATH`` argument to be able to upload an extension. The extension will then
automatically be added to the release which has the same revision than the ``--app_revision``
value. By default, if any release corresponds to the given revision, the extension will be
uploaded in the `draft` folder within the 'draft' release which has the given revision as
metadata, or create it if it doesn't exist yet.

The final name of the extension will depend of the ``extensionPackageNameTemplate`` set as
metadata on the application folder. The default name is
``{app_revision}_{baseName}_{os}_{arch}_{revision}``. It can be change at any time on the
application setting page.

::

    slicer_package_manager_client extension upload APP_NAME FILE_PATH [OPTIONS]

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
* ``--coll_id`` - ID of an existing collection
* ``--desc`` - The description of the new application

List extensions
^^^^^^^^^^^^^^^

Use options to filter the listed extensions. By default, the command will list all the extension
from the 'draft' release. It is possible to use the ``--release`` option to list the extension
from a particular release. Or use the flag ``--all`` to list all the extension present in the
application. It is also possible to get only one extension by providing the ``--fullname``
option of an extension.

::

    slicer_package_manager_client extension list APP_NAME [OPTIONS]

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
* ``--coll_id`` - ID of an existing collection


Download an extension
^^^^^^^^^^^^^^^^^^^^^

::

    slicer_package_manager_client extension download APP_NAME ID_OR_NAME [OPTIONS]

Arguments:

* ``APP_NAME`` - The name of the application
* ``ID_OR_NAME`` - The ID or name of the extension which will be downloaded

Options:

* ``--dir_path`` - Path where will be save the extension after the download
* ``--coll_id`` - ID of an existing collection


Delete an extension
^^^^^^^^^^^^^^^^^^^

Provide either the ID or the name of the extension to delete it.

::

    slicer_package_manager_client extension delete APP_NAME ID_OR_NAME

Arguments:

* ``APP_NAME`` - The name of the application
* ``ID_OR_NAME`` - The ID or name of the extension which will be deleted

Options:

* ``--coll_id`` - ID of an existing collection

