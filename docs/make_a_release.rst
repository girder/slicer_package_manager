.. _making_a_release:

================
Making a release
================

A core developer should use the following steps to create a release `X.Y.Z` of
**slicer-package-manager** on `PyPI`_.

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


5. In `CHANGES.rst` replace ``Next Release`` section header with
   ``X.Y.Z`` and commit the changes.

  .. code::

    $ git add CHANGES.rst && \
      git commit -m "slicer-package-manager ${release}"


6. Tag the release

  .. code::

    $ git tag --sign -m "slicer-package-manager ${release}" ${release} master

  .. warning::

      We recommend using a `GPG signing key <https://help.github.com/articles/generating-a-new-gpg-key/>`_
      to sign the tag.


7. Create the source distribution and wheel

  .. code::

    $ python setup.py sdist bdist_wheel


8. Publish the both release tag and the master branch

  .. code::

    $ git push origin ${release} && \
      git push origin master


9. Upload the distributions on `PyPI`_

  .. code::

    twine upload dist/*

  .. note::

    To first upload on `TestPyPI`_ , do the following::

        $ twine upload -r pypitest dist/*


10. Create a clean testing environment to test the installation

  .. code::

    $ pushd $(mktemp -d) && \
      mkvirtualenv slicer-package-manager-${release}-install-test && \
      pip install slicer-package-manager==${release}

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
      rmvirtualenv slicer-package-manager-${release}-install-test


13. Add a ``Next Release`` section back in `CHANGES.rst`, commit and push local changes.

  .. code::

    $ git add CHANGES.rst && \
      git commit -m "CHANGES.rst: Add \"Next Release\" section [ci skip]" && \
      git push origin master


.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/
.. _virtualenv: http://virtualenv.readthedocs.io
.. _venv: https://docs.python.org/3/library/venv.html

.. _CircleCI: https://app.circleci.com/pipelines/github/girder/slicer_package_manager

.. _PyPI: https://pypi.org/project/slicer-package-manager
.. _TestPyPI: https://test.pypi.org/project/slicer-package-manager
