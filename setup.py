import versioneer

from setuptools import setup

# This file is required to support editable install
# See https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)
