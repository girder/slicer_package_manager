==========
User Guide
==========

The **Slicer Extension Manager** is a Girder plugin to easily manage packages or extensions from an Application.
It is used by the Slicer community to share Slicer extensions by allowing to Upload and Download them.
Build onto the open source data management platform: **Girder**, the **Slicer Extension Manager** use some of the
concepts_ developed in Girder and embedded new ones as Application, Release or Extension.

This plugin is designed to be robust, fast, extensible and easy to use.

The server side is built in Python under the open source
`Apache License, version  2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>`_.

How to use the Slicer Extension Manager?
----------------------------------------

There are 3 different ways to use the Slicer Extension Manager:

* By using the User Interface (Work In Progress):

    If you don't want to use neither the Shell or python script, this UI is made for you. Let see the [documentation] to
    know how to use it.

* By using the :doc:`python_client` within Python script:

    Using the Python Client API allow you to write scripts for create application, release
    automatically upload extensions...

* By using the :doc:`commands_shell`:

    This is the more easy way to use the basic feature of the Slicer Extension Manager. These commands allow you to
    easily create or list applications and releases, and also list, upload or download extensions.

.. _concepts: http://girder.readthedocs.io/en/latest/user-guide.html#concepts

Concepts
--------

* **Application**:

    Applications are simple *Girder Folder*. They represent top-level folders which contain all the
    different releases and extensions or packages of your applications. By default when you create a new application, it
    will automatically be created within the default Girder collection 'Applications'
    (see `Girder concept <http://girder.readthedocs.io/en/latest/user-guide.html#concepts>`_ to learn more
    about Girder collections and Folder).

    Applications contain one ``extensionNameTemplate`` metadata which is set as
    ``{app_revision}_{os}_{arch}_{baseName}_{revision}`` by default.

    This template name corresponds to the future name of all the uploaded extensions for this specific application.
    Which means that all the extension will have the following name depending on their given metadata when uploaded.
    It can be changed at anytime using the Girder UI on the application view.

* **Release**:

    Release are also simple *Girder Folder*. They are part of an application and correspond to a specific revision of
    this application.
    They meant to contain packages or extensions which are developed for this specific application revision.
    It's why each release has the application ``revision`` as metadata.

    By default, when creating a new application, the 'Nightly' release is created. This release is used as default
    release to upload an extension or a package which its own ``app_revision`` metadata doesn't correspond to any
    release of the application (by checking the correspondence between the ``revision`` metadata stored on the release
    and the ``app_revision`` set when the upload occurs).
    This default release is the only one which will not have any application ``revision`` store as metadata.

* **Extension**:

    Extension are *Girder Item* which contains only one binary file (the real extension package).
    They are part of an application, and can only be found in a release folder. They are named following the
    ``extensionNameTemplate`` set on the application they are made for.
    Each extension contain a bunch of metadata that give us information on which environment can use the extension like
    Operating System: ``os``, architecture: ``arch``, application revision: ``app_revision``, repository url...
    (see the `list of parameters <http://slicer-extension-manager.readthedocs.io/en/latest/server.api.html
    #server.api.app.App.createOrUpdateExtension>`_ on the server API to have an exhausted list of all the metadata).


    When uploading an extension, some of these metadata are required, and the ``app_revision`` is used to determined
    in which release to upload the extension. The release which have the same ``revision`` as the given ``app_revision``
    metadata will be added the extension. If any release within the application has a corresponding revision,
    the extension will be uploaded directly into the 'Nightly' release (by default).

    The file extension (binary file) during the upload will be kept as it within Girder. So when the extension will be
    downloaded, the downloaded file will keep the same extension (.bin, .zip, ...). For instance, if the uploaded
    extension is named 'ext.tar.gz', then each time this extension will be downloaded, the downloaded file will keep
    the same '.tar.gz' extension.

Schema of concepts
------------------

.. image:: images/slicer_extension_manager_models.JPG


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
