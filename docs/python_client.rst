.. _python_client:

=============
Python Client
=============

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

.. note::
    *The API-KEY is given as an exemple, follow the documentation on* api-key_ *to create one.*

Then you can start using the API that allow you to easily create applications, manage release,
upload and download extension, see :doc:`python_client_commands` documentation for more details.

.. _api-key: http://girder.readthedocs.io/en/latest/user-guide.html#api-keys
.. _documentation: http://girder.readthedocs.io/en/latest/user-guide.html#api-keys
