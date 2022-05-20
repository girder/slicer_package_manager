.. _making_a_release:

================
Making a release
================

A core developer should use the following steps to create a release `X.Y.Z` of
**slicer-package-manager** and **slicer-package-manager-client** on `PyPI`_.

-------------
Prerequisites
-------------

* All CI tests are passing on `CircleCI`_.

* You have a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_.

-------------------------
Documentation conventions
-------------------------

The commands reported below should be evaluated in the same terminal session.

Commands to evaluate starts with a dollar sign. For example::

  $ echo "Hello"
  Hello

means that ``echo "Hello"`` should be copied and evaluated in the terminal.

----------------------
Setting up environment
----------------------

1. First, `register for an account on PyPI <https://pypi.org>`_.


2. If not already the case, ask to be added as a ``Package Index Maintainer``.


3. Create a ``~/.pypirc`` file with your login credentials::

    [distutils]
    index-servers =
      pypi
      pypitest

    [pypi]
    username=__token__
    password=<your-token>

    [pypitest]
    repository=https://test.pypi.org/legacy/
    username=__token__
    password=<your-token>

  where ``<your-token>`` correspond to the API token associated with your PyPI account.

---------------------
`PyPI`_: Step-by-step
---------------------

1. Make sure that all CI tests are passing on `CircleCI`_.


2. Download the latest sources

  .. code::

    $ cd /tmp && \
      git clone git@github.com:girder/slicer_package_manager && \
      cd slicer_package_manager


3. List all tags sorted by version

  .. code::

    $ git fetch --tags && \
      git tag -l | sort -V


4. Choose the next release version number

  .. code::

    $ release=X.Y.Z

  .. warning::

      To ensure the packages are uploaded on `PyPI`_, tags must match this regular
      expression: ``^[0-9]+(\.[0-9]+)*(\.post[0-9]+)?$``.


5. In ``CHANGES.rst`` replace ``Next Release`` section header with ``X.Y.Z``,
   in ``python_client/slicer_package_manager_client/__init__.py`` update version
   with ``X.Y.Z`` and commit the changes.

  .. code::

    $ git add CHANGES.rst && \
      git add python_client/slicer_package_manager_client/__init__.py && \
      git commit -m "slicer-package-manager[-client] ${release}"


6. Tag the release

  .. code::

    $ git tag --sign -m "slicer-package-manager[-client] ${release}" ${release} main

  .. warning::

      We recommend using a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_
      to sign the tag.


7. Create the source distribution and wheel for **slicer-package-manager**

  .. code::

    $ pipx run build

  .. note::

    `pipx <https://pypa.github.io/pipx/>`_ allows to directly run the `build frontend <https://pypa-build.readthedocs.io>`_
    without having to explicitly install it.

    To install `pipx`::

        $ python3 -m pip install --user pipx


8. Create the source distribution and wheel for **slicer-package-manager-client**

  .. code::

    $ pipx run build ./python_client


8. Publish the both release tag and the main branch

  .. code::

    $ git push origin ${release} && \
      git push origin main


9. Upload the distributions on `PyPI`_

  .. code::

    $ pipx run twine upload dist/*
    $ pipx run twine upload python_client/dist/*

  .. note::

    To first upload on `TestPyPI`_ , do the following::

        $ pipx run twine upload -r pypitest dist/*
        $ pipx run twine upload -r pypitest python_client/dist/*


10. Create a clean testing environment to test the installation

  .. code::

    $ pushd $(mktemp -d) && \
      mkvirtualenv slicer-package-manager-${release}-install-test && \
      pip install slicer-package-manager==${release}

    $ pushd $(mktemp -d) && \
      mkvirtualenv slicer-package-manager-client-${release}-install-test && \
      pip install slicer-package-manager-client==${release} && \
      slicer_package_manager_client --version

  .. note::

    If the ``mkvirtualenv`` command is not available, this means you do not have `virtualenvwrapper`_
    installed, in that case, you could either install it or directly use `virtualenv`_ or `venv`_.

    To install from `TestPyPI`_, do the following::

        $ pip install -i https://test.pypi.org/simple slicer-package-manager==${release}


12. Cleanup

  .. code::

    $ popd && \
      deactivate  && \
      rm -rf dist/* && \
      rmvirtualenv slicer-package-manager-${release}-install-test && \
      rm -rf python_client/dist/* && \
      rmvirtualenv slicer-package-manager-client-${release}-install-test


13. Add a ``Next Release`` section back in `CHANGES.rst`, commit and push local changes.

  .. code::

    $ git add CHANGES.rst && \
      git commit -m "CHANGES.rst: Add \"Next Release\" section [ci skip]" && \
      git push origin main


.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/
.. _virtualenv: http://virtualenv.readthedocs.io
.. _venv: https://docs.python.org/3/library/venv.html

.. _CircleCI: https://app.circleci.com/pipelines/github/girder/slicer_package_manager

.. _PyPI: https://pypi.org/project/slicer-package-manager
.. _TestPyPI: https://test.pypi.org/project/slicer-package-manager
