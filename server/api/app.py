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
##############################################################################
"""
The internal API of Slicer Extension Manager Girder plugin. Use these endpoints to
create new applications, new releases, and upload or download extensions or packages
"""
from bson.objectid import ObjectId

from girder import events
from girder.api import access
from girder.constants import TokenScope, AccessType
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource
from girder.models.file import File
from girder.models.item import Item
from girder.models.folder import Folder
from girder.models.collection import Collection
from girder.utility.progress import ProgressContext

from ..models.extension import Extension as ExtensionModel
from .. import constants


def _deleteFolder(folder, progress, user):
    with ProgressContext(progress, user=user,
                         title='Deleting folder %s' % folder['name'],
                         message='Calculating folder size...') as ctx:
        # Don't do the subtree count if we weren't asked for progress
        if progress:
            ctx.update(total=Folder().subtreeCount(folder))
        Folder().remove(folder, progress=ctx)
    return {'message': 'Deleted folder %s.' % folder['name']}


class App(Resource):
    def __init__(self):
        super(App, self).__init__()
        self.resourceName = 'app'
        self._model = Folder()

        self.route('POST', (), self.initApp)
        self.route('GET', (), self.listApp)
        self.route('DELETE', (':app_id',), self.deleteApp)
        self.route('POST', (':app_id', 'release'), self.createNewRelease)
        self.route('GET', (':app_id', 'release'), self.getAllReleases)
        self.route('GET', (':app_id', 'release', ':release_id_or_name'), self.getReleaseByIdOrName)
        self.route('DELETE', (':app_id', 'release', ':release_id_or_name'),
                   self.deleteReleaseByIdOrName)
        self.route('GET', (':app_id', 'extension'), self.getExtensions)
        self.route('GET', (':app_id', 'extension', ':extension_name'), self.getExtensionByName)
        self.route('POST', (':app_id', 'extension'), self.createOrUpdateExtension)
        self.route('DELETE', (':app_id', 'extension', ':ext_id'), self.deleteExtension)

    @autoDescribeRoute(
        Description('Create a new application.')
        .responseClass('Folder')
        .notes('If collectionId is missing or collectionName does not match an existing '
               'collection, a fresh new collection will be created with the "collection_name" '
               'given in parameters. '
               'By default the name "Applications" will be given to the collection.')
        .param('name', 'The name of the application.')
        .param('app_description', 'Application description.', required=False)
        .param('collection_id', 'The ID of the collection which contain the application',
               required=False)
        .param('collection_name', 'The Name of the collection which be created to contain'
               ' the application', required=False)
        .param('collection_description', 'Collection description.', required=False)
        .param('public', 'Whether the collection should be publicly visible.',
               required=False, dataType='boolean', default=True)
        .errorResponse('Write permission denied on the application.', 403)
    )
    @access.user(scope=TokenScope.DATA_WRITE)
    def initApp(self, name, app_description, collection_id, collection_name,
                collection_description, public):
        """
        Create the directory for start a new application. By default, without specifying
        a ``collection_id``, it will create a new collection name either ``collection_name``
        if provided, or **'Applications'**. If the collection 'Applications already exist it will
        get it.
        Return the new application (as a folder) that always contain a default
        sub-folder named 'nightly'.

        :param name: Name of the new application
        :param app_description: Description of the new application
        :param collection_id: Id of the collection within create the application
        :param collection_name: Name of the collection which will be created
        :param collection_description: Description of the new collection
        :param public: Whether the new collection should be publicly visible
        :return: The new application folder
        """
        creator = self.getCurrentUser()
        # Load or create the collection that contain the application
        if collection_id:
            collection = Collection().load(collection_id, force=True)
        elif collection_name:
            collection = list(Collection().find({'name': collection_name}, user=creator))
            if not collection:
                collection = Collection().createCollection(
                    name=collection_name,
                    description=collection_description,
                    public=public,
                    creator=creator)
            else:
                collection = collection[0]
        else:
            collection = list(Collection().find({'name': 'Applications'}, user=creator))
            if not collection:
                collection = Collection().createCollection(
                    name='Applications',
                    description=collection_description,
                    public=public,
                    creator=creator)
            else:
                collection = collection[0]
        # Create the application
        if not app_description:
            app_description = ''
        app = self._model.createFolder(
            parent=collection,
            name=name,
            description=app_description,
            parentType='Collection',
            public=public,
            creator=creator)
        # Create the 'nightly' release which will be the default folder when uploading an extension
        self._model.createFolder(
            parent=app,
            name=constants.NIGHTLY_RELEASE_NAME,
            description='Uploaded each night, always up-to-date',
            parentType='Folder',
            public=public,
            creator=creator)
        # Set a default template name for extensions in the application,
        # this can be changed in anytime.
        return self._model.setMetadata(
            app,
            {'extensionNameTemplate': constants.EXTENSION_TEMPLATE_NAME}
        )

    @autoDescribeRoute(
        Description('List existing application.')
        .responseClass('Folder', array=True)
        .param('app_id', 'The ID of the application.', required=False)
        .param('collection_id', 'The ID of the collection.', required=False)
        .param('name', 'The name of the application.', required=False)
        .param('text', 'Provide text search of the application.', required=False)
        .pagingParams(defaultSort='name')
        .errorResponse()
        .errorResponse('Read permission denied on the application.', 403)
    )
    @access.user(scope=TokenScope.DATA_READ)
    def listApp(self, app_id, collection_id, name, text, limit, offset, sort):
        """
        List existing applications base on some optional parameters.
        For searching application which aren't in the default collection (Applications),
        the parameter ``collection_id`` need to be provided.

        :param app_id: Application ID
        :param collection_id: Collection ID
        :param name: Name of the application
        :param text: Provide text search on the name of the application
        :return: List of applications
        """
        user = self.getCurrentUser()

        if ObjectId.is_valid(app_id):
            return self._model.load(app_id, user=user)
        else:
            if collection_id:
                parent = Collection().load(
                    collection_id, user=user, level=AccessType.READ, exc=True)
            else:
                parent = Collection().findOne(
                    query={'name': 'Applications'}, user=user, offset=offset)
            if parent:
                filters = {}
                if text:
                    filters['$text'] = {
                        '$search': text
                    }
                if name:
                    filters['name'] = name

                return list(self._model.childFolders(
                    parentType='collection', parent=parent, user=user,
                    offset=offset, limit=limit, sort=sort, filters=filters))
            return []

    @access.user(scope=TokenScope.DATA_WRITE)
    @autoDescribeRoute(
        Description('Delete an Application by ID.')
        .modelParam('app_id', model=Folder, level=AccessType.ADMIN)
        .param('progress', 'Whether to record progress on this task.',
               required=False, dataType='boolean', default=False)
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the application.', 403)
    )
    def deleteApp(self, folder, progress):
        """
        Delete the application by ID.

        :param id: Id of the application
        :return: Confirmation message with the deleted application name
        """
        return _deleteFolder(folder, progress, self.getCurrentUser())

    @autoDescribeRoute(
        Description('Create a new release.')
        .responseClass('Folder')
        .notes('The application\'s revision is stored as metadata of the new release.')
        .param('name', 'The release\'s name.')
        .param('app_id', 'The application\'s ID which contain the release')
        .param('app_revision', 'The application\'s revision which correspond to the release')
        .param('description', 'The application\'s description.', required=False)
        .param('public', 'Whether the release should be publicly visible.',
               required=False, dataType='boolean', default=True)
        .errorResponse()
    )
    @access.user(scope=TokenScope.DATA_WRITE)
    def createNewRelease(self, name, app_id, app_revision, description, public):
        """
        Create a new release with the ``name`` within the application. The ``app_revision``
        will permit to automatically choose this release when uploading an extension
        with a matching `app_revision`` metadata.

        :param name: Name of the new release
        :param app_id: Application ID
        :param app_revision: Revision of the application corresponding to this release
        :param description: Description of the new release
        :param public: Whether the release should be publicly visible

        :return: The new release folder
        """
        creator = self.getCurrentUser()
        application = self._model.load(app_id, user=creator)
        if not description:
            description = ''
        release = self._model.createFolder(
            parent=application,
            name=name,
            description=description,
            parentType='Folder',
            public=public,
            creator=creator)

        return self._model.setMetadata(release, {'revision': app_revision})

    @autoDescribeRoute(
        Description('Get all the releases from an application.')
        .responseClass('Folder')
        .param('app_id', 'The application\'s ID.')
        .pagingParams(defaultSort='name')
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the application.', 403)
    )
    @access.user(scope=TokenScope.DATA_READ)
    def getAllReleases(self, app_id, limit, offset, sort):
        """
        Get a list of all the release of an application.

        :param app_id: Application ID
        :return: List of all release within the application
        """
        user = self.getCurrentUser()
        application = self._model.load(app_id, user=user)
        # It returns the nightly release too
        return list(self._model.childFolders(
            application,
            'Folder',
            user=user,
            limit=limit,
            offset=offset,
            sort=sort))

    @autoDescribeRoute(
        Description('Get a particular releases by ID or name from an application.')
        .responseClass('Folder')
        .param('app_id', 'The application\'s ID.')
        .param('release_id_or_name', 'The release\'s ID or name.')
        .errorResponse('ID or name was invalid.')
        .errorResponse('Read permission denied on the application.', 403)
    )
    @access.user(scope=TokenScope.DATA_READ)
    def getReleaseByIdOrName(self, app_id, release_id_or_name):
        """
        Get the release folder by ID or by name.

        :param app_id: Application ID
        :param release_id_or_name: Could be either the release ID or the release name
        :return: The release folder
        """
        user = self.getCurrentUser()
        application = self._model.load(app_id, user=user)

        if ObjectId.is_valid(release_id_or_name):
            return self._model.load(release_id_or_name, user=user)
        release_folder = list(self._model.childFolders(
            application,
            'Folder',
            filters={'lowerName': release_id_or_name.lower()}))
        if not release_folder:
            return None
        return release_folder[0]

    @access.user(scope=TokenScope.DATA_WRITE)
    @autoDescribeRoute(
        Description('Delete a release by ID or name.')
        .modelParam('app_id', model=Folder, level=AccessType.ADMIN)
        .param('release_id_or_name', 'The release\'s ID or name.')
        .param('progress', 'Whether to record progress on this task.',
               required=False, dataType='boolean', default=False)
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the release.', 403)
    )
    def deleteReleaseByIdOrName(self, folder, release_id_or_name, progress):
        """
        Delete a release by ID or name.

        :param app_id: Application ID
        :param release_id_or_name: Could be either the release ID or the release name
        :param progress: Whether to record progress on this task
        :return: Confirmation message with the deleted release name
        """
        user = self.getCurrentUser()

        if ObjectId.is_valid(release_id_or_name):
            release = self._model.load(release_id_or_name, user=user)
        else:
            release_folder = list(self._model.childFolders(
                folder,
                'Folder',
                filters={'lowerName': release_id_or_name.lower()}))
            if not release_folder:
                raise Exception("Couldn't find release %s" % release_id_or_name)
            release = release_folder[0]

        return _deleteFolder(release, progress, self.getCurrentUser())

    @autoDescribeRoute(
        Description('List or search available extensions.')
        .responseClass('Extension')
        .param('app_id', 'The ID of the application.')
        .param('release_id', 'The release id.', required=False)
        .param('extension_id', 'The extension id.', required=False)
        .param('os', 'The target operating system of the package.',
               required=False, enum=['linux', 'win', 'macosx'])
        .param('arch', 'The os chip architecture.',
               required=False, enum=['i386', 'amd64'])
        .param('app_revision', 'The revision of the package.', required=False)
        .param('search', 'Text matched against extension name or description.', required=False)
        .pagingParams(defaultSort='created')
        .errorResponse()
    )
    @access.cookie
    @access.public
    def getExtensions(self, app_id, release_id, extension_id, os, arch, app_revision,
                      search, limit, offset, sort):
        """
        Get a list of extension which is filtered by some optional parameters:

        :param app_id: Application ID
        :param release_id: Release ID
        :param extension_id: Extension ID
        :param os: The operation system used for the extension.
        :param arch: The architecture compatible with the extension.
        :param app_revision: The revision of the application
        :param search: Text search on the name of the extension
        :return: The list of extensions
        """
        filters = {
            '$and': [
                {'meta.app_id': {'$eq': app_id}},
                {'meta.os': {'$exists': True}},
                {'meta.arch': {'$exists': True}},
                {'meta.revision': {'$exists': True}}]
        }
        if ObjectId.is_valid(extension_id):
            filters['_id'] = ObjectId(extension_id)
        if ObjectId.is_valid(release_id):
            filters['folderId'] = ObjectId(release_id)
        if os:
            filters['meta.os'] = os
        if arch:
            filters['meta.arch'] = arch
        if app_revision:
            filters['meta.revision'] = app_revision
        if search:
            # Provide a full text search on baseName
            filters['meta.baseName'] = search

        return list(ExtensionModel().find(
            query=filters,
            limit=limit,
            offset=offset,
            sort=sort))

    @autoDescribeRoute(
        Description('Get a particular extension by name from an application.')
        .responseClass('Item')
        .param('app_id', 'The application\'s ID.')
        .param('extension_name', 'The extension\'s name.')
        .errorResponse('ID or name was invalid.')
        .errorResponse('Read permission denied on the application.', 403)
    )
    @access.user(scope=TokenScope.DATA_READ)
    def getExtensionByName(self, app_id, extension_name):
        """
        Get the extension item by name.

        :param app_id: Application ID
        :param extension_name: The extension name
        :return: The extension item
        """
        user = self.getCurrentUser()
        application = self._model.load(app_id, user=user)

        release_folder = list(self._model.childFolders(
            application,
            'Folder'))
        if not release_folder:
            raise Exception('The application has no release')
        for release in release_folder:
            extensions = list(self._model.childItems(
                release,
                filters={'lowerName': extension_name.lower()}
            ))
            if extensions:
                return extensions[0]
        return None

    @autoDescribeRoute(  # noqa: C901
        Description('Create or Update an extension package.')
        .param('app_id', 'The ID of the App.')
        .param('os', 'The target operating system of the package.',
               enum=['linux', 'win', 'macosx'])
        .param('arch', 'The os chip architecture.', enum=['i386', 'amd64'])
        .param('baseName', 'The baseName of the package (ie installer baseName).')
        .param('repository_type', 'The type of the repository (svn, git).')
        .param('repository_url', 'The url of the repository.')
        .param('revision', 'The svn or git revision of the extension.')
        .param('app_revision', 'The revision of the application '
                               'that the extension was built against.')
        .param('packagetype', 'Installer, data, etc.')
        .param('codebase', 'The codebase baseName (Ex: Slicer4).')
        .param('description', 'Text describing the extension.')
        .param('release', 'Release identifier (Ex: 0.0.1, 0.0.2, 0.1).', required=False)
        .param('icon_url', 'The url of the icon for the extension.', required=False)
        .param('development_status', 'Arbitrary description of the status of the extension '
               '(stable, active, etc).', required=False)
        .param('category', 'Category under which to place the extension. Subcategories should be '
               'delimited by character. If none is passed, will render under '
               'the Miscellaneous category..', required=False)
        .param('enabled', 'Boolean indicating if the extension should be automatically enabled '
               'after its installation.', required=False)
        .param('homepage', 'The url of the extension homepage.', required=False)
        .param('screenshots', 'Space-separate list of URLs of screenshots for the extension.',
               required=False)
        .param('contributors', 'List of contributors of the extension', required=False)
        .errorResponse()
    )
    @access.cookie
    @access.public
    def createOrUpdateExtension(self, app_id, os, arch, baseName, repository_type, repository_url,
                                revision, app_revision, packagetype, codebase, description,
                                release, icon_url, development_status, category, enabled, homepage,
                                screenshots, contributors):
        """
        Upload an extension package in the database, in a specific release with providing
        ``release_id``. Or by default in the **'Nightly'** folder.

        :param app_id: The ID of the application.
        :param os: The operation system used for the extension.
        :param arch: The architecture compatible with the extension.
        :param baseName: The base name of the extension.
        :param repository_type: The type of repository (github, gitlab, ...).
        :param repository_url: The Url of the repository.
        :param revision: The revision of the extension.
        :param app_revision: The revision of the application.
        :param packagetype: Type of the extension.
        :param codebase: The codebase baseName.
        :param description: The description of the extension.
        :return: The status of the upload.
        """
        creator = self.getCurrentUser()
        application = self._model.load(app_id, user=creator)
        release_folder = None
        # Find the release by metadata revision
        releases = self._model.childFolders(application, 'Folder', user=creator)
        for folder in releases:
            if 'meta' in folder:
                if folder['meta']['revision'] == app_revision:
                    release_folder = folder
                    break
        if not release_folder:
            # Only the nightly folder in the list
            release_folder = list(self._model.childFolders(
                application,
                'Folder',
                user=creator,
                filters={'name': constants.NIGHTLY_RELEASE_NAME}))
            if not release_folder:
                raise Exception('The %s folder not found.' % constants.NIGHTLY_RELEASE_NAME)
            release_folder = release_folder[0]

        params = {
            'app_id': app_id,
            'baseName': baseName,
            'os': os,
            'arch': arch,
            'repository_type': repository_type,
            'repository_url': repository_url,
            'revision': revision,
            'app_revision': app_revision,
            'packagetype': packagetype,
            'codebase': codebase,
            'description': description
        }
        if release:
            params['release'] = release
        if icon_url:
            params['icon_url'] = icon_url
        if development_status:
            params['development_status'] = development_status
        if category:
            params['category'] = category
        if enabled:
            params['enabled'] = enabled
        if homepage:
            params['homepage'] = homepage
        if screenshots:
            params['screenshots'] = screenshots
        if contributors:
            params['contributors'] = contributors

        name = application['meta']['extensionNameTemplate'].format(**params)
        filters = {
            'name': name
        }
        # Only one extensions should be in this list
        extensions = list(ExtensionModel().get(release_folder, filters=filters))
        if not len(extensions):
            # The extension doesn't exist yet:
            extension = ExtensionModel().createExtension(name, creator, release_folder, params)
        elif len(extensions) == 1:
            extension = extensions[0]
        else:
            raise Exception('Too many extensions found for the same name :"%s"' % name)

        # Check the file inside the extension Item
        files = Item().childFiles(extension)
        if files.count() == 1:
            old_file = files.next()
            # catch the event of upload success and remove the file
            events.bind('model.file.finalizeUpload.after', 'application', File().remove(old_file))
        elif not files.count():
            # Extension new or empty
            pass
        else:
            raise Exception("More than 1 binary file in the extension.")

        old_meta = {
            'baseName': extension['meta']['baseName'],
            'os': extension['meta']['os'],
            'arch': extension['meta']['arch'],
            'revision': extension['meta']['revision'],
            'app_revision': extension['meta']['app_revision']
        }
        identifier_meta = {
            'baseName': baseName,
            'os': os,
            'arch': arch,
            'revision': revision,
            'app_revision': app_revision
        }
        if identifier_meta == old_meta and len(extensions):
            # The revision is the same than these before, no need to upload
            extension = ExtensionModel().setMetadata(extension, params)
            events.unbind('model.file.finalizeUpload.after', 'application')

        # Ready to upload the binary file
        return extension

    @access.user(scope=TokenScope.DATA_WRITE)
    @autoDescribeRoute(
        Description('Delete an Extension by ID.')
        .param('app_id', 'The ID of the App.')
        .modelParam('ext_id', model=Item, level=AccessType.WRITE)
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the extension.', 403)
    )
    def deleteExtension(self, app_id, item):
        """
        Delete the extension by ID.

        :param app_id: Application ID
        :param ext_id: Extension ID
        :return: Confirmation message with the name of the deleted extension
        """
        Item().remove(item)
        return {'message': 'Deleted extension %s.' % item['name']}
