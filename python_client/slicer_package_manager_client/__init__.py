# -*- coding: utf-8 -*-

import os
from bson.objectid import ObjectId

from girder_client import GirderClient

__version__ = '0.0.1'
__license__ = 'Apache 2.0'

appName = 'Slicer'


class Constant:
    """
    A bunch of utilities constant, as to handle ``Error`` or set default parameters.
    """

    # Success
    PACKAGE_NOW_UP_TO_DATE = 31
    EXTENSION_AREADY_UP_TO_DATE = 32
    EXTENSION_NOW_UP_TO_DATE = 33

    # Default
    CURRENT_FOLDER = os.getcwd()
    DRAFT_RELEASE_NAME = 'draft'
    DEFAULT_LIMIT = 50

    # Display
    WIDTH = 25  # Shouldn't be less than 24


class SlicerPackageManagerError(Exception):
    pass


class SlicerPackageClient(GirderClient):
    """
    The SlicerPackageClient allows to use the slicer_package_manager plugin of Girder.
    This allow to manage 5 top level entities:

        * Application
        * Release
        * Draft
        * Package
        * Extension

    It's now possible to choose the collection within create the application. It's also
    possible to get an existing collection by ID for creating the application inside.

    In this case, you must provide the ``coll_id`` argument to be able to use all the
    commands on these application. By default all the command look for application
    which are under the *Applications* collection.
    """

    def __init__(self, host=None, port=None, apiRoot=None, scheme=None, apiUrl=None,
                 progressReporterCls=None):
        super(SlicerPackageClient, self).__init__(
            host=host, port=port, apiRoot=apiRoot, scheme=scheme, apiUrl=apiUrl,
            progressReporterCls=progressReporterCls)

    def createApp(self, name, desc=None, coll_id=None, coll_name=None, coll_desc=None,
                  public=None):
        """
        Create a new application in the collection which correspond to ``coll_id``,
        by default it will create the application in the collection named ``Applications``.
        The application will contain a ``draft`` folder.
        Two templates names will be set as a metadata of this new application.
        One for determine each future uploaded application package and the
        other to determine each future uploaded extension.
        It's also possible to create a new collection by specifying "coll_name".
        If this collection already exist it will use it.

        :param name: name of the new application
        :param desc: Optional description of the application
        :param coll_id: Id of an existing collection
        :param coll_name: Name of the collection
        :param coll_desc: Optional description of the new collection
        :param public: Whether the collection should be publicly visible
        :return:  The new application
        """
        apps = self.listApp(name=name)
        if apps:
            raise SlicerPackageManagerError('The Application "%s" already exist.' % name)
        return self.post('/app', parameters={
            'name': name,
            'app_description': desc,
            'collection_id': coll_id,
            'collection_name': coll_name,
            'collection_description': coll_desc,
            'public': public
        })

    def listApp(self, name=None, coll_id=None):
        """
        List all the applications within a specific collection by providing the option
        ``coll_id``. By default it will list within the collection ``Applications``.
        It can also lead to get the application by name.

        :param name: application mame
        :param coll_id: Collection ID
        :return:  A list of applications
        """
        apps = self.get('/app', parameters={
            'collection_id': coll_id,
            'name': name
        })
        return apps

    def deleteApp(self, name, coll_id=None):
        """
        Delete the application by ID.

        :param name: application name
        :param coll_id: Collection ID
        :return: The deleted application
        """
        app = self._getApp(app_name=name, coll_id=coll_id)
        self.delete('/app/%s' % app['_id'])
        return app

    def createRelease(self, app_name, name, revision, coll_id=None, desc=None):
        """
        Create a new release within the application corresponding to ``app_name``.

        :param app_name: Name of the application
        :param name: Name of the release
        :param revision: Revision of the application
        :param coll_id: Collection ID
        :param desc: Description of the release
        :return: The new release
        """
        app = self._getApp(app_name=app_name, coll_id=coll_id)
        releases = self.listRelease(app_name=app_name, name=name)
        if releases:
            raise SlicerPackageManagerError('The release "%s" already exist.' % name)
        return self.post('/app/%s/release' % app['_id'], parameters={
            'name': name,
            'app_revision': revision,
            'description': desc
        })

    def listRelease(self, app_name, name=None, coll_id=None):
        """
        List all the release within an application. It's also able to get
        one specific release by name.

        :param app_name: Name of the application
        :param name: Name of the release
        :param coll_id: Collection ID
        :return: A list of all the release within the application
        """
        app = self._getApp(app_name=app_name, coll_id=coll_id)
        if name:
            releases = self.get(
                '/app/%s/release' % app['_id'],
                parameters={'release_id_or_name': name})
        else:
            releases = self.get('/app/%s/release' % app['_id'])
        return releases

    def deleteRelease(self, app_name, name, coll_id=None):
        """
        Delete a release within an application.

        :param app_name: Name of the application
        :param name: Name of the release
        :param coll_id: Collection ID
        :return: The deleted release
        """
        app = self._getApp(app_name=app_name, coll_id=coll_id)
        release = self.listRelease(app_name, name)
        if not release:
            raise SlicerPackageManagerError('The release "%s" doesn\'t exist.' % name)
        self.delete('/app/%s/release/%s' % (app['_id'], name))
        return release

    def listDraftRelease(self, app_name, coll_id=None, revision=None, limit=Constant.DEFAULT_LIMIT, offset=0):
        """
        List the draft releases with an offset option to list only the older ones.

        By default only the first N releases are listed. Setting ``limit`` parameter to `0`
        removes this restriction.

        It's also possible to list one release within the Draft release by providing
        its specific revision.

        :param app_name: Name of the application
        :param coll_id: Collection ID
        :param revision: Revision of the release
        :param limit: Limit of the number of draft releases listed (see :const:`Constant.DEFAULT_LIMIT`)
        :param offset: offset to list only older revisions
        :return: The list of draft release
        """
        app = self._getApp(app_name=app_name, coll_id=coll_id)
        return self.get(
            '/app/%s/draft' % app['_id'],
            parameters={'revision': revision, 'limit': limit, 'offset': offset}
        )

    def deleteDraftRelease(self, app_name, revision, coll_id=None):
        """
        Delete a specific revision within the Draft release.

        :param app_name: Name of the application
        :param revision: Revision of the release
        :param coll_id: Collection ID
        :return: The deleted release
        """
        app = self._getApp(app_name=app_name, coll_id=coll_id)
        release = self.listDraftRelease(app_name, revision=revision)
        if not release:
            raise SlicerPackageManagerError(
                'The release with the revision "%s" doesn\'t exist.' % revision)
        self.delete('/app/%s/release/%s' % (app['_id'], release[0]['name']))
        return release[0]

    def uploadExtension(self, filepath, app_name, ext_os, arch, name, repo_type, repo_url,
                        revision, app_revision, desc='', icon_url='',
                        category=None, homepage='', screenshots=None, contributors=None,
                        dependency=None, coll_id=None, force=False):
        """
        Upload an extension by providing a path to the file. It can also be used to update an
        existing one, in this case the upload is done only if the extension has a different
        revision than the old one.

        :param filepath: The path to the file
        :param app_name: The name of the application
        :param ext_os: The target operating system of the package
        :param arch: The os chip architecture
        :param name: The baseName of the extension
        :param repo_type: Type of the repository
        :param repo_url: Url of the repository
        :param revision: The revision of the extension
        :param app_revision: The revision of the application supported by the extension
        :param desc: The description of the extension
        :param icon_url: Url of the extension's logo
        :param category: Category of the extension
        :param homepage: Url of the extension's homepage
        :param screenshots: Space-separate list of URLs of screenshots for the extension.
        :param contributors: List of contributors of the extension.
        :param dependency: List of the required extensions to use this one.
        :param coll_id: Collection ID
        :param force: To force update the binary file
        :return: The uploaded extension
        """
        def _displayProgress(*args, **kwargs):
            pass

        app = self._getApp(app_name=app_name, coll_id=coll_id)
        # Get potential existing extension
        extensions = self.listExtension(
            app_name,
            name=name,
            ext_os=ext_os,
            arch=arch,
            app_revision=app_revision)
        if not extensions:
            # Create the extension into Girder hierarchy
            extension = self.post('/app/%s/extension' % app['_id'], parameters={
                'os': ext_os,
                'arch': arch,
                'baseName': name,
                'repository_type': repo_type,
                'repository_url': repo_url,
                'revision': revision,
                'app_revision': app_revision,
                'description': desc,
                'icon_url': icon_url,
                'category': category,
                'homepage': homepage,
                'screenshots': screenshots,
                'contributors': contributors,
                'dependency': dependency,
            })

            # Upload the extension
            self.uploadFileToItem(
                extension['_id'],
                filepath,
                reference='',
                mimeType='application/octet-stream',
                progressCallback=_displayProgress)
        else:
            extension = extensions[0]
            # Revision different or force upload
            if revision != extension['meta']['revision'] or force:
                files = list(self.listFile(extension['_id']))
                if files:
                    oldFile = files[0]
                    filename = 'new_file'
                else:
                    filename = None

                # Upload the extension
                newFile = self.uploadFileToItem(
                    extension['_id'],
                    filepath,
                    reference='',
                    filename=filename,
                    mimeType='application/octet-stream',
                    progressCallback=_displayProgress)

                # Update the extension into Girder hierarchy
                extension = self.post('/app/%s/extension' % app['_id'], parameters={
                    'os': ext_os,
                    'arch': arch,
                    'baseName': name,
                    'repository_type': repo_type,
                    'repository_url': repo_url,
                    'revision': revision,
                    'app_revision': app_revision,
                    'description': desc,
                    'icon_url': icon_url,
                    'category': category,
                    'homepage': homepage,
                    'screenshots': screenshots,
                    'contributors': contributors,
                    'dependency': dependency,
                })

                files = list(self.listFile(extension['_id']))
                if len(files) == 2:
                    # Remove the oldFIle
                    self.delete('/file/%s' % oldFile['_id'])
                    # Change the name
                    self.put('/file/%s' % newFile['_id'], parameters={
                        'name': os.path.basename(filepath)
                    })
                    return Constant.EXTENSION_NOW_UP_TO_DATE
            else:
                return Constant.EXTENSION_AREADY_UP_TO_DATE

        return extension

    def downloadExtension(self, app_name, id_or_name, coll_id=None,
                          dir_path=Constant.CURRENT_FOLDER):
        """
        Download an extension by ID and store it in the given option ``dir_path``.
        When we use the extension id in ``id_or_name``, the parameter ``app_name`` is ignored.

        :param app_name: Name of the application
        :param id_or_name: ID or name of the extension
        :param coll_id: Collection ID
        :param dir_path: Path of the directory where the extension has to be downloaded
        :return: The downloaded extension
        """
        return self._downloadPackage('extension', app_name=app_name, id_or_name=id_or_name,
                                     dir_path=dir_path, coll_id=coll_id)

    def listExtension(self, app_name, coll_id=None, name=None, ext_os=None, arch=None,
                      app_revision=None, release=Constant.DRAFT_RELEASE_NAME,
                      limit=Constant.DEFAULT_LIMIT, all=False):
        """
        List the extensions of a specific application ``app_name``.

        By default only the first N extensions within the ``draft`` release are listed. Setting ``limit``
        parameter to `0` removes this restriction.

        Specifying optional parameters like `ext_os` or `arch` allows to return the
        corresponding subset.

        Passing ``all=True`` option allow to list all the extensions from all the
        releases of an application.

        :param app_name: Name of the application
        :param coll_id: Collection ID
        :param name: Base name of the extension
        :param ext_os: The target operating system of the package
        :param arch: The os chip architecture
        :param app_revision: Revision of the application
        :param release: Name of the release
        :param limit: Limit of the number of extensions listed (see :const:`Constant.DEFAULT_LIMIT`)
        :param all: Boolean that allow to list extensions from all the release
        :return: A list of extensions filtered by optional parameters
        """
        app = self._getApp(app_name=app_name, coll_id=coll_id)

        if all:
            release_id = None
            limit = 0
        else:
            release_folder = self.listRelease(app_name, release)
            if release_folder:
                release_id = release_folder['_id']
            else:
                raise SlicerPackageManagerError(
                    'The release "%s" doesn\'t exist.' % release)

        extensions = self.get('/app/%s/extension' % app['_id'], parameters={
            'os': ext_os,
            'arch': arch,
            'baseName': name,
            'app_revision': app_revision,
            'release_id': release_id,
            'limit': limit,
            'sort': 'created',
            'sortDir': -1
        })
        return extensions

    def deleteExtension(self, app_name, id_or_name, coll_id=None):
        """
        Delete an extension within an application.

        :param app_name: Name of the application
        :param id_or_name: Extension ID or name
        :param coll_id: Collection ID
        :return: The deleted extension
        """
        return self._deletePackage('extension', app_name, id_or_name, coll_id)

    def uploadApplicationPackage(self, filepath, app_name, pkg_os, arch, name, repo_type,
                                 repo_url, revision, version, build_date=None, coll_id=None, desc='',
                                 pre_release=False):
        """
        Upload an application package by providing a path to the file.
        It can also be used to update an existing one.

        :param filepath: The path to the file
        :param app_name: The name of the application
        :param pkg_os: The target operating system of the package
        :param arch: The os chip architecture
        :param name: The baseName of the package
        :param repo_type: Type of the repository
        :param repo_url: Url of the repository
        :param revision: The revision of the application
        :param version: The version of the application
        :param build_date: The build timestamp specified as a datetime string. Default set to current date and time.
        :param coll_id: Collection ID
        :param desc: The description of the application package
        :param pre_release: Boolean to specify if the package is ready to be distributed
        :return: The uploaded application package
        """
        def _displayProgress(*args, **kwargs):
            pass

        app = self._getApp(app_name=app_name, coll_id=coll_id)
        # Get potential existing package
        package = self.listApplicationPackage(
            app_name,
            name=name,
            pkg_os=pkg_os,
            arch=arch,
            revision=revision)
        if not package:
            # Create the package into Girder hierarchy
            parameters = {
                'os': pkg_os,
                'arch': arch,
                'baseName': name,
                'repository_type': repo_type,
                'repository_url': repo_url,
                'revision': revision,
                'version': version,
                'description': desc,
                'pre_release': pre_release
            }
            if build_date is not None:
                parameters['build_date'] = build_date
            package = self.post('/app/%s/package' % app['_id'], parameters=parameters)

            # Upload the package
            self.uploadFileToItem(
                package['_id'],
                filepath,
                reference='',
                mimeType='application/octet-stream',
                progressCallback=_displayProgress)
        else:
            package = package[0]
            # Revision different or force upload
            files = list(self.listFile(package['_id']))
            if files:
                oldFile = files[0]
                filename = 'new_file'
            else:
                filename = None

            # Upload the package
            newFile = self.uploadFileToItem(
                package['_id'],
                filepath,
                reference='',
                filename=filename,
                mimeType='application/octet-stream',
                progressCallback=_displayProgress)

            # Update the package into Girder hierarchy
            parameters = {
                'os': pkg_os,
                'arch': arch,
                'baseName': name,
                'repository_type': repo_type,
                'repository_url': repo_url,
                'revision': revision,
                'version': version,
                'description': desc
            }
            if build_date is not None:
                parameters['build_date'] = build_date
            package = self.post('/app/%s/package' % app['_id'], parameters=parameters)

            files = list(self.listFile(package['_id']))
            if len(files) == 2:
                # Remove the oldFIle
                self.delete('/file/%s' % oldFile['_id'])
                # Change the name
                self.put('/file/%s' % newFile['_id'], parameters={
                    'name': os.path.basename(filepath)
                })
                return Constant.PACKAGE_NOW_UP_TO_DATE
        return package

    def downloadApplicationPackage(self, app_name, id_or_name, coll_id=None,
                                   dir_path=Constant.CURRENT_FOLDER):
        """
        Download an application package by ID and store it in the given option ``dir_path``.
        When we use the package id in ``id_or_name``, the parameter ``app_name`` is ignored.

        :param app_name: Name of the application
        :param id_or_name: ID or name of the package
        :param coll_id: Collection ID
        :param dir_path: Path of the directory where the application package has to be downloaded
        :return: The downloaded package
        """
        return self._downloadPackage('package', app_name=app_name, id_or_name=id_or_name,
                                     dir_path=dir_path, coll_id=coll_id)

    def listApplicationPackage(self, app_name, coll_id=None, name=None, pkg_os=None, arch=None,
                               revision=None, version=None, release=None, limit=Constant.DEFAULT_LIMIT):
        """
        List the application packages filtered by some optional parameters (os, arch, ...).

        By default only the first N application packages are listed. Setting the ``limit`` parameter
        to `0` removes this restriction.

        It's also possible to specify the ``--release`` option to list all the package from a
        specific release.

        :param app_name: Name of the application
        :param coll_id: Collection ID
        :param name: Base name of the application package
        :param pkg_os: The target operating system of the package
        :param arch: The os chip architecture
        :param revision: Revision of the application
        :param version: Version of the application
        :param release: Name or ID of the release
        :param limit: Limit of the number of applications listed (see :const:`Constant.DEFAULT_LIMIT`)
        :return: A list of application package filtered by optional parameters
        """
        app = self._getApp(app_name=app_name, coll_id=coll_id)
        if release and not ObjectId.is_valid(release):
            if not self.listRelease(app_name, release):
                raise SlicerPackageManagerError(
                    'The release "%s" doesn\'t exist.' % release)

        pkg = self.get('/app/%s/package' % app['_id'], parameters={
            'os': pkg_os,
            'arch': arch,
            'baseName': name,
            'revision': revision,
            'version': version,
            'release_id_or_name': release,
            'limit': limit,
            'sort': 'created',
            'sortDir': -1
        })
        return pkg

    def deleteApplicationPackage(self, app_name, id_or_name, coll_id=None):
        """
        Delete an application package within an application.

        :param app_name: Name of the application
        :param id_or_name: Package ID or name
        :param coll_id: Collection ID
        :return: The deleted application package
        """
        return self._deletePackage(
            'package',
            app_name=app_name,
            id_or_name=id_or_name,
            coll_id=coll_id)

    # ---------------- UTILITIES ---------------- #

    def _getApp(self, app_name, coll_id=None):
        """
        Private method to get a single application by Name.

        :param app_name: Name of the application
        :param coll_id: ID of the collection that contains the application
        :return: A single application
        """
        apps = self.listApp(name=app_name, coll_id=coll_id)
        if not apps:
            raise SlicerPackageManagerError(
                'The Application "%s" doesn\'t exist.' % app_name)
        return apps[0]

    def _downloadPackage(self, package_type, app_name, id_or_name, dir_path, coll_id):
        app = self._getApp(app_name=app_name, coll_id=coll_id)

        if ObjectId.is_valid(id_or_name):
            pkg = self.get('/resource/%s' % id_or_name, parameters={'type': 'item'})
        else:
            pkg = self.get(
                '/app/%s/%s' % (app['_id'], package_type),
                parameters={'%s_name' % package_type: id_or_name})
            if pkg:
                pkg = pkg[0]
        if not pkg:
            raise SlicerPackageManagerError(
                'The %s "%s" doesn\'t exist.' % (package_type, id_or_name))
        files = self.get('/item/%s/files' % pkg['_id'])
        if not files:
            raise SlicerPackageManagerError(
                'The %s "%s" doesn\'t contain any file.' % (package_type, id_or_name))
        file = files[0]
        self.downloadFile(
            file['_id'],
            os.path.join(dir_path, '%s.%s' % (pkg['name'], file['name'].split('.')[1])))
        return pkg

    def _deletePackage(self, package_type, app_name, id_or_name, coll_id):
        app = self._getApp(app_name=app_name, coll_id=coll_id)

        if ObjectId.is_valid(id_or_name):
            pkg = self.get(
                '/app/%s/%s' % (app['_id'], package_type),
                parameters={'%s_id' % package_type: id_or_name})
        else:
            pkg = self.get(
                '/app/%s/%s' % (app['_id'], package_type),
                parameters={'%s_name' % package_type: id_or_name})
        if not pkg:
            raise SlicerPackageManagerError(
                'The %s "%s" doesn\'t exist.' % (package_type, id_or_name))
        pkg = pkg[0]
        self.delete('/app/%s/%s/%s' % (app['_id'], package_type, pkg['_id']))
        return pkg
