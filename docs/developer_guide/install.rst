============
Installation
============

You can either install the Slicer Package Manager natively on your machine or inside it's own
`virtual environment <https://docs.python-guide.org/en/latest/dev/virtualenvs/>`_.

Virtual environment
-------------------

While not strictly required, it is recommended to install the Slicer Package Manager and Girder
within its own virtual environment to isolate its dependencies from other python packages.
To generate a new virtual environment, first install/update the ``virtualenv`` and ``pip``
packages::

    $ sudo pip install -U virtualenv pip

Now create a virtual environment using the `virtualenv command <https://virtualenv.readthedocs.io/en/latest/user_guide.html>`_. You can place the virtual environment directory wherever you want, but
it should not be moved. The following command will generate a new directory called
``slicer_package_manager_env`` in your home directory::

    $ virtualenv ~/slicer_package_manager_env

Then to enter in the virtual environment, use the command::

    $ . ~/slicer_package_manager_env/bin/activate

.. note::
    The ``(slicer_package_manager_env)`` prepended to your prompt indicates you have entered the
    virtual environment.

Install from Git
----------------

To easily develop the Slicer Package Manager, you will need to use some of Girder commands.
So let's start by installing Girder::

    $ git clone https://github.com/girder/girder.git
    $ cd girder
    $ pip install -e .


Then, let's install the Slicer Package Manager server plugin:

    $ git clone https://github.com/girder/slicer_package_manager
    $ cd slicer_package_manager
    $ pip install -e .[test]


This will provide you all the package needed to run the development environment. Then install
the front-end web client development dependencies::

    $ girder build --dev


Run
---

To run the server, first make sure the Mongo daemon is running. To manually start it, run::

    $ mongod &

Then to run Girder itself, just use the following command::

    $ girder-server --dev

The application should be accessible on http://localhost:8080/ in your web browser.
