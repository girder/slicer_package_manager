# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

install_reqs = [
    'click>=6.7',
    'girder_client',
    'pytest-vcr',
    'tabulate'
]
with open('README.rst') as f:
    readme = f.read()

# perform the install
setup(
    name='slicer_package_manager_client',
    version='0.0.1',
    description='Python client for interacting with the Slicer package manager endpoint.',
    long_description=readme,
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    url='https://slicer-package-manager.readthedocs.io/en/latest/commands_shell.html#slicer-package-manager-client',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    packages=find_packages(exclude=('tests.*', 'tests')),
    python_require='>=3.7',
    install_requires=install_reqs,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'slicer_package_manager_client = slicer_package_manager_client.cli:main'
        ]
    }
)
