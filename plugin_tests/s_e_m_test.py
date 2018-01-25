from bson.objectid import ObjectId
import hashlib
import os
import six

from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.user import User

from server import constants

from tests import base


def setUpModule():
    base.enabledPlugins.append('slicer-extension-manager')
    base.startServer()


def tearDownModule():
    base.stopServer()


class SlicerExtensionManagerTest(base.TestCase):

    def setUp(self):
        super(SlicerExtensionManagerTest, self).setUp()

        self.maxDiff = None
        self._MAX_CHUNK_SIZE = 1024 * 1024 * 64
        self._extensionNameTemplate = '{baseName}_{arch}_{os}_{revision}'

        self.dataDir = os.path.join(
            os.environ['GIRDER_TEST_DATA_PREFIX'], 'plugins', 'slicer-extension-manager')

        self._user = User().createUser('usr0', 'passwd', 'tst', 'usr', 'u@u.com')
        self._collection = Collection().createCollection(
            'testCollection',
            creator=self._user,
            description='Contain applications')
        self._app = Folder().createFolder(
            parent=self._collection,
            name='application',
            description='app description',
            parentType='Collection',
            public=True,
            creator=self._user)
        self._app = Folder().setMetadata(
            self._app,
            {'extensionNameTemplate': self._extensionNameTemplate}
        )
        self._nightly = Folder().createFolder(
            parent=self._app,
            name=constants.NIGHTLY_RELEASE_NAME,
            description='Uploaded each night, always up-to-date',
            parentType='Folder',
            public=True,
            creator=self._user)
        self._release = Folder().createFolder(
            parent=self._app,
            name='release',
            description='release description',
            parentType='Folder',
            public=True,
            creator=self._user)
        self._release = Folder().setMetadata(self._release, {'revision': '12345'})

        self._extensions = {
            'extension1': {
                'name': 'slicerExt_i386_linux_35333',
                'meta': {
                    'os': 'linux',
                    'arch': 'i386',
                    'baseName': 'slicerExt',
                    'repository_type': 'git',
                    'repository_url': 'http://slicer.com/extension/Ext',
                    'revision': '35333',
                    'app_revision': '12345',
                    'packagetype': 'installer',
                    'codebase': 'SL4',
                    'description': 'Extension for Slicer 4'
                }
            },
            'extension2': {
                'name': 'slicerExt1_i386_win_54342',
                'meta': {
                    'os': 'win',
                    'arch': 'i386',
                    'baseName': 'slicerExt1',
                    'repository_type': 'git',
                    'repository_url': 'http://slicer.com/extension/Ext',
                    'revision': '54342',
                    'app_revision': '112233',
                    'packagetype': 'installer',
                    'codebase': 'SL4',
                    'description': 'Extension for Slicer 4 new version'
                }
            },
            'extension3': {
                'name': 'slicerExt2_amd64_linux_542',
                'meta': {
                    'os': 'linux',
                    'arch': 'amd64',
                    'baseName': 'slicerExt2',
                    'repository_type': 'gitlab',
                    'repository_url': 'http://slicer.com/extension/Ext',
                    'revision': '542',
                    'app_revision': '112233',
                    'packagetype': 'zip',
                    'codebase': 'SL434334',
                    'description': 'Extension for Slicer 4 new version'
                }
            }
        }

    def _createApplicationCheck(self, appName, appDescription, extensionNameTemplate, collId=None,
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
            resp.json['meta']['extensionNameTemplate'], extensionNameTemplate)

        # Check if it has created the collection
        collection = Collection().load(resp.json['parentId'], user=self._user)
        self.assertEqual(collection['name'], collName)
        if collDescription:
            self.assertEqual(collection['description'], collDescription)

        # Check if it has created "the nightly" release
        parent = Folder().load(resp.json['_id'], user=self._user)
        nightly = list(Folder().childFolders(parent, 'Folder', user=self._user))
        self.assertEqual(len(nightly), 1)
        self.assertEqual(nightly[0]['name'], constants.NIGHTLY_RELEASE_NAME)
        self.assertEqual(nightly[0]['description'], 'Uploaded each night, always up-to-date')

        return resp.json

    def testInitApp(self):
        # Without any collection this should create the new 'Applications' collection
        self._createApplicationCheck(
            'App_test',
            'Application without specifying any collection',
            self._extensionNameTemplate,
            collDescription='Automatic creation of the collection Applications')

        # Without any collection this should load the 'Applications' collection
        self._createApplicationCheck(
            'App_test1',
            'Application without specifying any collection',
            self._extensionNameTemplate)

        # With a collection ID this should load the collection
        self._createApplicationCheck(
            'App_test2',
            'Application with a collection ID',
            self._extensionNameTemplate,
            collId=self._collection['_id'])

        # With a collection name that match an existing collection name
        self._createApplicationCheck(
            'App_test3',
            'Application with a collection name',
            self._extensionNameTemplate,
            collName=self._collection['name'])

        # With a collection name that does not exist yet
        self._createApplicationCheck(
            'App_test4',
            'Application with a collection name',
            self._extensionNameTemplate,
            collName='Collection_for_app')

    def testGetApp(self):
        resp = self.request(
            path='/app',
            method='GET',
            user=self._user,
            params={'id': self._app['_id']}
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], self._app['name'])
        self.assertEqual(resp.json['description'], self._app['description'])
        self.assertEqual(
            resp.json['meta']['extensionNameTemplate'], self._extensionNameTemplate)

    def testDeleteApp(self):
        # Create the application without any collection,
        # this should create the new 'Applications' collection
        app = self._createApplicationCheck(
            'App_test',
            'Application without specifying any collection',
            self._extensionNameTemplate,
            collDescription='Automatic creation of the collection Applications')
        # Get the new application
        resp = self.request(
            path='/app',
            method='GET',
            user=self._user,
            params={'id': app['_id']}
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], app['name'])
        # Delete the application
        resp = self.request(
            path='/app/{app_id}'.format(app_id=app['_id']),
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(
            resp.json,
            {'message': 'Deleted folder {app_name}.'.format(app_name='App_test')}
        )
        # Try to get the application should failed
        resp = self.request(
            path='/app',
            method='GET',
            user=self._user,
            params={'id': app['_id']}
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json, None)

    def testNewRelease(self):
        resp = self.request(
            path='/app/{app_id}/release'.format(app_id=self._app['_id']),
            method='POST',
            user=self._user,
            params={
                'name': 'V3.2.1',
                'app_revision': '12345',
                'description': 'This is a new release'
            }
        )
        # Check if it has created the new release
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], 'V3.2.1')
        self.assertEqual(resp.json['description'], 'This is a new release')
        self.assertEqual(resp.json['meta']['revision'], '12345')

    def testGetAllRelease(self):
        resp = self.request(
            path='/app/{app_id}/release'.format(app_id=self._app['_id']),
            method='GET',
            user=self._user
        )
        # Check if it has return all the releases 'release' & 'nightly'
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 2)

    def testGetReleaseByIdOrName(self):
        # Get by ID
        resp = self.request(
            path='/app/{app_id}/release/{id_or_name}'.format(
                app_id=self._app['_id'],
                id_or_name=self._release['_id']),
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], self._release['name'])
        self.assertEqual(resp.json['description'], self._release['description'])
        self.assertEqual(ObjectId(resp.json['_id']), self._release['_id'])

        # Get by name
        resp = self.request(
            path='/app/{app_id}/release/{id_or_name}'.format(
                app_id=self._app['_id'],
                id_or_name=self._release['name']),
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], self._release['name'])
        self.assertEqual(resp.json['description'], self._release['description'])
        self.assertEqual(ObjectId(resp.json['_id']), self._release['_id'])

    def testDeleteReleaseByID(self):
        # Create the release
        resp = self.request(
            path='/app/{app_id}/release'.format(app_id=self._app['_id']),
            method='POST',
            user=self._user,
            params={
                'name': 'V3.2.1',
                'app_revision': '12345',
                'description': 'This is a new release'
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], 'V3.2.1')
        release = resp.json
        # Get the new release by ID
        resp = self.request(
            path='/app/{app_id}/release/{id_or_name}'.format(
                app_id=self._app['_id'],
                id_or_name=release['_id']),
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], release['name'])
        # Delete the release by ID
        resp = self.request(
            path='/app/{app_id}/release/{id_or_name}'.format(
                app_id=self._app['_id'],
                id_or_name=release['_id']),
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(
            resp.json,
            {'message': 'Deleted folder {release_name}.'.format(release_name=release['name'])}
        )
        # Try to get the release should failed
        resp = self.request(
            path='/app/{app_id}/release/{id_or_name}'.format(
                app_id=self._app['_id'],
                id_or_name=release['_id']),
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json, None)

    def testDeleteReleaseByName(self):
        # Create the release
        resp = self.request(
            path='/app/{app_id}/release'.format(app_id=self._app['_id']),
            method='POST',
            user=self._user,
            params={
                'name': 'V3.2.1',
                'app_revision': '12345',
                'description': 'This is a new release'
            }
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], 'V3.2.1')
        release = resp.json
        # Get the new release by name
        resp = self.request(
            path='/app/{app_id}/release/{id_or_name}'.format(
                app_id=self._app['_id'],
                id_or_name=release['name']),
            method='GET',
            user=self._user,
        )
        self.assertStatusOk(resp)
        self.assertEqual(resp.json['name'], release['name'])
        # Delete the release by name
        resp = self.request(
            path='/app/{app_id}/release/{id_or_name}'.format(
                app_id=self._app['_id'],
                id_or_name=release['name']),
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(
            resp.json,
            {'message': 'Deleted folder {release_name}.'.format(release_name=release['name'])}
        )
        # Try to get the release should failed
        resp = self.request(
            path='/app/{app_id}/release/{id_or_name}'.format(
                app_id=self._app['_id'],
                id_or_name=release['name']),
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
                'size': os.path.getsize(file),
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
            self.assertEqual(uploadedFile['size'], os.path.getsize(file))
        return uploadedFile

    def _createOrUpdateExtension(self, params):
        resp = self.request(
            path='/app/{app_id}/extension'.format(app_id=self._app['_id']),
            method='POST',
            user=self._user,
            params=params)
        self.assertStatusOk(resp)
        resp.json['meta'].pop('app_id')
        self.assertEqual(resp.json['meta'], params)
        return resp.json

    def _downloadFile(self, id):
        resp = self.request(
            path='/file/{file_id}/download'.format(file_id=id),
            method='GET',
            user=self._user,
            isJson=False)
        self.assertStatusOk(resp)
        return self.getBody(resp, text=False)

    def testCreateExtension(self):
        # Create a new extension in the release "self._release"
        extension1 = self._createOrUpdateExtension(self._extensions['extension1']['meta'])
        self.assertEqual(extension1['name'], self._extensions['extension1']['name'])
        self.assertEqual(ObjectId(extension1['folderId']), self._release['_id'])

        # Create an other extension in the "nightly" release
        extension2 = self._createOrUpdateExtension(self._extensions['extension2']['meta'])
        self.assertEqual(extension2['name'], self._extensions['extension2']['name'])
        self.assertEqual(ObjectId(extension2['folderId']), self._nightly['_id'])

        # Create a third extension
        extension3 = self._createOrUpdateExtension(self._extensions['extension3']['meta'])
        self.assertEqual(extension3['name'], self._extensions['extension3']['name'])
        self.assertEqual(ObjectId(extension3['folderId']), self._nightly['_id'])

        # Upload an extension file
        sha512 = hashlib.sha512()
        filePath = 'extension.tar.gz'
        file = os.path.join(self.dataDir, filePath)
        with open(file, 'rb') as fp:
            sha512.update(fp.read())
            shaUploadedFile = sha512.hexdigest()
        uploadedFile = self._uploadExternalData(extension3, filePath)

        # Download the extension
        sha512 = hashlib.sha512()
        sha512.update(self._downloadFile(uploadedFile['_id']))
        shaDownloadedFile = sha512.hexdigest()

        self.assertEqual(shaUploadedFile, shaDownloadedFile)

    def testUpdateExtensions(self):
        extension = self._createOrUpdateExtension(self._extensions['extension2']['meta'])
        self.assertEqual(extension['name'], 'slicerExt1_i386_win_54342')
        self.assertEqual(ObjectId(extension['folderId']), self._nightly['_id'])
        # Update the same extension
        newParams = self._extensions['extension2']['meta'].copy()
        newParams.update({
            'repository_type': 'gitlab',
            'packagetype': 'zip',
            'codebase': 'SL434334',
            'description': 'Extension for Slicer 4 new version 2'
        })
        updatedExtension = self._createOrUpdateExtension(newParams)
        self.assertEqual(updatedExtension['name'], 'slicerExt1_i386_win_54342')
        self.assertEqual(ObjectId(updatedExtension['folderId']), self._nightly['_id'])
        self.assertNotEqual(updatedExtension['meta'], extension['meta'])

    def testGetExtensions(self):
        # Create a new extension in the release "self._release"
        extension1 = self._createOrUpdateExtension(self._extensions['extension1']['meta'])
        self.assertEqual(extension1['name'], self._extensions['extension1']['name'])
        self.assertEqual(ObjectId(extension1['folderId']), self._release['_id'])

        # Create an other extension in the "nightly" release
        extension2 = self._createOrUpdateExtension(self._extensions['extension2']['meta'])
        self.assertEqual(extension2['name'], self._extensions['extension2']['name'])
        self.assertEqual(ObjectId(extension2['folderId']), self._nightly['_id'])

        # Create a third extension
        extension3 = self._createOrUpdateExtension(self._extensions['extension3']['meta'])
        self.assertEqual(extension3['name'], self._extensions['extension3']['name'])
        self.assertEqual(ObjectId(extension3['folderId']), self._nightly['_id'])

        # Get all the extension of the application
        resp = self.request(
            path='/app/{app_id}/extension'.format(app_id=self._app['_id']),
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 3)

        # Get all the extension of the application for Linux
        resp = self.request(
            path='/app/{app_id}/extension'.format(app_id=self._app['_id']),
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
            path='/app/{app_id}/extension'.format(app_id=self._app['_id']),
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

        # TODO: Add the file verification ?

    def testDeleteExtension(self):
        # Create a new extension in the release "self._release"
        extension = self._createOrUpdateExtension(self._extensions['extension1']['meta'])
        self.assertEqual(extension['name'], self._extensions['extension1']['name'])
        self.assertEqual(ObjectId(extension['folderId']), self._release['_id'])
        # Get all the extension of the application, this should only be the new one
        resp = self.request(
            path='/app/{app_id}/extension'.format(app_id=self._app['_id']),
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 1)
        # Delete the extension
        resp = self.request(
            path='/app/{app_id}/extension/{ext_id}'.format(
                app_id=self._app['_id'],
                ext_id=extension['_id']),
            method='DELETE',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(
            resp.json,
            {'message': 'Deleted extension {ext_name}.'.format(ext_name=extension['name'])}
        )
        # Try to get the extension shouldn't success
        resp = self.request(
            path='/app/{app_id}/extension'.format(app_id=self._app['_id']),
            method='GET',
            user=self._user
        )
        self.assertStatusOk(resp)
        self.assertEqual(len(resp.json), 0)
