"""
The internal server API of Slicer Package Manager. Use these endpoints to
create new applications, new releases, and upload or download application and extensions
packages.
"""
import datetime
import re

from bson.objectid import ObjectId

from girder.api import access
from girder.constants import TokenScope, AccessType, SortDir
from girder.api.describe import Description, autoDescribeRoute
from girder.api.rest import Resource
from girder.exceptions import RestException
from girder.models.folder import Folder
from girder.models.collection import Collection
from girder.utility import parseTimestamp

from ..models.extension import Extension as ExtensionModel
from ..models.package import Package as PackageModel
from .. import constants
from .. import utilities


class App(Resource):
    def __init__(self):
        super(App, self).__init__()
        self.resourceName = 'app'
        self._model = Folder()

        self.route('POST', (), self.initApp)
        self.route('GET', (), self.listApp)
        self.route('DELETE', (':app_id',), self.deleteApp)
        self.route('GET', (':app_id', 'downloadstats'), self.getDownloadStats)
        self.route('POST', (':app_id', 'release'), self.createNewRelease)
        self.route('GET', (':app_id', 'release'), self.getReleases)
        self.route('DELETE', (':app_id', 'release', ':release_id_or_name'),
                   self.deleteReleaseByIdOrName)
        self.route('POST', (':app_id', 'extension'), self.createOrUpdateExtension)
        self.route('GET', (':app_id', 'extension'), self.getExtensions)
        self.route('DELETE', (':app_id', 'extension', ':ext_id'), self.deleteExtension)
        self.route('POST', (':app_id', 'package'), self.createOrUpdatePackage)
        self.route('GET', (':app_id', 'package'), self.getPackages)
        self.route('DELETE', (':app_id', 'package', ':pkg_id'), self.deletePackage)
        self.route('GET', (':app_id', 'draft'), self.getAllDraftReleases)

    @autoDescribeRoute(
        Description('Create a new application.')
        .responseClass('Folder')
        .notes('If collectionId is missing or collectionName does not match an existing '
               'collection, a fresh new collection will be created with the "collection_name" '
               'given in parameters.<br/>'
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
        sub-folder named 'draft'.

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
        # Load or create the top_level_folder
        top_level_folder = list(self._model.childFolders(
            parent=collection,
            parentType='Collection',
            user=creator,
            filters={'name': constants.TOP_LEVEL_FOLDER_NAME}))
        if top_level_folder:
            top_level_folder = top_level_folder[0]
        else:
            # Create the 'package' folder
            top_level_folder = self._model.createFolder(
                parent=collection,
                name=constants.TOP_LEVEL_FOLDER_NAME,
                description='',
                parentType='Collection',
                public=public,
                creator=creator)

        # Create the application
        if not app_description:
            app_description = ''
        app = self._model.createFolder(
            parent=top_level_folder,
            name=name,
            description=app_description,
            parentType='Folder',
            public=public,
            creator=creator)
        # Create the 'draft' release which will be the default folder when uploading an extension
        self._model.createFolder(
            parent=app,
            name=constants.DRAFT_RELEASE_NAME,
            description='Uploaded each night, always up-to-date',
            parentType='Folder',
            public=public,
            creator=creator)
        # Set a default template name for extensions in the application,
        # this can be changed in anytime.
        return self._model.setMetadata(
            app,
            {
                'applicationPackageNameTemplate': constants.APPLICATION_PACKAGE_TEMPLATE_NAME,
                'extensionPackageNameTemplate': constants.EXTENSION_PACKAGE_TEMPLATE_NAME
            }
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
    @access.public(scope=TokenScope.DATA_READ)
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
            return self._model.load(app_id, user=user, level=AccessType.READ)
        else:
            if collection_id:
                parent = Collection().load(
                    collection_id, user=user, level=AccessType.READ, exc=True)
            else:
                parent = Collection().findOne(
                    query={'name': 'Applications'}, user=user, offset=offset)
            if parent:
                top_folder_name = list(self._model.childFolders(
                    parentType='collection', parent=parent, user=user,
                    filters={'name': constants.TOP_LEVEL_FOLDER_NAME}))
                if top_folder_name:
                    top_folder_name = top_folder_name[0]
                else:
                    return []
                filters = {}
                if text:
                    filters['$text'] = {
                        '$search': text
                    }
                if name:
                    filters['name'] = name

                return list(self._model.childFolders(
                    parentType='Folder', parent=top_folder_name, user=user,
                    offset=offset, limit=limit, sort=sort, filters=filters))
            return []

    @access.user(scope=TokenScope.DATA_WRITE)
    @autoDescribeRoute(
        Description('Delete an Application by ID.')
        .modelParam('app_id', destName='app_folder', model=Folder, level=AccessType.ADMIN)
        .param('progress', 'Whether to record progress on this task.',
               required=False, dataType='boolean', default=False)
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the application.', 403)
    )
    def deleteApp(self, app_folder, progress):
        """
        Delete an application by ID.

        :param app_folder: Application folder loaded using ``app_id`` route parameter.
        :return: Confirmation message with the deleted application name
        """
        return utilities.deleteFolder(app_folder, progress, self.getCurrentUser())

    @autoDescribeRoute(
        Description('Create a new release.')
        .responseClass('Folder')
        .notes("The application's revision is stored as metadata of the new release.")
        .param('name', "The release's name.")
        .param('app_id', "The application's ID which contain the release", paramType='path')
        .param('app_revision', "The application's revision which correspond to the release")
        .param('description', "The application's description.", required=False)
        .param('public', 'Whether the release should be publicly visible.',
               required=False, dataType='boolean', default=True)
        .errorResponse()
    )
    @access.user(scope=TokenScope.DATA_WRITE)
    def createNewRelease(self, name, app_id, app_revision, description, public):
        """
        Create a new release with the ``name`` within the application. The ``app_revision``
        will be used to automatically choose this release when uploading an application or
        extension package with a matching application revision metadata.

        :param name: Name of the new release
        :param app_id: Application ID
        :param app_revision: Revision of the application corresponding to this release
        :param description: Description of the new release
        :param public: Whether the release should be publicly visible

        :return: The new release folder
        """
        creator = self.getCurrentUser()
        application = self._model.load(app_id, user=creator, level=AccessType.READ)
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
        .param('app_id', "The application's ID.", paramType='path')
        .param('release_id_or_name', "The release's ID or name.", required=False)
        .pagingParams(defaultSort='created', defaultSortDir=SortDir.DESCENDING)
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the application.', 403)
    )
    @access.public(scope=TokenScope.DATA_READ)
    def getReleases(self, app_id, release_id_or_name, limit, offset, sort):
        """
        Get a list of all the stable release of an application. You can also search
        for a specific release if you provide the ``release_id_or_name`` parameter.
        If the ``release_id_or_name`` parameter doesn't correspond to any existing
        release, this will just return ``None``.

        :param app_id: Application ID
        :param release_id_or_name: Could be either the release ID or the release name
        :return: List of all release within the application or a specific release folder
        """
        user = self.getCurrentUser()
        application = self._model.load(app_id, user=user, level=AccessType.READ)

        if ObjectId.is_valid(release_id_or_name):
            return self._model.load(release_id_or_name, user=user, level=AccessType.READ)
        elif release_id_or_name:
            release_folder = list(self._model.childFolders(
                application,
                'Folder',
                user=user,
                filters={'lowerName': release_id_or_name.lower()}))
            if not release_folder:
                return None
            else:
                return release_folder[0]
        filters = {
            'name': {'$ne': constants.DRAFT_RELEASE_NAME}
        }
        return list(self._model.childFolders(
            application,
            'Folder',
            user=user,
            limit=limit,
            offset=offset,
            sort=sort,
            filters=filters))

    @autoDescribeRoute(
        Description('Get all the draft releases from an application.')
        .responseClass('Folder')
        .param('app_id', "The application's ID.", paramType='path')
        .param('revision', 'The revision of a draft release', required=False)
        .pagingParams(defaultSort='created', defaultSortDir=SortDir.DESCENDING)
        .errorResponse('ID was invalid.')
        .errorResponse('Read permission denied on the application.', 403)
    )
    @access.public(scope=TokenScope.DATA_READ)
    def getAllDraftReleases(self, app_id, revision, limit, offset, sort):
        """
        Get a list of all the draft release of an application. It's also
        possible to filter this list by the metadata ``revision``.

        :param app_id: Application ID
        :param revision: Revision of one of the draft release
        :return: List of all release within the application
        """
        user = self.getCurrentUser()
        application = self._model.load(app_id, user=user, level=AccessType.READ)

        filters = {
            'name': constants.DRAFT_RELEASE_NAME
        }
        release = list(self._model.childFolders(
            application,
            'Folder',
            user=user,
            filters=filters))
        if not release:
            raise RestException('There is no %s release in this application.'
                                % constants.DRAFT_RELEASE_NAME)
        release = release[0]
        draft_filters = {'meta.revision': {'$exists': True}}
        if revision:
            draft_filters = {'meta.revision': revision}
        return list(self._model.childFolders(
            release,
            'Folder',
            user=user,
            filters=draft_filters,
            limit=limit,
            offset=offset,
            sort=sort))

    @access.user(scope=TokenScope.DATA_WRITE)
    @autoDescribeRoute(
        Description('Delete a release by ID or name.')
        .modelParam('app_id', destName='app_folder', model=Folder, level=AccessType.ADMIN)
        .param('release_id_or_name', "The release's ID or name.", paramType='path')
        .param('progress', 'Whether to record progress on this task.',
               required=False, dataType='boolean', default=False)
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the release.', 403)
    )
    def deleteReleaseByIdOrName(self, app_folder, release_id_or_name, progress):
        """
        Delete a release by ID or name.

        :param app_folder: Application folder loaded using ``app_id`` route parameter.
        :param release_id_or_name: Could be either the release ID or the release name
        :param progress: Whether to record progress on this task
        :return: Confirmation message with the deleted release name
        """
        user = self.getCurrentUser()

        if ObjectId.is_valid(release_id_or_name):
            release = self._model.load(release_id_or_name, user=user)
        else:
            release_folder = list(self._model.childFolders(
                app_folder,
                'Folder',
                user=user,
                filters={'lowerName': release_id_or_name.lower()}))
            if not release_folder:
                release_folder = list(self._model.childFolders(
                    app_folder,
                    'Folder',
                    user=user,
                    filters={'lowerName': constants.DRAFT_RELEASE_NAME.lower()}))
                if not release_folder:
                    raise RestException("Couldn't find release %s" % release_id_or_name)
                revision_folder = list(self._model.childFolders(
                    release_folder[0],
                    'Folder',
                    user=user,
                    filters={'lowerName': release_id_or_name.lower()}
                ))
                if not revision_folder:
                    raise RestException("Couldn't find release %s" % release_id_or_name)
                release = revision_folder[0]
            else:
                release = release_folder[0]

        return utilities.deleteFolder(release, progress, self.getCurrentUser())

    @autoDescribeRoute(  # noqa: C901
        Description('List or search available extensions.')
        .notes('If the "release_id" provided correspond to the "draft" release,'
               ' then you must provide the "app_revision" to use this parameters. '
               'If not, it will just be ignored.')
        .responseClass('Extension')
        .param('app_id', 'The ID of the application.', paramType='path')
        .param('extension_name', 'The name of the extension.', required=False)
        .param('release_id', 'The release id.', required=False)
        .param('extension_id', 'The extension id.', required=False)
        .param('os', 'The target operating system of the package.',
               required=False, enum=['linux', 'win', 'macosx'])
        .param('arch', 'The os chip architecture.',
               required=False, enum=['i386', 'amd64'])
        .param('app_revision', 'The revision of the application.', required=False)
        .param('baseName', 'The baseName of the extension', required=False)
        .param('q', 'The search query.', required=False)
        .pagingParams(defaultSort='created', defaultSortDir=SortDir.DESCENDING)
        .errorResponse()
    )
    @access.public(scope=TokenScope.DATA_READ)
    def getExtensions(self, app_id, extension_name, release_id, extension_id, os, arch,
                      app_revision, baseName, q, limit, sort, offset=0):
        """
        Get a list of extension which is filtered by some optional parameters. If the ``release_id``
        provided correspond to the draft release, then you must provide the app_revision to use
        this parameters. If not, it will just be ignored.

        :param app_id: Application ID
        :param extension_name: Extension name
        :param release_id: Release ID
        :param extension_id: Extension ID
        :param os: The operation system used for the extension.
        :param arch: The architecture compatible with the extension.
        :param app_revision: The revision of the application
        :param baseName: The baseName of the extension
        :param q: Text expected to be found in the extension name or description
        :return: The list of extensions
        """
        user = self.getCurrentUser()
        utilities.checkAccess(app_id, user)
        filters = {
            '$and': [
                {'meta.app_id': {'$eq': app_id}},
                {'meta.os': {'$exists': True}},
                {'meta.arch': {'$exists': True}},
                {'meta.app_revision': {'$exists': True}}]
        }
        if extension_name:
            filters['lowerName'] = extension_name.lower()
        if ObjectId.is_valid(extension_id):
            filters['_id'] = ObjectId(extension_id)
        if os:
            filters['meta.os'] = os
        if arch:
            filters['meta.arch'] = arch
        if app_revision:
            filters['meta.app_revision'] = app_revision
        if baseName:
            # Provide a exact match base on baseName
            filters['meta.baseName'] = baseName
        if q:
            escaped_query = re.escape(q)
            filters['$or'] = [
                {'meta.baseName': {'$regex': escaped_query, '$options': 'i'}},
                {'meta.description': {'$regex': escaped_query, '$options': 'i'}}
            ]
        if ObjectId.is_valid(release_id):
            release = self._model.load(release_id, user=user, level=AccessType.READ)
            if release['name'] == constants.DRAFT_RELEASE_NAME:
                if app_revision:
                    revisions = list(self._model.childFolders(
                        release,
                        'Folder',
                        user=user,
                        filters={'meta.revision': app_revision}))
                    if revisions:
                        extensions_folder = list(self._model.childFolders(
                            revisions[0],
                            'Folder',
                            user=user,
                            filters={'name': constants.EXTENSIONS_FOLDER_NAME}))
                        if extensions_folder:
                            filters['folderId'] = ObjectId(extensions_folder[0]['_id'])
                else:
                    revisions = self._model.childFolders(
                        release,
                        'Folder',
                        user=user,
                        sort=sort)
                    extensions = []
                    limit_tmp = limit
                    for revision in revisions:
                        extensions_folder = list(self._model.childFolders(
                            revision,
                            'Folder',
                            user=user,
                            filters={'name': constants.EXTENSIONS_FOLDER_NAME}))
                        # If the 'extensions' directory is not here, there are no extensions to list
                        if not extensions_folder:
                            continue
                        extensions_folder = extensions_folder[0]
                        filters['folderId'] = ObjectId(extensions_folder['_id'])
                        extensions += list(ExtensionModel().find(
                            query=filters,
                            limit=limit_tmp,
                            offset=offset,
                            sort=sort))
                        limit_tmp = limit - len(extensions)
                        if limit_tmp <= 0:
                            break
                    return extensions
            else:
                extensions_folder = list(self._model.childFolders(
                    release,
                    'Folder',
                    user=user,
                    filters={'name': constants.EXTENSIONS_FOLDER_NAME}))
                # If the 'extensions' directory is not here, there are no extensions to list
                if not extensions_folder:
                    return []
                extensions_folder = extensions_folder[0]
                filters['folderId'] = ObjectId(extensions_folder['_id'])
        return list(ExtensionModel().find(
            query=filters,
            limit=limit,
            offset=offset,
            sort=sort))

    @autoDescribeRoute(  # noqa: 901
        Description('Create or Update an extension package.')
        .param('app_id', 'The ID of the App.', paramType='path')
        .param('os', 'The target operating system of the package.',
               enum=['linux', 'win', 'macosx'])
        .param('arch', 'The os chip architecture.', enum=['i386', 'amd64'])
        .param('baseName', 'The baseName of the package (ie installer baseName).')
        .param('repository_type', 'The type of the repository (svn, git).')
        .param('repository_url', 'The url of the repository.')
        .param('revision', 'The svn or git revision of the extension.')
        .param('app_revision', 'The revision of the application '
                               'that the extension was built against.')
        .param('description', 'Text describing the extension.')
        .param('icon_url', 'The url of the icon for the extension.', required=False)
        .param('category', 'Category under which to place the extension. Subcategories should be '
               'delimited by character. If none is passed, will render under '
               'the Miscellaneous category..', required=False)

        .param('homepage', 'The url of the extension homepage.', required=False)
        .param('screenshots', 'Space-separate list of URLs of screenshots for the extension.',
               required=False)
        .param('contributors', 'List of contributors of the extension.', required=False)
        .param('dependency', 'List of the required extensions to use this one.', required=False)
        .param('license', 'The license short description of the extension.', required=False)
        .param('development_status', 'Arbitrary description of the status of the extension '
               '(stable, active, etc).', required=False)
        .param('enabled', 'Boolean indicating if the extension should be automatically enabled '
               'after its installation.', required=False)
        .errorResponse()
    )
    @access.user(scope=TokenScope.DATA_WRITE)
    def createOrUpdateExtension(self, app_id, os, arch, baseName, repository_type, repository_url,
                                revision, app_revision, description,
                                icon_url, development_status, category, enabled, homepage,
                                screenshots, contributors, dependency, license):
        """
        Create or update an extension item.

        If a release identified by ``app_revision`` exists, it is used to create or lookup
        the corresponding release folder. Otherwise, a **draft** sub-folder named after
        ``app_revision`` is either used or created.

        If an extension with matching metadata ``meta.baseName``, ``meta.os``, ``meta.arch`` and
        ``meta.app_revision`` is found, the extension name and other metadata are updated.

        :param app_id: The ID of the application.
        :param os: The operation system used for the extension.
        :param arch: The architecture compatible with the extension.
        :param baseName: The base name of the extension.
        :param repository_type: The type of repository (github, gitlab, ...).
        :param repository_url: The Url of the repository.
        :param revision: The revision of the extension.
        :param app_revision: The revision of the application.
        :param description: The description of the extension.
        :return: The created/updated extension.
        """
        creator = self.getCurrentUser()
        application = Folder().load(app_id, user=creator)
        release_folder = utilities.getOrCreateReleaseFolder(
            application=application,
            user=creator,
            app_revision=app_revision)

        extensions_folder = list(self._model.childFolders(
            release_folder,
            'Folder',
            user=creator,
            filters={'name': constants.EXTENSIONS_FOLDER_NAME}))
        if not extensions_folder:
            extensions_folder = self._model.createFolder(
                parent=release_folder,
                name=constants.EXTENSIONS_FOLDER_NAME,
                parentType='Folder',
                public=release_folder['public'],
                description='This directory contains all the extensions packages',
                creator=creator)
        else:
            extensions_folder = extensions_folder[0]

        params = {
            'app_id': app_id,
            'baseName': baseName,
            'os': os,
            'arch': arch,
            'repository_type': repository_type,
            'repository_url': repository_url,
            'revision': revision,
            'app_revision': app_revision,
            'description': description
        }
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
        if dependency:
            params['dependency'] = dependency
        if license:
            params['license'] = license

        name = application['meta']['extensionPackageNameTemplate'].format(**params)
        filters = {
            'meta.baseName': baseName,
            'meta.os': os,
            'meta.arch': arch,
            'meta.app_revision': app_revision
        }
        # Only one extensions should be in this list
        extensions = list(ExtensionModel().get(extensions_folder, filters=filters))
        if not len(extensions):
            # The extension doesn't exist yet:
            extension = ExtensionModel().createExtension(name, creator, extensions_folder, params)
        elif len(extensions) == 1:
            # The extension already exist
            extension = extensions[0]
            # Check the file inside the extension Item
            files = ExtensionModel().childFiles(extension)
            if not files.count():
                # Extension empty
                raise RestException("Extension existing without any binary file.")

            # Update the extension
            extension['name'] = name
            extension = ExtensionModel().setMetadata(extension, params)
        else:
            raise RestException('Too many extensions found for the same name :"%s"' % name)

        # Ready to upload the binary file
        return extension

    @autoDescribeRoute(
        Description('Delete an Extension by ID.')
        .param('app_id', 'The ID of the App.', paramType='path')
        .modelParam('ext_id', destName='ext_model', model=ExtensionModel, level=AccessType.WRITE)
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the extension.', 403)
    )
    @access.user(scope=TokenScope.DATA_WRITE)
    def deleteExtension(self, app_id, ext_model):
        """
        Delete an extension by ID.

        :param app_id: Application ID
        :param ext_model: Extension model loaded using ``ext_id`` route parameter.
        :return: The deleted extension
        """
        ExtensionModel().remove(ext_model)
        return ext_model

    @autoDescribeRoute(
        Description('List or search available packages.')
        .notes('If the "release_id" provided correspond to the "draft" release,'
               ' then you must provide the "revision" to use this parameters. '
               'If not, it will just be ignored.')
        .responseClass('Package')
        .param('app_id', 'The ID of the application.', paramType='path')
        .param('package_name', 'The name of the package.', required=False)
        .param('release_id_or_name', "The release's ID or name", required=False)
        .param('package_id', 'The package id.', required=False)
        .param('os', 'The target operating system of the package.',
               required=False, enum=['linux', 'win', 'macosx'])
        .param('arch', 'The os chip architecture.',
               required=False, enum=['i386', 'amd64'])
        .param('revision', 'The revision of the application.', required=False)
        .param('baseName', 'The baseName of the package', required=False)
        .pagingParams(defaultSort='created', defaultSortDir=SortDir.DESCENDING)
        .errorResponse()
    )
    @access.public(scope=TokenScope.DATA_READ)
    def getPackages(self, app_id, package_name, release_id_or_name, package_id, os, arch,
                    revision, baseName, limit, offset, sort):
        """
        Get a list of package which is filtered by some optional parameters. If the ``release_id``
        provided correspond to the draft release, then you must provide the revision to use
        this parameters. If not, it will just be ignored.

        :param app_id: Application ID
        :param package_name: Package name
        :param release_id_or_name: Could be either the release ID or the release name
        :param package_id: Package ID
        :param os: The operation system used for the application package.
        :param arch: The architecture compatible with the application package.
        :param revision: The revision of the application
        :param baseName: The baseName of the package
        :return: The list of application packages
        """
        user = self.getCurrentUser()
        filters = {
            '$and': [
                {'meta.app_id': {'$eq': app_id}},
                {'meta.os': {'$exists': True}},
                {'meta.arch': {'$exists': True}},
                {'meta.revision': {'$exists': True}},
                {'meta.app_revision': {'$exists': False}}]
        }
        if package_name:
            filters['lowerName'] = package_name.lower()
        if ObjectId.is_valid(package_id):
            filters['_id'] = ObjectId(package_id)
        if os:
            filters['meta.os'] = os
        if arch:
            filters['meta.arch'] = arch
        if revision:
            filters['meta.revision'] = revision
        if baseName:
            # Provide a exact match base on baseName
            filters['meta.baseName'] = baseName

        release = None
        if ObjectId.is_valid(release_id_or_name):
            release = self._model.load(release_id_or_name, user=user, level=AccessType.READ)
        elif release_id_or_name:
            application = self._model.load(app_id, user=user, level=AccessType.READ)
            release_folder = list(self._model.childFolders(
                application,
                'Folder',
                user=user,
                filters={'lowerName': release_id_or_name.lower()}))
            if len(release_folder) > 0:
                release = release_folder[0]

        if release is not None:
            if release['name'] == constants.DRAFT_RELEASE_NAME:
                if revision:
                    revisions = list(self._model.childFolders(
                        release,
                        'Folder',
                        user=user,
                        filters={'meta.revision': revision}))
                    if revisions:
                        filters['folderId'] = ObjectId(revisions[0]['_id'])
                else:
                    revisions = self._model.childFolders(release, 'Folder', user=user)
                    packages = []
                    limit_tmp = limit
                    for rev in revisions:
                        filters['folderId'] = ObjectId(rev['_id'])
                        packages += list(PackageModel().find(
                            query=filters,
                            limit=limit_tmp,
                            offset=offset,
                            sort=sort))
                        if limit == 0:
                            continue
                        limit_tmp = limit - len(packages)
                        if limit_tmp <= 0:
                            break
                    return packages
            else:
                filters['folderId'] = ObjectId(release['_id'])

        return list(PackageModel().find(
            query=filters,
            limit=limit,
            offset=offset,
            sort=sort))

    @autoDescribeRoute(
        Description('Create or Update an application package.')
        .param('app_id', 'The ID of the App.', paramType='path')
        .param('os', 'The target operating system of the package.',
               enum=['linux', 'win', 'macosx'])
        .param('arch', 'The os chip architecture.', enum=['i386', 'amd64'])
        .param('baseName', 'The baseName of the package (ie installer baseName).')
        .param('repository_type', 'The type of the repository (svn, git).')
        .param('repository_url', 'The url of the repository.')
        .param('revision', 'The revision of the application')
        .param('version', 'The version of the application')
        .param('description', 'Text describing the package.', required=False)
        .param('pre_release', 'Boolean to specify if the package is a full release ready to be distributed.',
               dataType='boolean', required=False)
        .param('build_date', 'Build timestamp specified as a datetime string. Default set to current date and time.',
               required=False)
        .errorResponse()
    )
    @access.user(scope=TokenScope.DATA_WRITE)
    def createOrUpdatePackage(self, app_id, os, arch, baseName, repository_type, repository_url,
                              revision, version, description, pre_release, build_date):
        """
        Create or update a package item.

        If a release identified by ``revision`` exists, it is used to create or lookup
        the corresponding release folder. Otherwise, a **draft** sub-folder named after
        ``revision`` is either used or created.

        If a package with matching metadata ``meta.baseName``, ``meta.os``, ``meta.arch`` and
        ``meta.revision`` is found, the package name and other metadata are updated.

        :param app_id: The ID of the application.
        :param os: The operation system used for the package.
        :param arch: The architecture compatible with the application package.
        :param baseName: The base name of the package.
        :param repository_type: The type of repository (github, gitlab, ...).
        :param repository_url: The Url of the repository.
        :param revision: The revision of the application.
        :param version: The version of the application.
        :param description: Description of the application package
        :param pre_release: Boolean to specify if the package is a full release ready to be distributed
        :param build_date: The build timestamp specified as datetime string. Default set to current date and time.
        :return: The created/updated package.
        """
        creator = self.getCurrentUser()
        application = Folder().load(app_id, user=creator)
        release_folder = utilities.getOrCreateReleaseFolder(
            application=application,
            user=creator,
            app_revision=revision)

        if not build_date:
            build_date = datetime.datetime.utcnow()
        else:
            try:
                build_date = parseTimestamp(build_date)
            except ValueError:
                raise RestException('Parameter "build_date" is incorrectly formatted.')

        params = {
            'app_id': app_id,
            'baseName': baseName,
            'os': os,
            'arch': arch,
            'repository_type': repository_type,
            'repository_url': repository_url,
            'revision': revision,
            'version': version,
            'pre_release': pre_release,
            'build_date': build_date
        }

        name = application['meta']['applicationPackageNameTemplate'].format(**params)
        filters = {
            'meta.baseName': baseName,
            'meta.os': os,
            'meta.arch': arch,
            'meta.revision': revision
        }
        # Only one package should be in this list
        package = list(PackageModel().get(release_folder, filters=filters))
        if not len(package):
            # The package doesn't exist yet:
            package = PackageModel().createPackage(name, creator, release_folder, params,
                                                   description)
        elif len(package) == 1:
            # The package already exist
            package = package[0]
            # Check the file inside the application package
            files = PackageModel().childFiles(package)
            if not files.count():
                # Package empty
                raise RestException("Application Package existing without any binary file.")
            # Update the package
            package['name'] = name
            package = PackageModel().setMetadata(package, params)
        else:
            raise RestException('Too many packages found for the same name :"%s"' % name)

        # Ready to upload the binary file
        return package

    @autoDescribeRoute(
        Description('Delete a Package by ID.')
        .param('app_id', 'The ID of the App.', paramType='path')
        .modelParam('pkg_id', destName='pkg_model', model=PackageModel, level=AccessType.WRITE)
        .errorResponse('ID was invalid.')
        .errorResponse('Admin access was denied for the package.', 403)
    )
    @access.user(scope=TokenScope.DATA_WRITE)
    def deletePackage(self, app_id, pkg_model):
        """
        Delete an application package by ID.

        :param app_id: Application ID
        :param pkg_model: Package model loaded using ``pkg_id`` route parameter.
        :return: The deleted package
        """
        PackageModel().remove(pkg_model)
        return pkg_model

    @autoDescribeRoute(
        Description('Get download stats of application and extensions packages '
                    'within an application.')
        .param('app_id', 'The ID of the application.', paramType='path')
        .errorResponse()
    )
    @access.public(scope=TokenScope.DATA_READ)
    def getDownloadStats(self, app_id):
        """
        Get all the download count of all the application and extension packages
        from an application.

        :param app_id: Application ID
        :return: The JSON document of all the download statistics
        """
        user = self.getCurrentUser()
        application = self._model.load(app_id, user=user, level=AccessType.READ)
        releases = self._model.childFolders(application, 'Folder', user=user)

        downloadStats = {}

        for release in releases:
            if 'meta' in release and 'downloadStats' in release['meta']:
                if release['name'] == constants.DRAFT_RELEASE_NAME:
                    downloadStats.update(release['meta']['downloadStats'])
                else:
                    try:
                        downloadStats[release['meta']['revision']].update(
                            release['meta']['downloadStats'])
                    except KeyError:
                        downloadStats[
                            release['meta']['revision']] = release['meta']['downloadStats']

        return downloadStats
