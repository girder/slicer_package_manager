==========
User Guide
==========

The **Slicer Package Manager** is a Girder plugin to easily manage application packages
and extension packages from an Application. It is used by the Slicer community to share
Slicer extensions by allowing to Upload and Download them. Build onto the open source
data management platform: **Girder**, the **Slicer Package Manager** use some of the
`girder concepts`_ developed in Girder and embedded new ones as Application, Release,
Draft, Package or Extension.

This plugin is designed to be robust, fast, extensible and easy to use.

The server side is built in Python under the open source
`Apache License, version  2.0 <https://www.apache.org/licenses/LICENSE-2.0.html>`_.

How to use the Slicer Package Manager?
----------------------------------------

There are 3 different ways to use the Slicer Package Manager:

* By using the User Interface (Work In Progress):

    If you don't want to use neither the Shell or python script, this UI is made for you.
    Let see the [documentation] to know how to use it.

* By using the :doc:`slicer_package_manager_client` within Python script:

    Using the Python Client API allow you to write scripts for create application, new release and
    automatically upload or download application or extensions packages.

* By using the :doc:`commands_shell`:

    This is the more easy way to use the basic feature of the Slicer Package Manager.
    These commands allow you to easily create, list, or delete applications and releases,
    and also list, upload, download or delete application or extension packages.

.. _girder concepts: https://girder.readthedocs.io/en/latest/user-guide.html#concepts

.. _concepts:

Concepts
--------

* **Application**:

    Applications are simple *Girder Folder*. They represent top-level folders which contain
    all the different releases, application and extensions packages of your application.
    By default when you create a new application, it will automatically be created within
    the default Girder collection 'Applications'
    (see `Girder concept <https://girder.readthedocs.io/en/latest/user-guide.html#concepts>`_
    to learn more about Girder collections and Folder).

    Applications contain metadata that organize the application and extension packages
    following a same name:

    * ``applicationPackageNameTemplate`` (set as ``{baseName}_{os}_{arch}_{revision}`` by default).

    * ``extensionPackageNameTemplate`` (set as ``{app_revision}_{baseName}_{arch}_{os}_{revision}``
      by default).

    These template names correspond to the given name of all the uploaded application or
    extensions packages. Which means that all the packages (application or extension) will
    have a name that follow these templates depending on their given metadata during the
    upload.

    These templates can be changed at anytime using the Girder UI on the application view.

* **Release**:

    Release are also simple *Girder Folder*. They are part of an application and correspond to a
    specific revision of this application. They meant to contain application or extension packages
    which correspond to this specific application revision.
    It's why each release has the application ``revision`` as metadata.

* **Draft**:

    Draft is a simple *Girder Folder* which contain a flat list of **Release** named as the
    corresponding application revision by default. When a new application is created, the *draft*
    folder is also created. This *draft* folder is used as default release when the upload
    of an application or an extension package occurs and which its own *application revision*
    doesn't correspond to any release of the application (by checking the correspondence
    between the ``revision`` metadata stored on the release and the ``app_revision`` stored on
    the packages).

    However the *draft* folder does not contain any metadata. Only the release that's contained
    into it got a ``revision`` metadata (corresponding to the application revision they are
    made for).

* **Package**:

    Package (application package) are *Girder Item* which contains only one binary file (the real
    application package). They are part of an application, and can only be found in a release
    folder. They are named following the ``applicationPackageNameTemplate`` set on the application
    they are made for.

    Each application package contain a bunch of metadata that give us information on which
    environment the package is made for like : Operating System: ``os``, architecture: ``arch``,
    application revision: ``revision``, repository url... (see the
    `list of parameters of Package <https://slicer-package-manager.readthedocs.io/en/latest/
    slicer_package_manager.api.html#slicer_package_manager.api.app.App.createOrUpdatePackage>`_
    on the server API to have an exhausted list of all the metadata).

    When uploading an application package, some of these metadata are required, the ``revision``
    metadata is used to determine in which release to upload the application package.
    The release which have the same ``revision`` metadata will see the application package
    uploaded into it.
    If any release within the application has a matching revision,
    the application package will be uploaded into the corresponding *draft* release (by default).
    By searching for an existing draft release (with the matching revision) or if it doesn't
    already exist, by creating a new one.

    The package file (binary file) during the upload will be kept as it within Girder. So when
    the extension will be downloaded, the downloaded file will keep the same extension
    (.bin, .zip, ...). For instance, if the uploaded package is named 'pkg.tar.gz', then each
    time this application package will be downloaded, the downloaded file will keep the same
    '.tar.gz' extension.

* **Extension**:

    As an application package, an Extension package is also a *Girder Item*, and has the same
    behavior than an application package. It contain a single binary file. The name of all
    uploaded extension follow the ``extensionPackageNameTemplate`` metadata stored in the
    **Application**.

    See the `list of parameters of Extension <https://slicer-package-manager.readthedocs.io/en/latest/server.api.html
    #server.api.app.App.createOrUpdateExtension>`_ on the server API to have an exhausted list of all the metadata.


Schema of concepts
------------------
::

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

Download Statistics
-------------------

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
