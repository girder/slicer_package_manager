================
Vendoring Policy
================

*Adapted from https://github.com/pypa/pip/blob/main/src/pip/_vendor/README.rst*

* Vendored libraries **MUST** not be modified except as required to
  successfully vendor them.

* Vendored libraries **MUST** be released copies of libraries available on
  PyPI.

* Vendored libraries **MUST** be available under a license that allows
  them to be integrated into ``slicer-package-manager-client``, which is released
  under the Apache Software License 2.0.

* Vendored libraries **MUST** be accompanied with LICENSE files.

* The versions of libraries vendored in pip **MUST** be reflected in
  ``slicer_package_manager_client/_vendor/README.rst``.

* Vendored libraries **MUST** function without any build steps such as ``2to3``
  or compilation of C code, practically this limits to single source 2.x/3.x and
  pure Python.

* Any modifications made to libraries **MUST** be documented in
  ``slicer_package_manager_client/_vendor/README.rst`` and their corresponding patches **MUST** be
  included ``tools/vendoring/patches``.


Vendored Libraries
==================

* pymongo==3.12.3
  - https://github.com/mongodb/mongo-python-driver/tree/3.12.3
  - keep ``bson/errors.py``, ``bson/objectid.py``, ``bson/py3compat.py``and ``bson/tz_util.py``
  - empty ``bson/__init__.py``
  - update ``bson/objectid.py``to use relative imports for ``errors``, ``objectid`` and ``tz_util``.
