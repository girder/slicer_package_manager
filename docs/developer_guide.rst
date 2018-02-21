Developer Guide
===============

As **Slicer Extension Manager** is part of Girder plugins, it's also split in 2 different parts:

* Back-end (server side)
* Front-end (client side)

To have a better idea of how contributing on a plugin within the Girder community, let's read the `Plugin Development
documentation <http://girder.readthedocs.io/en/latest/plugin-development.html>`_.

Developer Installation
----------------------

You can either install Slicer Extension Manager natively on your machine or inside a virtual environment.

Virtual environment
^^^^^^^^^^^^^^^^^^^
TODO


--> Use girder-install web --dev or --watch-plugin ... TODO

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

Tests are the base of software, they permit to check if what you've expect is really happening and find error you didn't
even think about. There is few thing you should know about test within the Slicer Extension Manager.

Server Side Testing
^^^^^^^^^^^^^^^^^^^

As part of Girder, server test are done using `pytest <https://docs.pytest.org/en/latest/>`_. Let's read the
`server test documentation <http://girder.readthedocs.io/en/latest/development.html#server-side-testing>`_ to know more
about Girder testing.

Python Client Testing
^^^^^^^^^^^^^^^^^^^^^

To see an example of Python Client Testing let's take a look at the `Source Code
<https://github.com/girder/slicer_extension_manager/blob/master/plugin_tests/python_client_tests/
slicer_extension_manager_client_test.sh>`_

This test is also used within CircleCi.

Docker container testing
^^^^^^^^^^^^^^^^^^^^^^^^

In CircleCI configuration file, there is directive to test the build and the deploy of the different Docker container.


Regenerate Documentation Locally
--------------------------------

When developing new feature it's very important to add some documentation to explain the community what is it and
how to use it. The Slicer Extension Manager Documentation is build thanks to
`Sphinx <http://www.sphinx-doc.org/en/master/>`_, an open source documentation generator.


Here is some tools very useful to rapidly see what is result of your documentation.

In the 'slicer_extension_manager' directory, just run::

    make docs

This will automatically create the API documentation for you and open a web browser tab to visualize the documentation.
If you don't want to open a new tab and just rebuild the documentation run::

    make docs-only

