# -*- coding: utf-8 -*-

from bson.objectid import ObjectId
import hashlib
import os
import six

from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.file import File
from girder.models.user import User

from server import constants
from . import utile

from tests import base


def setUpModule():
    base.enabledPlugins.append('slicer_package_manager')
    base.startServer()


def tearDownModule():
    base.stopServer()


class SlicerPackageManagerTest(base.TestCase):

    def setUp(self):
        super(SlicerPackageManagerTest, self).setUp()

        self.maxDiff = None
        self._MAX_CHUNK_SIZE = 1024 * 1024 * 64

        self.dataDir = os.path.join(
            os.environ['GIRDER_TEST_DATA_PREFIX'], 'plugins', 'slicer_package_manager')

        self._user = User().createUser('usr0', 'passwd', 'tst', 'usr', 'u@u.com')
        self._collection = Collection().createCollection(
            'testCollection',
            creator=self._user,
            description='Contain applications')
        self._packages = Folder().createFolder(
            parent=self._collection,
            name=constants.TOP_LEVEL_FOLDER_NAME,
            parentType='Collection',
            public=True,
            creator=self._user)
        self._app = Folder().createFolder(
            parent=self._packages,
            name='application',
            description='app description',
            parentType='Folder',
            public=True,
            creator=self._user)
        self._app = Folder().setMetadata(
            self._app,
            {
                'applicationPackageNameTemplate': constants.APPLICATION_PACKAGE_TEMPLATE_NAME,
                'extensionPackageNameTemplate': constants.EXTENSION_PACKAGE_TEMPLATE_NAME
            }
        )
        self._draftRelease = Folder().createFolder(
            parent=self._app,
            name=constants.DRAFT_RELEASE_NAME,
            description='Uploaded each night, always up-to-date',
            parentType='Folder',
            public=True,
            creator=self._user)
        self._draftRevision = Folder().createFolder(
            parent=self._draftRelease,
            name='0000',
            parentType='Folder',
            public=True,
            creator=self._user)
        self._draftRevision = Folder().setMetadata(
            self._draftRevision,
            {'revision': '0000'}
        )
        self._release = Folder().createFolder(
            parent=self._app,
            name='release1',
            description='release description',
            parentType='Folder',
            public=True,
            creator=self._user)
        self._release = Folder().setMetadata(self._release, {'revision': '0005'})
        self._extensions = utile.extensions
        self._extensions['extension1']['name'] = constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(
            **self._extensions['extension1']['meta'])
        self._extensions['extension2']['name'] = constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(
            **self._extensions['extension2']['meta'])
        self._extensions['extension3']['name'] = constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(
            **self._extensions['extension3']['meta'])
        self._extensions['extension4']['name'] = constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(
            **self._extensions['extension4']['meta'])
        self._extensions['extension5']['name'] = constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(
            **self._extensions['extension5']['meta'])
        self._packages = utile.packages
        self._packages['package1']['name'] = constants.APPLICATION_PACKAGE_TEMPLATE_NAME.format(
            **self._packages['package1']['meta'])
        self._packages['package2']['name'] = constants.APPLICATION_PACKAGE_TEMPLATE_NAME.format(
            **self._packages['package2']['meta'])
        self._packages['package3']['name'] = constants.APPLICATION_PACKAGE_TEMPLATE_NAME.format(
            **self._packages['package3']['meta'])

    def testInitApp(self):
        # Without any collection this should create the new 'Applications' collection
        self._createApplicationCheck(
            'App_test',
            'Application without specifying any collection',
            collDescription='Automatic creation of the collection Applications')
        # Without any collection this should load the 'Applications' collection
        self._createApplicationCheck(
            'App_test1',
            'Application without specifying any collection')
        # With a collection ID this should load the collection
        self._createApplicationCheck(
            'App_test2',
            'Application with a collection ID',
            collId=self._collection['_id'])
        # With a collection name that match an existing collection name
        self._createApplicationCheck(
            'App_test3',
            'Application with a collection name',
            collName=self._collection['name'])
        # With a collection name that does not exist yet
        self._createApplicationCheck(
            'App_test4',
            'Application with a collection name',
            collName='Collection_for_app')

    def testlistApp(self):
        # Create applications in the 'Applications' collection
        app1 = self._createApplicationCheck(
            'App_test1',
            'Application without specifying any collection',
            collDescription='Automatic creation of the collection Applications')
        app2 = self._createApplicationCheck(
            'App_test2',
            'Application without specifying any collection',
            collDescription='Automatic creation of the collection Applications')
        # Get application with application ID
        resp = self.request(
            path='/app',
            method='GET',
            user=self._user,
            params={'app_id': self._app['_id']}
        )
        self.assertStatusOk(resp)
        self.assertEqual(ObjectId(resp.json['_id']), self._app['_id'])
        self.assertEqual(resp.json['name'], self._app['name'])
        self.assertEqual(resp.json['description'], self._app['description'])
        self.assertEqual(
            resp.json['meta']['applicationPackageNameTemplate'],
            constants.APPLICATION_PACKAGE_TEMPLATE_NAME)
        self.assertEqual(
            resp.json['meta']['extensionPackageNameTemplate'],
            constants.EXTENSION_PACKAGE_TEMPLATE_NAME)
        # List all applications from 'Applications' collection (Default)
        resp = self.request(
            path='/app',
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 2)
        self.assertEqual(resp.json[0]['_id'], app1['_id'])
        self.assertEqual(resp.json[1]['_id'], app2['_id'])
        # Get application with exact name
        resp = self.request(
            path='/app',
            method='GET',
            user=self._user,
            params={
                'collection_id': self._collection['_id'],
                'name': self._app['name']}
        )
        self.assertStatusOk(resp)
        self.assertEqual(ObjectId(resp.json[0]['_id']), self._app['_id'])
        self.assertEqual(resp.json[0]['name'], self._app['name'])
        self.assertEqual(resp.json[0]['description'], self._app['description'])
        self.assertEqual(
            resp.json[0]['meta']['applicationPackageNameTemplate'],
            constants.APPLICATION_PACKAGE_TEMPLATE_NAME)
        self.assertEqual(
            resp.json[0]['meta']['extensionPackageNameTemplate'],
            constants.EXTENSION_PACKAGE_TEMPLATE_NAME)

    def testDeleteApp(self):
        # Create the application without any collection,
        # this should create the new 'Applications' collection
        app = self._createApplicationCheck(
            'App_test',
            'Application without specifying any collection',
            collDescription='Automatic creation of the collection Applications')
        # Get the new application by ID
        resp = self.request(
            path='/app',
            method='GET',
            user=self._user,
            params={'app_id': app['_id']}
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['_id'], app['_id'])
        self.assertEqual(resp.json['name'], app['name'])
        # Delete the application
        resp = self.request(
            path='/app/%s' % app['_id'],
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['_id'], app['_id'])
        # Try to get the application should failed
        resp = self.request(
            path='/app',
            method='GET',
            user=self._user,
            params={'app_id': app['_id']}
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json, None)

    def testNewRelease(self):
        self._createReleaseCheck(
            name='V3.2.1',
            app_id=self._app['_id'],
            app_revision='001',
            desc='This is a new release')

    def testGetRelease(self):
        release1 = self._createReleaseCheck(
            name='V3.2.1',
            app_id=self._app['_id'],
            app_revision='002',
            desc='This is a new release')

        resp = self.request(
            path='/app/%s/release' % self._app['_id'],
            method='GET',
            user=self._user
        )
        # Check if it has return all the stable releases
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 2)
        self.assertEqual(resp.json[0]['_id'], release1['_id'])
        self.assertEqual(ObjectId(resp.json[1]['_id']), self._release['_id'])

        # Get one release by ID
        resp = self.request(
            path='/app/%s/release' % self._app['_id'],
            params={'release_id_or_name': self._release['_id']},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], self._release['name'])
        self.assertEqual(resp.json['description'], self._release['description'])
        self.assertEqual(ObjectId(resp.json['_id']), self._release['_id'])

        # Get one release by name
        resp = self.request(
            path='/app/%s/release' % self._app['_id'],
            params={'release_id_or_name': self._release['name']},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], self._release['name'])
        self.assertEqual(resp.json['description'], self._release['description'])
        self.assertEqual(ObjectId(resp.json['_id']), self._release['_id'])

        resp = self.request(
            path='/app/%s/release' % self._app['_id'],
            params={'release_id_or_name': constants.DRAFT_RELEASE_NAME},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], constants.DRAFT_RELEASE_NAME)
        self.assertEqual(ObjectId(resp.json['_id']), self._draftRelease['_id'])

    def testGetAllDraftRelease(self):
        resp = self.request(
            path='/app/%s/draft' % self._app['_id'],
            method='GET',
            user=self._user
        )
        # Check if it has return all the revision from the default release
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(ObjectId(resp.json[0]['_id']), self._draftRevision['_id'])
        self.assertEqual(
            resp.json[0]['meta']['revision'],
            self._draftRevision['meta']['revision'])
        # With the parameter 'revision'
        resp = self.request(
            path='/app/%s/draft' % self._app['_id'],
            method='GET',
            user=self._user,
            params={'revision': self._draftRevision['meta']['revision']}
        )
        # Check if it has return the good revision from the draft folder
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(ObjectId(resp.json[0]['_id']), self._draftRevision['_id'])
        self.assertEqual(
            resp.json[0]['meta']['revision'],
            self._draftRevision['meta']['revision'])
        # With the parameter 'revision' set to a wrong value
        resp = self.request(
            path='/app/%s/draft' % self._app['_id'],
            method='GET',
            user=self._user,
            params={'revision': 'wrongRev'}
        )
        # Check if it has return the good revision from the draft folder
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 0)

    def testDeleteReleaseByID(self):
        self._deleteRelease('_id')

    def testDeleteReleaseByName(self):
        self._deleteRelease('name')

    def testDeleteRevisionRelease(self):
        # Create extensions in the "draft" release
        extension1 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension3']['meta'],
            'extension3.tar.gz')
        self.assertEqual(extension1['name'], self._extensions['extension3']['name'])
        extension2 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension4']['meta'],
            'extension4.tar.gz')
        self.assertEqual(extension2['name'], self._extensions['extension4']['name'])

        resp = self.request(
            path='/app/%s/draft' % self._app['_id'],
            method='GET',
            user=self._user
        )
        # Check if it has return all the revision from the default release
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 2)

        # Delete by Name the revision release '0001' in the "draft" release
        resp = self.request(
            path='/app/%s/release/%s' %
                 (self._app['_id'], self._extensions['extension4']['meta']['app_revision']),
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)

        resp = self.request(
            path='/app/%s/draft' % self._app['_id'],
            method='GET',
            user=self._user
        )
        # Check if it has return all the revision from the default release
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)

    def testUploadAndDownloadExtension(self):
        # Create a new extension in the release "self._release"
        extension1 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension1']['meta'],
            'extension1.tar.gz')
        self.assertEqual(extension1['name'], self._extensions['extension1']['name'])
        extensions_folder = Folder().load(extension1['folderId'], user=self._user)
        self.assertEqual(ObjectId(extensions_folder['parentId']), self._release['_id'])
        # Create an other extension in the "draft" release
        extension2 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension2']['meta'],
            'extension2.tar.gz')
        self.assertEqual(extension2['name'], self._extensions['extension2']['name'])
        # Create a third extension in the "draft" release
        extension3 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension3']['meta'],
            'extension3.tar.gz')
        self.assertEqual(extension3['name'], self._extensions['extension3']['name'])
        # Try to create the same extension should just get the same one
        extension3 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension3']['meta'],
            'extension3.tar.gz')
        self.assertEqual(extension3['name'], self._extensions['extension3']['name'])

    def testUpdateExtensions(self):
        extension = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension2']['meta'],
            'extension2.tar.gz')
        self.assertEqual(extension['name'], self._extensions['extension2']['name'])
        # Update the same extension
        newParams = self._extensions['extension2']['meta'].copy()
        newParams.update({
            'revision': '0000',
            'repository_type': 'gitlab',
            'packagetype': 'zip',
            'codebase': 'SL434334',
            'description': 'Extension for Slicer 4 new version 2'
        })
        updatedExtension = self._createOrUpdatePackage('extension', newParams)
        # Check the same extension has different metadata
        self.assertEqual(updatedExtension['_id'], extension['_id'])
        self.assertEqual(
            updatedExtension['name'],
            constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(**newParams)
        )
        self.assertNotEqual(updatedExtension['meta'], extension['meta'])

    def testGetExtensions(self):
        # Create a new extension in the release "self._release"
        extension1 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension1']['meta'])
        self.assertEqual(extension1['name'], self._extensions['extension1']['name'])
        extensions_folder = Folder().load(extension1['folderId'], user=self._user)
        self.assertEqual(ObjectId(extensions_folder['parentId']), self._release['_id'])
        # Create other extensions in the "draft" release
        extension2 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension2']['meta'])
        self.assertEqual(extension2['name'], self._extensions['extension2']['name'])
        extension3 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension3']['meta'])
        self.assertEqual(extension3['name'], self._extensions['extension3']['name'])
        # Get all the extension of the application
        resp = self.request(
            path='/app/%s/extension' % self._app['_id'],
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 3)
        # Get all the extension of the application for Linux
        resp = self.request(
            path='/app/%s/extension' % self._app['_id'],
            method='GET',
            user=self._user,
            params={
                'os': 'linux'
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 2)
        for ext in resp.json:
            self.assertEqual(ext['meta']['os'], 'linux')
        # Get all the extension of the application for Linux and amd64 architecture
        resp = self.request(
            path='/app/%s/extension' % self._app['_id'],
            method='GET',
            user=self._user,
            params={
                'os': 'linux',
                'arch': 'amd64'
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)
        for ext in resp.json:
            self.assertEqual(ext['meta']['os'], 'linux')
            self.assertEqual(ext['meta']['arch'], 'amd64')
        # Get all the extension of the application which are in "release1"
        resp = self.request(
            path='/app/%s/extension' % self._app['_id'],
            method='GET',
            user=self._user,
            params={
                'release_id': self._release['_id']
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)
        # Get all the extension of the application which are in the draft release
        draftRelease = list(Folder().childFolders(
            self._app,
            'Folder',
            user=self._user,
            filters={'name': constants.DRAFT_RELEASE_NAME}))
        resp = self.request(
            path='/app/%s/extension' % self._app['_id'],
            method='GET',
            user=self._user,
            params={
                'release_id': draftRelease[0]['_id']
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 2)
        # Get a specific extension by name
        resp = self.request(
            path='/app/%s/extension' % self._app['_id'],
            params={'extension_name': extension3['name']},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json[0]['_id'], extension3['_id'])
        self.assertEqual(resp.json[0]['name'], extension3['name'])
        # Get a specific extension with wrong name
        resp = self.request(
            path='/app/%s/extension' % self._app['_id'],
            params={'extension_name': 'wrong_name'},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 0)
        self.assertEqual(resp.json, [])

    def testDeleteExtensionPackages(self):
        # Create a new extension in the release "self._release"
        extension = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension1']['meta'])
        self.assertEqual(extension['name'], self._extensions['extension1']['name'])
        extensions_folder = Folder().load(extension['folderId'], user=self._user)
        self.assertEqual(ObjectId(extensions_folder['parentId']), self._release['_id'])
        # Get, delete, and try to re-get the package
        self._deletePackages('extension', extension)

    def testUploadAndDownloadPackages(self):
        # Create a new application package in the release "self._release"
        package1 = self._createOrUpdatePackage(
            'package',
            self._packages['package1']['meta'],
            'pkg1.dmg')
        self.assertEqual(package1['name'], self._packages['package1']['name'])
        self.assertEqual(ObjectId(package1['folderId']), self._release['_id'])
        # Create an other application package in the "draft" release
        package2 = self._createOrUpdatePackage(
            'package',
            self._packages['package2']['meta'],
            'pkg2.exe')
        self.assertEqual(package2['name'], self._packages['package2']['name'])
        # Create a third application package in the "draft" release
        package3 = self._createOrUpdatePackage(
            'package',
            self._packages['package3']['meta'],
            'pkg3.tar.gz')
        self.assertEqual(package3['name'], self._packages['package3']['name'])
        # Try to create the same application package should just get the same one
        package3 = self._createOrUpdatePackage(
            'package',
            self._packages['package3']['meta'],
            'pkg3.tar.gz')
        self.assertEqual(package3['name'], self._packages['package3']['name'])

    def testUpdatePackages(self):
        package = self._createOrUpdatePackage(
            'package',
            self._packages['package2']['meta'],
            'pkg2.exe')
        self.assertEqual(package['name'], self._packages['package2']['name'])
        # Update the same package
        newParams = self._packages['package2']['meta'].copy()
        newParams.update({
            'repository_url': 'https://AnotherURL.com',
            'repository_type': 'gitlab',
        })
        updatedPackage = self._createOrUpdatePackage('package', newParams)
        # Check the same package has different metadata
        self.assertEqual(updatedPackage['_id'], package['_id'])
        self.assertEqual(
            updatedPackage['name'],
            constants.APPLICATION_PACKAGE_TEMPLATE_NAME.format(**newParams)
        )
        self.assertNotEqual(updatedPackage['meta'], package['meta'])

    def testGetPackages(self):
        # Create a new application package in the release "self._release"
        package1 = self._createOrUpdatePackage(
            'package',
            self._packages['package1']['meta'],
            'pkg1.dmg')
        self.assertEqual(package1['name'], self._packages['package1']['name'])
        self.assertEqual(ObjectId(package1['folderId']), self._release['_id'])
        # Create an other application package in the "draft" release
        package2 = self._createOrUpdatePackage(
            'package',
            self._packages['package2']['meta'],
            'pkg2.exe')
        self.assertEqual(package2['name'], self._packages['package2']['name'])
        # Create a third application package in the "draft" release
        package3 = self._createOrUpdatePackage(
            'package',
            self._packages['package3']['meta'],
            'pkg3.tar.gz')
        self.assertEqual(package3['name'], self._packages['package3']['name'])
        # Get all the package of the application
        resp = self.request(
            path='/app/%s/package' % self._app['_id'],
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 3)
        # Get all the package of the application for Linux
        resp = self.request(
            path='/app/%s/package' % self._app['_id'],
            method='GET',
            user=self._user,
            params={
                'os': 'linux'
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(resp.json[0]['meta']['os'], 'linux')
        # Get all the package of the application for Linux and amd64 architecture
        resp = self.request(
            path='/app/%s/package' % self._app['_id'],
            method='GET',
            user=self._user,
            params={
                'os': 'macosx',
                'arch': 'i386'
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 0)
        # Get all the package of the application which are in "release1"
        resp = self.request(
            path='/app/%s/package' % self._app['_id'],
            method='GET',
            user=self._user,
            params={
                'release_id': self._release['_id']
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)
        # Get all the package of the application which are in the draft release
        draftRelease = list(Folder().childFolders(
            self._app,
            'Folder',
            user=self._user,
            filters={'name': constants.DRAFT_RELEASE_NAME}))
        resp = self.request(
            path='/app/%s/package' % self._app['_id'],
            method='GET',
            user=self._user,
            params={
                'release_id': draftRelease[0]['_id']
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 2)
        # Get a specific package by name
        resp = self.request(
            path='/app/%s/package' % self._app['_id'],
            params={'package_name': package3['name']},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json[0]['_id'], package3['_id'])
        self.assertEqual(resp.json[0]['name'], package3['name'])
        # Get a specific extension with wrong name
        resp = self.request(
            path='/app/%s/package' % self._app['_id'],
            params={'package_name': 'wrong_name'},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 0)
        self.assertEqual(resp.json, [])

    def testDeleteApplicationPackages(self):
        # Create a new application package in the release "self._release"
        package = self._createOrUpdatePackage(
            'package',
            self._packages['package1']['meta'])
        self.assertEqual(package['name'], self._packages['package1']['name'])
        self.assertEqual(ObjectId(package['folderId']), self._release['_id'])
        # Get, delete, and try to re-get the package
        self._deletePackages('package', package)

    def testDownloadStats(self):
        extension1 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension1']['meta'],
            'extension1.tar.gz')
        self.assertEqual(extension1['name'], self._extensions['extension1']['name'])
        extension2 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension2']['meta'],
            'extension2.tar.gz')
        self.assertEqual(extension2['name'], self._extensions['extension2']['name'])
        extension3 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension3']['meta'],
            'extension3.tar.gz')
        self.assertEqual(extension3['name'], self._extensions['extension3']['name'])
        extension4 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension4']['meta'],
            'extension4.tar.gz')
        self.assertEqual(extension4['name'], self._extensions['extension4']['name'])
        extension5 = self._createOrUpdatePackage(
            'extension',
            self._extensions['extension5']['meta'],
            'extension5.tar.gz')
        self.assertEqual(extension5['name'], self._extensions['extension5']['name'])
        package1 = self._createOrUpdatePackage(
            'package',
            self._packages['package1']['meta'],
            'pkg1.dmg')
        self.assertEqual(package1['name'], self._packages['package1']['name'])
        package2 = self._createOrUpdatePackage(
            'package',
            self._packages['package2']['meta'],
            'pkg2.exe')
        self.assertEqual(package2['name'], self._packages['package2']['name'])
        package3 = self._createOrUpdatePackage(
            'package',
            self._packages['package3']['meta'],
            'pkg3.tar.gz')
        self.assertEqual(package3['name'], self._packages['package3']['name'])

        # Get the downloadStats
        expectedStats = utile.expectedDownloadStats
        resp = self.request(
            path='/app/%s/downloadstats' % self._app['_id'],
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertDictEqual(resp.json, expectedStats)

        # Download multiple time an extension
        ext4_file = list(File().find({'itemId': ObjectId(extension4['_id'])}))
        ext5_file = list(File().find({'itemId': ObjectId(extension5['_id'])}))

        N = 5
        for idx in range(N):
            self._downloadFile(ext4_file[0]['_id'])
            self._downloadFile(ext5_file[0]['_id'])

        expectedStats['0001']['extensions']['Ext3']['macosx'].update({
            'amd64': N + expectedStats['0001']['extensions']['Ext3']['macosx']['amd64'],
            'i386': N + expectedStats['0001']['extensions']['Ext3']['macosx']['i386']
        })
        resp = self.request(
            path='/app/%s/downloadstats' % self._app['_id'],
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertDictEqual(resp.json, expectedStats)

        # The download stats aren't affected by deletion of extension or revision
        # in the default release
        # Delete extensions
        resp = self.request(
            path='/app/%(app_id)s/extension/%(ext_id)s' % {
                'app_id': self._app['_id'],
                'ext_id': extension4['_id']},
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        resp = self.request(
            path='/app/%(app_id)s/extension/%(ext_id)s' % {
                'app_id': self._app['_id'],
                'ext_id': extension5['_id']},
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        # Delete the revision '0000' in the "draft" release
        resp = self.request(
            path='/app/%(app_id)s/release/%(release_id)s' % {
                'app_id': self._app['_id'],
                'release_id': self._draftRevision['_id']},
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        # Check if download Stats are the same
        resp = self.request(
            path='/app/%s/downloadstats' % self._app['_id'],
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertDictEqual(resp.json, expectedStats)

    # ************************ UTILITIES ************************ #

    def _createApplicationCheck(self, appName, appDescription, collId=None,
                                collName=None, collDescription=''):
        params = {
            'name': appName,
            'app_description': appDescription,
            'collection_description': collDescription
        }
        if not (collId or collName):
            collName = 'Applications'
            params.update({'collection_name': collName})
        elif collId:
            if not ObjectId.is_valid(collId):
                raise Exception("The ObjectId %s is not valid" % collId)
            params.update({'collection_id': collId})
            collection = Collection().load(collId, user=self._user)
            collName = collection['name']
        else:
            params.update({'collection_name': collName})

        resp = self.request(
            path='/app',
            method='POST',
            user=self._user,
            params=params
        )
        # Check if it has created the application
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], appName)
        self.assertEqual(resp.json['description'], appDescription)
        self.assertEqual(
            resp.json['meta']['applicationPackageNameTemplate'],
            constants.APPLICATION_PACKAGE_TEMPLATE_NAME)
        self.assertEqual(
            resp.json['meta']['extensionPackageNameTemplate'],
            constants.EXTENSION_PACKAGE_TEMPLATE_NAME)
        # Check if it has created/load the collection
        topLevelFolder = Folder().load(resp.json['parentId'], user=self._user)
        collection = Collection().load(topLevelFolder['parentId'], user=self._user)
        self.assertEqual(collection['name'], collName)
        if collDescription:
            self.assertEqual(collection['description'], collDescription)
        # Check if it has created the "draft" release
        parent = Folder().load(resp.json['_id'], user=self._user)
        draft = list(Folder().childFolders(parent, 'Folder', user=self._user))
        self.assertEqual(len(draft), 1)
        self.assertEqual(draft[0]['name'], constants.DRAFT_RELEASE_NAME)
        self.assertEqual(draft[0]['description'], 'Uploaded each night, always up-to-date')

        return resp.json

    def _createReleaseCheck(self, name, app_id, app_revision, desc=''):
        resp = self.request(
            path='/app/%s/release' % app_id,
            method='POST',
            user=self._user,
            params={
                'name': name,
                'app_revision': app_revision,
                'description': desc
            }
        )
        # Check if it has created the new release
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], name)
        self.assertEqual(resp.json['description'], desc)
        self.assertEqual(resp.json['meta']['revision'], app_revision)
        return resp.json

    def _deleteRelease(self, identifier):
        # Create the release
        release = self._createReleaseCheck(
            name='V3.2.1',
            app_id=self._app['_id'],
            app_revision='001',
            desc='This is a new release')
        # Get the new release by name
        resp = self.request(
            path='/app/%s/release' % self._app['_id'],
            params={'release_id_or_name': release[identifier]},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['_id'], release['_id'])
        self.assertEqual(resp.json['name'], release['name'])
        # Delete the release by name
        resp = self.request(
            path='/app/%(app_id)s/release/%(id_or_name)s' % {
                'app_id': self._app['_id'],
                'id_or_name': release[identifier]},
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['_id'], release['_id'])
        # Try to get the release should failed
        resp = self.request(
            path='/app/%s/release' % self._app['_id'],
            params={'release_id_or_name': release[identifier]},
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json, None)

    def _uploadExternalData(self, item, filePath, fileName=None):
        file = os.path.join(self.dataDir, filePath)
        size = os.path.getsize(file)
        offset = 0
        if fileName is None:
            fileName = filePath

        # Initialize the upload
        resp = self.request(
            path='/file', method='POST', user=self._user, params={
                'parentType': 'item',
                'parentId': item['_id'],
                'name': fileName,
                'size': size,
                'mimeType': 'application/octet-stream'
            })
        self.assertStatusOk(resp)
        uploadId = resp.json['_id']

        # Upload content
        with open(file, 'rb') as fp:
            while True:
                chunk = fp.read(min(self._MAX_CHUNK_SIZE, (size - offset)))
                if not chunk:
                    break
                if isinstance(chunk, six.text_type):
                    chunk = chunk.encode('utf8')
                resp = self.request(
                    path='/file/chunk',
                    method='POST',
                    user=self._user,
                    params={
                        'offset': offset,
                        'uploadId': uploadId
                    },
                    body=chunk,
                    type='application/octet-stream'
                )
                self.assertStatusOk(resp)
                offset += len(chunk)

            uploadedFile = resp.json
            self.assertHasKeys(uploadedFile, ['itemId'])
            self.assertEqual(uploadedFile['assetstoreId'], str(self.assetstore['_id']))
            self.assertEqual(uploadedFile['name'], filePath)
            self.assertEqual(uploadedFile['size'], size)
        return uploadedFile

    def _downloadFile(self, id):
        resp = self.request(
            path='/file/%s/download' % id,
            method='GET',
            user=self._user,
            isJson=False)
        self.assertStatusOk(resp)
        return self.getBody(resp, text=False)

    def _getSha512(self, file):
        sha512 = hashlib.sha512()
        sha512.update(file)
        return sha512.hexdigest()

    def _createOrUpdatePackage(self, packageType, params, filePath=None):
        resp = self.request(
            path='/app/%s/%s' % (self._app['_id'], packageType),
            method='POST',
            user=self._user,
            params=params)
        self.assertStatusOk(resp)
        # Remove the app_id to check the metadata with these set during the creation
        metadata = resp.json['meta'].copy()
        metadata.pop('app_id')
        self.assertDictEqual(metadata, params)
        if filePath:
            # Upload a package file
            file = os.path.join(self.dataDir, filePath)
            with open(file, 'rb') as fp:
                file_sha = self._getSha512(fp.read())
            uploadedfile = self._uploadExternalData(resp.json, filePath)

            # Download the extension and compare files
            self.assertEqual(
                self._getSha512(self._downloadFile(uploadedfile['_id'])),
                file_sha
            )
        return resp.json

    def _deletePackages(self, packageType, pkg):
        # Get all the  application package, this should only be the new one
        resp = self.request(
            path='/app/%s/%s' % (self._app['_id'], packageType),
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)
        self.assertEqual(resp.json[0]['_id'], pkg['_id'])
        # Delete the package
        resp = self.request(
            path='/app/%(app_id)s/%(type)s/%(pkg_id)s' % {
                'app_id': self._app['_id'],
                'type': packageType,
                'pkg_id': pkg['_id']},
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['_id'], pkg['_id'])
        # Try to get the package shouldn't success
        resp = self.request(
            path='/app/%s/%s' % (self._app['_id'], packageType),
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 0)
