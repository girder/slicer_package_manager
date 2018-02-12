#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################
import os as OS
from bson.objectid import ObjectId

from girder_client import GirderClient

__version__ = '0.0.1'
__license__ = 'Apache 2.0'

appName = 'Slicer'


class Constant:
    # Errors
    ERROR_ALREADY_EXIST = 1
    ERROR_APP_NOT_EXIST = 2
    ERROR_RELEASE_NOT_EXIST = 3
    ERROR_EXT_NOT_EXIST = 4
    ERROR_EXT_NO_FILE = 5

    # Default
    # TODO: Find a good default path
    DEFAULT_DOWNLOAD_PATH = '/Users/pierre.assemat/slicer-extension-manager/extensions'
    DEFAULT_RELEASE = 'Nightly'
    DEFAULT_LIMIT = 50


class SlicerExtensionClient(GirderClient):
    """
    The SlicerExtensionClient allow to us the GirderClient with specific functions to use the
    slicer_extension_manager plugin of Girder. This allow to manage 3 top level entity:
    - Application
    - Release
    - Extension

    To know more about the it : TODO: LINK to README
    """

    def __init__(self, host=None, port=None, apiRoot=None, scheme=None, apiUrl=None,
                 progressReporterCls=None):
        super(SlicerExtensionClient, self).__init__(
            host=host, port=port, apiRoot=apiRoot, scheme=scheme, apiUrl=apiUrl,
            progressReporterCls=progressReporterCls)

    def createApp(self, name, desc=None):
        """
        Create a new application in the default collection 'Applications'.
        The application will contain a 'Nightly' folder.
        A template of the name of each future uploaded extension will be set as a metadata of
        this new application.
        :param name: name of the new application
        :param desc: Optional description of the application
        :return Return the fresh new application
        """
        apps = self.listApp(name=name)
        if apps:
            return Constant.ERROR_ALREADY_EXIST
        return self.post('/app', parameters={
            'name': name,
            'app_description': desc
        })

    def listApp(self, name=None):
        """
        1. List all the applications within the default collection 'Applications'.
        2. Get the application by name.
        :param name: application mame
        :return Return a list of applications
        """
        apps = self.get('/app', parameters={
            'name': name
        })
        return apps

    def deleteApp(self, name):
        """
        Delete the application by ID.
        :param name: application name
        :return Return the deleted application
        """
        apps = self.listApp(name=name)
        if not apps:
            return Constant.ERROR_APP_NOT_EXIST
        app = apps[0]
        self.delete('/app/%s' % app['_id'])
        return app

    def createRelease(self, app_name, name, revision, desc=None):
        """
        Create a new release within the application corresponding to 'app_name'.
        :param app_name: Name of the application
        :param name: Name of the release
        :param revision: Revision of the application
        :param desc: Description of the release
        :return: Return the new release
        """
        apps = self.listApp(app_name)
        if not apps:
            return Constant.ERROR_APP_NOT_EXIST
        app = apps[0]

        releases = self.listRelease(app_name=app_name)
        for release in releases:
            if release['name'] == name:
                return Constant.ERROR_ALREADY_EXIST
        return self.post('/app/%s/release' % app['_id'], parameters={
            'name': name,
            'app_revision': revision,
            'description': desc
        })

    def listRelease(self, app_name, name=None):
        """
        1. List all the release within an application.
        2. Get the release by name.
        :param app_name: Name of the application
        :param name: Name of the release
        :return: Return a list of all the release within the application
        """
        apps = self.listApp(app_name)
        if not apps:
            return Constant.ERROR_APP_NOT_EXIST
        app = apps[0]
        if name:
            releases = self.get('/app/%s/release/%s' % (app['_id'], name))
        else:
            releases = self.get('/app/%s/release' % app['_id'])
        return releases

    def deleteRelease(self, app_name, name):
        """
        Delete a release within an application.
        :param app_name: Name of the application
        :param name: Name of the release
        :return: Return the deleted release
        """
        apps = self.listApp(app_name)
        if not apps:
            return Constant.ERROR_APP_NOT_EXIST
        app = apps[0]
        release = self.listRelease(app_name, name)
        if not release:
            return Constant.ERROR_RELEASE_NOT_EXIST
        self.delete('/app/%s/release/%s' % (app['_id'], name))
        return release

    def uploadExtension(self, filepath, app_name, os, arch, name, repo_type, repo_url, revision, app_revision,
                        packagetype, codebase, desc):
        """
        Upload an extension by providing a path to the file.
        :param filepath: The path to the file
        :param app_name: The name of the application
        :param os: The target operating system of the package
        :param arch: The os chip architecture
        :param name: The basename of the extension
        :param repo_type:
        :param repo_url:
        :param revision: The revision of the extension
        :param app_revision: The revision of the application supported by the extension
        :param packagetype:
        :param codebase:
        :param desc: The description of the extension
        :return: Return the uploaded extension
        """
        apps = self.listApp(app_name)
        if not apps:
            return Constant.ERROR_APP_NOT_EXIST
        app = apps[0]

        # Create the extension into Girder hierarchy
        extension = self.post('/app/%s/extension' % app['_id'], parameters={
            'os': os,
            'arch': arch,
            'baseName': name,
            'repository_type': repo_type,
            'repository_url': repo_url,
            'revision': revision,
            'app_revision': app_revision,
            'packagetype': packagetype,
            'codebase': codebase,
            'description': desc
        })

        # Upload the extension
        def _displayProgress(*args, **kwargs):
            pass

        filename = OS.path.basename(filepath)  # extract full name of file
        self.uploadFileToItem(
            extension['_id'],
            filepath,
            reference='',
            mimeType='application/octet-stream',
            filename=filename,
            progressCallback=_displayProgress)

        return extension

    def downloadExtension(self, ext_id, dir_path=Constant.DEFAULT_DOWNLOAD_PATH):
        """
        Download an extension by ID and store it in the given option 'dir_path'.
        :param ext_id: ID of the extension
        :param dir_path: Path of the directory when the extension has to be downloaded
        :return: Return the downloaded extension
        """
        ext = self.get('/item/%s' % ObjectId(ext_id))
        if not ext:
            return Constant.ERROR_EXT_NOT_EXIST
        files = self.get('/item/%s/files' % ObjectId(ext_id))
        if not files:
            return Constant.ERROR_EXT_NO_FILE
        file = files[0]
        self.downloadFile(file['_id'], OS.path.join(dir_path, '%s.%s' % (ext['name'], file['name'].split('.')[1])))
        return ext

    def listExtension(self, app_name, os, arch, app_revision, release=Constant.DEFAULT_RELEASE,
                      limit=Constant.DEFAULT_LIMIT, all=False):
        """
        List all the extension for a specific release and filter them with some option (os, arch, ...).
        By default the extensions within 'Nightly' release are listed. It's also possible to specify the '--all'
        option to list all the extensions from all the release of an application.
        :param app_name: Name of the application
        :param os: The target operating system of the package
        :param arch: The os chip architecture
        :param app_revision:
        :param release: Name of the release
        :param limit: Limit of the number of extensions listed
        :param all: Boolean that allow to list extensions from all the release
        :return: Return a list of extensions filtered by optional parameters
        """
        apps = self.listApp(app_name)
        if not apps:
            return Constant.ERROR_APP_NOT_EXIST
        app = apps[0]

        if all:
            release_id = None
        else:
            release_folder = self.listRelease(app_name, release)
            if release_folder:
                release_id = release_folder['_id']
            else:
                return Constant.ERROR_RELEASE_NOT_EXIST

        extensions = self.get('/app/%s/extension' % app['_id'], parameters={
            'os': os,
            'arch': arch,
            'app_revision': app_revision,
            'release_id': release_id,
            'limit': limit,
            'sort': 'created',
            'sortDir': -1
        })
        return extensions
