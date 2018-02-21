Developer Guide
===============

As **Slicer Extension Manager** is part of Girder plugins, it's also split in 2 different parts:

* Back-end/server side (a CherryPy-based Python module)
* Front-end/client side (Work In Progress)

To have a better idea of how contributing on a plugin within the Girder community, let's read the `Plugin Development
documentation <http://girder.readthedocs.io/en/latest/plugin-development.html>`_.


Developer Installation
----------------------

You can either install Slicer Extension Manager natively on your machine or inside it's own `virtual environment
<http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

Virtual environment
^^^^^^^^^^^^^^^^^^^
While not strictly required, it is recommended to install the Slicer Extension Manager and Girder within its own
virtual environment to isolate its dependencies from other python packages.
To generate a new virtual environment, first install/update the ``virtualenv`` and ``pip`` packages::

    $ sudo pip install -U virtualenv pip

Now create a virtual environment using the `virtualenv command <http://virtualenv.readthedocs.io/en/latest
/userguide/>`_. You can place the virtual environment directory wherever you want, but it should not be moved.
The following command will generate a new directory called ``slicer_extension_manager_env`` in your home directory::

    $ virtualenv ~/slicer_extension_manager_env

Then to enter in the virtual environment, use the command::

    $ . ~/slicer_extension_manager_env/bin/activate

.. note::
    The ``(slicer_extension_manager_env)`` prepended to your prompt indicates you have entered the virtual environment.

Install from Git
^^^^^^^^^^^^^^^^^

To easily develop the Slicer Extension Manager, you will need to use some of Girder commands. So let's start by
installing Girder::

    $ git clone --branch 2.x-maintenance https://github.com/girder/girder.git
    $ cd girder

To run the server, you must install some external Python package dependencies::

    $ pip install -e .

This will provide you all the package needed to run the development environment. Then install the front-end web
client development dependencies::

    $ girder-install web --dev

Run
^^^

To run the server, first make sure the Mongo daemon is running. To manually start it, run::

    $ mongod &

Then to run Girder itself, just use the following command::

    $ girder-server

Then open http://localhost:8080/ in your web browser, and you should see the application.


During development
------------------

Once Girder is started via ``girder-server``, the server will reload itself whenever a Python file is modified.
If you are doing front-end development, it’s much faster to use a watch process to perform automatic fast
rebuilds of your code whenever you make changes to source files.

If you are developing the web client of Slicer extension manager plugin, run::

    $ girder-install web --watch-plugin slicer_extension_manager


Server side development
-----------------------

See the `Server Development documentation <http://girder.readthedocs.io/en/latest/development.html#server-development>`_
to know more about the good development practise in Girder


Client side development
-----------------------

See the `Client Development documentation <http://girder.readthedocs.io/en/latest/development.html#client-development>`_
to know more about the good development practise in Girder


Python client development
-------------------------

The development of the **Slicer Extension Manager Client** is in Python, it must work on both 2.7 and 3.5 version of
python, and follow flake8_ (the wrapper which verifies ``pep8``, ``pyflakes`` and ``circular complexity``)

The python client use click_ a command line library for Python.

.. _flake8: https://pypi.python.org/pypi/flake8
.. _click: http://click.pocoo.org


Testing
-------

Tests are the base of software development, they meant to check if what you've expect is really happening and find
error you didn't even think about. There is few thing you should know about test within the Slicer Extension Manager.

.. _server_side_testing:

Server Side Testing
^^^^^^^^^^^^^^^^^^^

As part of Girder, server test are done using `pytest <https://docs.pytest.org/en/latest/>`_. Let's read the
`server test documentation <http://girder.readthedocs.io/en/latest/development.html#server-side-testing>`_ to know more
about Girder testing.

.. _python_client_testing:

Python Client Testing
^^^^^^^^^^^^^^^^^^^^^

To see an example of Python Client Testing let's take a look at the `Source Code
<https://github.com/girder/slicer_extension_manager/blob/master/plugin_tests/python_client_tests/
slicer_extension_manager_client_test.sh>`_

This test is also used within CircleCi.

To run locally this test, from the slicer_extension_manager folder run::

    $ cd plugin_tests/python_client_tests

Then run::

    $ ./slicer_extension_manager_client_test.sh

It will run some of the commands available with the ``slicer_extension_manager_client``, check if the upload and
the download works and then delete everything.

This script could be take as a good example of using the :doc:`commands_shell`.

CircleCI tests
^^^^^^^^^^^^^^

In the `CircleCI configuration file
<https://github.com/girder/slicer_extension_manager/blob/master/.circleci/config.yml>`_,
there are several test going on:

* :ref:`server_side_testing`

    It will occurs each time a commit will be pushed on the repository (Source code at `s_e_m_test.py
    <https://github.com/girder/slicer_extension_manager/blob/master/plugin_tests/s_e_m_test.py>`_).

* :ref:`python_client_testing`

* Docker containers testing

    Test the build and the deploy of the different :ref:`docker_containers`.


Regenerate Documentation Locally
--------------------------------

When developing new feature it's very important to add some documentation to explain the community what is it and
how to use it. The Slicer Extension Manager Documentation is build thanks to
`Sphinx <http://www.sphinx-doc.org/en/master/>`_, an open source documentation generator.


Here is some tools very useful to rapidly see what is result of your documentation.

In the 'slicer_extension_manager' directory, just run::

    $ make docs

This will automatically create the API documentation for you and open a web browser tab to visualize the documentation.
If you don't want to open a new tab and just rebuild the documentation run::

    $ make docs-only


.. _docker_containers:

Docker containers
-----------------

Docker containers allow an easy use and setup of the Slicer extension manager. There are 3 different containers that
communique between them.

* The application container

    It contains both the **Girder** application with its plugin the **Slicer Extension Manager**.

* The database container

    This one contains the **MongoDB** instance that allow the Girder and the Slicer Extension Manager to store all the
    data as Applications, Releases or Extensions.

* The provisioning container

    This container is special, its only used once both the Girder server is running and connected to the Mongo server.
    It is meant to configure the server to make the use of the Slicer Extension Manager easier. By doing that it
    **enable the Slicer Extension Manager plugin within Girder** and it also create a first **admin user**, and set up
    the **assetstore** used to store the binary files (In fact the DB only store reference to these files, the real data
    are stored on your own machine in the assetstore).
