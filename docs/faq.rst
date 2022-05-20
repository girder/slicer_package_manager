===
FAQ
===

*Frequently Asked Questions*

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

To know more about Slicer extension, see the `Extensions Manager`_ documentation.

.. _Extensions Manager: https://slicer.readthedocs.io/en/latest/user_guide/extensions_manager.html


Does the server collect download statistics ?
---------------------------------------------

Each time an extension is downloaded (using the Client or the UI), a metadata is incremented on the release folder.
This allow to referenced all downloaded extension even after their deletion.

The download count is stored in the metadata following this rule::

    $ {
        'downloadExtensions': {
            baseName: {
                os: {
                    arch: downloadCount
                }
            }
        }

How to interface with the Slicer Package Manager server ?
---------------------------------------------------------

There are 3 different ways to use the Slicer Package Manager server:

* By using the :doc:`commands_shell`:

    This is the more easy way to use the basic feature of the Slicer Package Manager.
    These commands allow you to easily create, list, or delete applications and releases,
    and also list, upload, download or delete application or extension packages.

* By using the :doc:`developer_guide/slicer_package_manager_client` within Python script:

    Using the Python Client API allow you to write scripts for create application, new release and
    automatically upload or download application or extensions packages.

* By using the User Interface:

    The default girder user interface allows to browse through the `Application`, `Release` and `Draft`
    Girder folders and their associated `Package` and `Extension` Girder items.

How to create a new release with existing uploaded packages?
------------------------------------------------------------

Follow this few steps to be able to update a draft release into a stable release:

*   Open the Girder UI, go under your application folder (Slicer here). By default it should be inside the
    ``Applications`` collection, that you can find under the ``Collections`` item in the main menu.

::

    Applications
           |--- packages
           |        |----- Slicer

*   Look for the specific application revision folder under the ``draft`` folder within the application. All the packages
    which are contained in this folder will be part of the futur new stable release.

*   Select all the element contained in this folder by using the ``Pick all checked resources for Copy or Move`` action

*   Go to the new release folder, that you can create both by using the CLI or the Girder UI. In the case of the Girder UI
    you will need to give a specific metadata on the folder: ``revision: <revision-of-the-application>`` corresponding the
    this release.

*   Once you created the new release folder, enter inside it, then use the ``Copy picked resources here``

*   You will just need to delete the draft sub-folder used to make the new stable release

How to clean up the Draft release folder?
-----------------------------------------

Every day more than 300 extensions are supposed to be uploaded into the Slicer Package Manager. It's important to be
able to clean up the old packages occasionally. Here's the process to do it:

The command: ``slicer_package_manager_client draft list <APP_NAME> --offset <N>`` allows to list the oldest draft subfolders
related to old application revision. Using this command, you will be able to get a list of ``revision`` and then use the
command ``slicer_package_manager_client draft delete <APP_NAME> <REVISION>`` in a loop to delete them all.

There is also a bash script you can use easily to do that for you. In the directory
``slicer_package_manager/python_client``, you will find the ``cleanNightly.sh`` script.

To be able to run this script make sure to have the ``slicer_package_manager_client`` installed on your machine, if not
check the :doc:`commands_shell` documentation.

Then just enter::

    $ ./cleanNightly.sh <API_URL> <API_KEY> <N>

* API_URL: The URL of the distant machine, for instance http://192.168.xxx.xxx/api/v1

* API_KEY: The token that allow you to use the client

* N: Number of draft release you want to keep, all the oldest will be deleted
