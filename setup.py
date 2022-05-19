# -*- coding: utf-8 -*-

import versioneer

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = [
    'girder>=3.0.0a1'
]

setup(
    author='Jean-Christophe Fillion-Robin',
    author_email='slicer-packages-support@kitware.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    description='Manage Slicer application and extension packages.',
    install_requires=requirements,
    license='Apache Software License 2.0',
    long_description=readme,
    long_description_content_type='text/x-rst',
    include_package_data=True,
    keywords='girder-plugin, slicer_package_manager',
    name='slicer_package_manager',
    packages=find_packages(exclude=['test', 'test.*']),
    python_require='>=3.7',
    url='https://github.com/girder/slicer_package_manager',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    zip_safe=False,
    entry_points={
        'girder.plugin': [
            'slicer_package_manager = slicer_package_manager:GirderPlugin'
        ]
    }
)
