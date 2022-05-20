During development
------------------

Once Girder is started via ``girder-server``, the server will reload itself whenever a server
source file is modified. If you are doing front-end development, it’s much faster to use a watch
process to perform automatic fast rebuilds of your code whenever you make changes to source files.

If you are front-end development of Slicer package manager plugin, use::

    $ girder-install web --watch-plugin slicer_package_manager


Server side development
-----------------------

See the `Server Development documentation <https://girder.readthedocs.io/en/latest/development.html
#server-development>`_ to know more about the good development practise in Girder


Client side development
-----------------------

See the `Client Development documentation <https://girder.readthedocs.io/en/latest/development.html
#client-development>`_ to know more about the good development practise in Girder


Python client development
-------------------------

The development of the **Slicer Package Manager Client** is in Python, it must work on both 2.7
and 3.5 version of python, and follow flake8_ (the wrapper which verifies ``pep8``, ``pyflakes``
and ``circular complexity``).

The python client use click_, a command line library for Python.

.. _flake8: https://pypi.python.org/pypi/flake8
.. _click: https://click.pocoo.org


Testing
-------

Tests are the base of software development, they meant to check if what you've expected is really
happening and find issues you didn't even think about. There are few thing you should know about
test within the Slicer Package Manager.

.. _server_side_testing:

Server Side Testing
^^^^^^^^^^^^^^^^^^^

As part of Girder, server test are done using `pytest <https://docs.pytest.org/en/latest/>`_.
Let's read the `server test documentation <https://girder.readthedocs.io/en/latest/development.html
#server-side-testing>`_ to know more about Girder testing.

.. _python_client_testing:

Python Client Testing
^^^^^^^^^^^^^^^^^^^^^

The Python Client use `pytest <https://docs.pytest.org/en/latest/>`_ to test its API. It also
uses a tool named `pytest-vcr <https://pytest-vcr.readthedocs.io/en/latest/>`_ to record the
server responses and be able to test the client within CircleCI.

.. note::

    Each time the client will change, or the tests, you will have to record the server an other
    time by running the tests manually. But first, you will have to delete the old records.
    All the server records should be saved as ``.yml`` file into the ``cassettes`` folder
    next to your tests.
    Delete this folder, and then run the tests again, it should create new records automatically.

To run manually these test run the following command::

    $ pytest --tb=long plugin_tests/python_client_tests/test_python_client.py


The CLI is also briefly tested using a shell script. To see an example let's take a look at the
`Source Code <https://github.com/girder/slicer_package_manager/blob/
main/plugin_tests/python_client_tests/slicer_package_manager_client_test.sh>`_

This test is also used within CircleCi.

To run locally this test, from the ``slicer_package_manager`` folder run::

    $ cd plugin_tests/python_client_tests
    $ ./slicer_extension_manager_client_test.sh

It will run some of the commands available with the ``slicer_package_manager_client``, check if
the upload and the download works and then delete everything.

This script could be take as a good example of using the :doc:`../commands_shell`.

CircleCI tests
^^^^^^^^^^^^^^

In the `CircleCI configuration file
<https://github.com/girder/slicer_package_manager/blob/main/.circleci/config.yml>`_,
there are several test going on:

* :ref:`server_side_testing`

    It will occurs each time a commit will be pushed on the repository (Source code at
    `s_e_m_test.py <https://github.com/girder/slicer_package_manager/blob/main/plugin_tests/
    s_e_m_test.py>`_).

* :ref:`python_client_testing`

    Both the python client API and the CLI are tested

* Docker containers testing

    Test the build and the deploy of the different :ref:`docker_containers`.


Regenerate Documentation Locally
--------------------------------

When developing new feature it's very important to add some documentation to explain the community
what is it and how to use it. The Slicer Package Manager Documentation is build thanks to
`Sphinx <https://www.sphinx-doc.org/>`_, an open source documentation generator.


Here is some tools very useful to rapidly see what is result of your documentation.

In the ``slicer_package_manager/docs`` directory, just run::

    $ make docs

This will automatically create the API documentation for you and open a web browser tab to
visualize the documentation. If you don't want to open a new tab and just rebuild the
documentation run::

    $ make docs-only


.. _docker_containers:

Docker containers
-----------------

Docker containers allow an easy use and setup of the Slicer Package Manager. There are 3 different
containers that communique between themselves.

* The application container

    It contains both the **Girder** application with the **Slicer Package Manager** plugin enabled.

* The database container

    This one contains the **MongoDB** instance that allow the Girder and the Slicer Package
    Manager to store all the data as Applications, Releases, Application or Extension packages.

* The provisioning container

    This container is special, it is only used once both the Girder server and the Mongo server
    are running and connected to each other. It is meant to handle the server configuration and
    make the use of the Slicer Package Manager much easier. By doing that it
    **enables the Slicer Package Manager plugin within Girder**, create the first **admin user**,
    and set up the **assetstore** used to store the binary files (In fact the DB only store
    reference to these files, the real data are stored on your own machine in this assetstore).
