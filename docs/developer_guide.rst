Developer Guide
===============

As **Slicer Extension Manager** is part of Girder plugins, it's also split in 2 different parts:

* Back-end (server side)
* Front-end (client side)

To have a better idea of how contributing on a plugin within the Girder community, let's read the `Plugin Development
documentation <http://girder.readthedocs.io/en/latest/plugin-development.html>`_.

Set up the development environment
----------------------------------

--> VM ... TODO

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



