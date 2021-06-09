import os

import pytest

from bson.objectid import ObjectId

from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.file import File
from girder.models.user import User

from pytest_girder.assertions import assertStatusOk
from pytest_girder.utils import getResponseBody

from slicer_package_manager import constants, utilities

from . import computeFileChecksum, computeContentChecksum, EXTENSIONS, FIXTURE_DIR, PACKAGES, expectedDownloadStats


def _initialize():
    _user = User().createUser('usr0', 'passwd', 'tst', 'usr', 'u@u.com')
    _collection = Collection().createCollection(
        'testCollection',
        creator=_user,
        description='Contain applications')
    _packages = Folder().createFolder(
        parent=_collection,
        name=constants.TOP_LEVEL_FOLDER_NAME,
        parentType='Collection',
        public=True,
        creator=_user)
    _app = Folder().createFolder(
        parent=_packages,
        name='application',
        description='app description',
        parentType='Folder',
        public=True,
        creator=_user)
    _app = Folder().setMetadata(
        _app,
        {
            'applicationPackageNameTemplate': constants.APPLICATION_PACKAGE_TEMPLATE_NAME,
            'extensionPackageNameTemplate': constants.EXTENSION_PACKAGE_TEMPLATE_NAME
        }
    )
    _draftRelease = Folder().createFolder(
        parent=_app,
        name=constants.DRAFT_RELEASE_NAME,
        description='Uploaded each night, always up-to-date',
        parentType='Folder',
        public=True,
        creator=_user)
    _draftRevision = Folder().createFolder(
        parent=_draftRelease,
        name='0000',
        parentType='Folder',
        public=True,
        creator=_user)
    _draftRevision = Folder().setMetadata(
        _draftRevision,
        {'revision': '0000'}
    )
    _release = Folder().createFolder(
        parent=_app,
        name='release1',
        description='release description',
        parentType='Folder',
        public=True,
        creator=_user)
    _release = Folder().setMetadata(_release, {'revision': '0005'})

    _extensions = EXTENSIONS
    for extension in _extensions:
        extension['name'] = constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(**extension['meta'])

    _packages = PACKAGES
    for package in _packages:
        package['name'] = constants.APPLICATION_PACKAGE_TEMPLATE_NAME.format(**package['meta'])

    return _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages


@pytest.mark.plugin('slicer_package_manager')
def testInitApp(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    _createApplicationCheck(
        server,
        'App_test',
        'Application without specifying any collection',
        collDescription='Automatic creation of the collection Applications',
        _user=_user
    )
    # Without any collection this should load the 'Applications' collection
    _createApplicationCheck(
        server,
        'App_test1',
        'Application without specifying any collection',
        _user=_user
    )
    # With a collection ID this should load the collection
    _createApplicationCheck(
        server,
        'App_test2',
        'Application with a collection ID',
        collId=_collection['_id'],
        _user=_user
    )
    # With a collection name that match an existing collection name
    _createApplicationCheck(
        server,
        'App_test3',
        'Application with a collection name',
        collName=_collection['name'],
        _user=_user
    )
    # With a collection name that does not exist yet
    _createApplicationCheck(
        server,
        'App_test4',
        'Application with a collection name',
        collName='Collection_for_app',
        _user=_user
    )


@pytest.mark.plugin('slicer_package_manager')
def testListApp(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create applications in the 'Applications' collection
    app1 = _createApplicationCheck(
        server,
        'App_test1',
        'Application without specifying any collection',
        collDescription='Automatic creation of the collection Applications',
        _user=_user
    )
    app2 = _createApplicationCheck(
        server,
        'App_test2',
        'Application without specifying any collection',
        collDescription='Automatic creation of the collection Applications',
        _user=_user
    )
    # Get application with application ID
    resp = server.request(
        path='/app',
        method='GET',
        user=_user,
        params={'app_id': _app['_id']}
    )
    assertStatusOk(resp)
    assert ObjectId(resp.json['_id']) == _app['_id']
    assert resp.json['name'] == _app['name']
    assert resp.json['description'] == _app['description']
    assert resp.json['meta']['applicationPackageNameTemplate'] == constants.APPLICATION_PACKAGE_TEMPLATE_NAME
    assert resp.json['meta']['extensionPackageNameTemplate'] == constants.EXTENSION_PACKAGE_TEMPLATE_NAME
    # List all applications from 'Applications' collection (Default)
    resp = server.request(
        path='/app',
        method='GET',
        user=_user
    )
    assertStatusOk(resp)
    assert len(resp.json) == 2
    assert resp.json[0]['_id'] == app1['_id']
    assert resp.json[1]['_id'] == app2['_id']
    # Get application with exact name
    resp = server.request(
        path='/app',
        method='GET',
        user=_user,
        params={
            'collection_id': _collection['_id'],
            'name': _app['name']}
    )
    assertStatusOk(resp)
    assert ObjectId(resp.json[0]['_id']) == _app['_id']
    assert resp.json[0]['name'] == _app['name']
    assert resp.json[0]['description'] == _app['description']
    assert resp.json[0]['meta']['applicationPackageNameTemplate'] == constants.APPLICATION_PACKAGE_TEMPLATE_NAME
    assert resp.json[0]['meta']['extensionPackageNameTemplate'] == constants.EXTENSION_PACKAGE_TEMPLATE_NAME


@pytest.mark.plugin('slicer_package_manager')
def testDeleteApp(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create the application without any collection,
    # this should create the new 'Applications' collection
    app = _createApplicationCheck(
        server,
        'App_test',
        'Application without specifying any collection',
        collDescription='Automatic creation of the collection Applications',
        _user=_user
    )
    # Get the new application by ID
    resp = server.request(
        path='/app',
        method='GET',
        user=_user,
        params={'app_id': app['_id']}
    )
    assertStatusOk(resp)
    assert resp.json['_id'] == app['_id']
    assert resp.json['name'] == app['name']
    # Delete the application
    resp = server.request(
        path='/app/%s' % app['_id'],
        method='DELETE',
        user=_user
    )
    assertStatusOk(resp)
    assert resp.json['_id'] == app['_id']
    # Try to get the application should failed
    resp = server.request(
        path='/app',
        method='GET',
        user=_user,
        params={'app_id': app['_id']}
    )
    assertStatusOk(resp)
    assert resp.json is None


@pytest.mark.plugin('slicer_package_manager')
def testNewRelease(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    _createReleaseCheck(
        server,
        name='V3.2.1',
        app_id=_app['_id'],
        app_revision='001',
        desc='This is a new release',
        _user=_user
    )


@pytest.mark.plugin('slicer_package_manager')
def testGetRelease(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    release1 = _createReleaseCheck(
        server,
        name='V3.2.1',
        app_id=_app['_id'],
        app_revision='002',
        desc='This is a new release',
        _user=_user
    )

    resp = server.request(
        path='/app/%s/release' % _app['_id'],
        method='GET',
        user=_user
    )
    # Check if it has return all the stable releases
    assertStatusOk(resp)
    assert len(resp.json) == 2
    assert resp.json[0]['_id'] == release1['_id']
    assert ObjectId(resp.json[1]['_id']) == _release['_id']

    # Get one release by ID
    resp = server.request(
        path='/app/%s/release' % _app['_id'],
        params={'release_id_or_name': _release['_id']},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert resp.json['name'] == _release['name']
    assert resp.json['description'] == _release['description']
    assert ObjectId(resp.json['_id']) == _release['_id']

    # Get one release by name
    resp = server.request(
        path='/app/%s/release' % _app['_id'],
        params={'release_id_or_name': _release['name']},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert resp.json['name'] == _release['name']
    assert resp.json['description'] == _release['description']
    assert ObjectId(resp.json['_id']) == _release['_id']

    resp = server.request(
        path='/app/%s/release' % _app['_id'],
        params={'release_id_or_name': constants.DRAFT_RELEASE_NAME},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert resp.json['name'] == constants.DRAFT_RELEASE_NAME
    assert ObjectId(resp.json['_id']) == _draftRelease['_id']


@pytest.mark.plugin('slicer_package_manager')
def testGetAllDraftRelease(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    resp = server.request(
        path='/app/%s/draft' % _app['_id'],
        method='GET',
        user=_user
    )
    # Check if it has return all the revision from the default release
    assertStatusOk(resp)
    assert len(resp.json) == 1
    assert ObjectId(resp.json[0]['_id']) == _draftRevision['_id']
    assert resp.json[0]['meta']['revision'] == _draftRevision['meta']['revision']
    # With the parameter 'revision'
    resp = server.request(
        path='/app/%s/draft' % _app['_id'],
        method='GET',
        user=_user,
        params={'revision': _draftRevision['meta']['revision']}
    )
    # Check if it has return the good revision from the draft folder
    assertStatusOk(resp)
    assert len(resp.json) == 1
    assert ObjectId(resp.json[0]['_id']) == _draftRevision['_id']
    assert resp.json[0]['meta']['revision'] == _draftRevision['meta']['revision']
    # With the parameter 'revision' set to a wrong value
    resp = server.request(
        path='/app/%s/draft' % _app['_id'],
        method='GET',
        user=_user,
        params={'revision': 'wrongRev'}
    )
    # Check if it has return the good revision from the draft folder
    assertStatusOk(resp)
    assert len(resp.json) == 0


@pytest.mark.plugin('slicer_package_manager')
def testDeleteReleaseByID(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    _deleteRelease(server, '_id', _user=_user, _app=_app)


@pytest.mark.plugin('slicer_package_manager')
def testDeleteReleaseByName(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    _deleteRelease(server, 'name', _user=_user, _app=_app)


@pytest.mark.external_data(
    os.path.join(FIXTURE_DIR, 'extension2.tar.gz'),
    os.path.join(FIXTURE_DIR, 'extension3.tar.gz'),
)
@pytest.mark.plugin('slicer_package_manager')
def testDeleteRevisionRelease(server, fsAssetstore, external_data):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create extensions in the "draft" release
    extension0 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[2]['meta'],
        external_data.join('extension2.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension0['name'] == _extensions[2]['name']
    extension1 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[3]['meta'],
        external_data.join('extension3.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension1['name'] == _extensions[3]['name']

    resp = server.request(
        path='/app/%s/draft' % _app['_id'],
        method='GET',
        user=_user
    )
    # Check if it has return all the revision from the default release
    assertStatusOk(resp)
    assert len(resp.json) == 2

    # Delete by Name the revision release '0001' in the "draft" release
    resp = server.request(
        path='/app/%s/release/%s' %
             (_app['_id'], _extensions[3]['meta']['app_revision']),
        method='DELETE',
        user=_user
    )
    assertStatusOk(resp)

    resp = server.request(
        path='/app/%s/draft' % _app['_id'],
        method='GET',
        user=_user
    )
    # Check if it has return all the revision from the default release
    assertStatusOk(resp)
    assert len(resp.json) == 1


@pytest.mark.external_data(
    os.path.join(FIXTURE_DIR, 'extension0.tar.gz'),
    os.path.join(FIXTURE_DIR, 'extension1.tar.gz'),
    os.path.join(FIXTURE_DIR, 'extension2.tar.gz')
)
@pytest.mark.plugin('slicer_package_manager')
def testUploadAndDownloadExtension(server, fsAssetstore, external_data):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create a new extension in the release "_release"
    extension0 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[0]['meta'],
        external_data.join('extension0.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension0['name'] == _extensions[0]['name']
    extensions_folder = Folder().load(extension0['folderId'], user=_user)
    assert ObjectId(extensions_folder['parentId']) == _release['_id']
    # Create an other extension in the "draft" release
    extension1 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[1]['meta'],
        external_data.join('extension1.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension1['name'] == _extensions[1]['name']
    # Create a third extension in the "draft" release
    extension2 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[2]['meta'],
        external_data.join('extension2.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension2['name'] == _extensions[2]['name']
    # Try to create the same extension should just get the same one
    extension2 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[2]['meta'],
        external_data.join('extension2.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension2['name'] == _extensions[2]['name']


@pytest.mark.external_data(
    os.path.join(FIXTURE_DIR, 'extension1.tar.gz')
)
@pytest.mark.plugin('slicer_package_manager')
def testUpdateExtensions(server, fsAssetstore, external_data):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    extension = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[1]['meta'],
        external_data.join('extension1.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension['name'] == _extensions[1]['name']
    # Update the same extension
    newParams = _extensions[1]['meta'].copy()
    newParams.update({
        'revision': '0000',
        'repository_type': 'gitlab',
        'packagetype': 'zip',
        'codebase': 'SL434334',
        'description': 'Extension for Slicer 4 new version 2'
    })
    updatedExtension = _createOrUpdatePackage(server, 'extension', newParams, _user=_user, _app=_app)
    # Check the same extension has different metadata
    assert updatedExtension['_id'] == extension['_id']
    assert updatedExtension['name'] == constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(**newParams)
    assert updatedExtension['meta'] != extension['meta']


@pytest.mark.plugin('slicer_package_manager')
def testGetExtensions(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create a new extension in the release "_release"
    extension0 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[0]['meta'],
        _user=_user,
        _app=_app
    )
    assert extension0['name'] == _extensions[0]['name']
    extensions_folder = Folder().load(extension0['folderId'], user=_user)
    assert ObjectId(extensions_folder['parentId']) == _release['_id']
    # Create other extensions in the "draft" release
    extension1 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[1]['meta'],
        _user=_user,
        _app=_app
    )
    assert extension1['name'] == _extensions[1]['name']
    extension2 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[2]['meta'],
        _user=_user,
        _app=_app
    )
    assert extension2['name'] == _extensions[2]['name']
    # Get all the extension of the application
    resp = server.request(
        path='/app/%s/extension' % _app['_id'],
        method='GET',
        user=_user
    )
    assertStatusOk(resp)
    assert len(resp.json) == 3
    # Get all the extension of the application for Linux
    resp = server.request(
        path='/app/%s/extension' % _app['_id'],
        method='GET',
        user=_user,
        params={
            'os': 'linux'
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 2
    for ext in resp.json:
        assert ext['meta']['os'] == 'linux'
    # Get all the extension of the application for Linux and amd64 architecture
    resp = server.request(
        path='/app/%s/extension' % _app['_id'],
        method='GET',
        user=_user,
        params={
            'os': 'linux',
            'arch': 'amd64'
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 1
    for ext in resp.json:
        assert ext['meta']['os'] == 'linux'
        assert ext['meta']['arch'] == 'amd64'
    # Get all the extension of the application which are in "release1"
    resp = server.request(
        path='/app/%s/extension' % _app['_id'],
        method='GET',
        user=_user,
        params={
            'release_id': _release['_id']
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 1
    # Get all the extension of the application which are in the draft release
    draftRelease = list(Folder().childFolders(
        _app,
        'Folder',
        user=_user,
        filters={'name': constants.DRAFT_RELEASE_NAME}))
    resp = server.request(
        path='/app/%s/extension' % _app['_id'],
        method='GET',
        user=_user,
        params={
            'release_id': draftRelease[0]['_id']
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 2
    # Get a specific extension by name
    resp = server.request(
        path='/app/%s/extension' % _app['_id'],
        params={'extension_name': extension2['name']},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert resp.json[0]['_id'] == extension2['_id']
    assert resp.json[0]['name'] == extension2['name']
    # Get a specific extension with wrong name
    resp = server.request(
        path='/app/%s/extension' % _app['_id'],
        params={'extension_name': 'wrong_name'},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert len(resp.json) == 0
    assert resp.json == []


@pytest.mark.plugin('slicer_package_manager')
def testDeleteExtensionPackages(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create a new extension in the release "_release"
    extension = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[0]['meta'],
        _user=_user,
        _app=_app
    )
    assert extension['name'] == _extensions[0]['name']
    extensions_folder = Folder().load(extension['folderId'], user=_user)
    assert ObjectId(extensions_folder['parentId']) == _release['_id']
    # Get, delete, and try to re-get the package
    _deletePackages(server, 'extension', extension, _user=_user, _app=_app)


@pytest.mark.external_data(
    os.path.join(FIXTURE_DIR, 'pkg0.dmg'),
    os.path.join(FIXTURE_DIR, 'pkg1.exe'),
    os.path.join(FIXTURE_DIR, 'pkg2.tar.gz')
)
@pytest.mark.plugin('slicer_package_manager')
def testUploadAndDownloadPackages(server, fsAssetstore, external_data):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create a new application package in the release "_release"
    package0 = _createOrUpdatePackage(
        server,
        'package',
        _packages[0]['meta'],
        external_data.join('pkg0.dmg'),
        _user=_user,
        _app=_app
    )
    assert package0['name'] == _packages[0]['name']
    assert ObjectId(package0['folderId']) == _release['_id']
    # Create an other application package in the "draft" release
    package1 = _createOrUpdatePackage(
        server,
        'package',
        _packages[1]['meta'],
        external_data.join('pkg1.exe'),
        _user=_user,
        _app=_app
    )
    assert package1['name'] == _packages[1]['name']
    # Create a third application package in the "draft" release
    package2 = _createOrUpdatePackage(
        server,
        'package',
        _packages[2]['meta'],
        external_data.join('pkg2.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert package2['name'] == _packages[2]['name']
    # Try to create the same application package should just get the same one
    package2 = _createOrUpdatePackage(
        server,
        'package',
        _packages[2]['meta'],
        external_data.join('pkg2.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert package2['name'] == _packages[2]['name']


@pytest.mark.external_data(
    os.path.join(FIXTURE_DIR, 'pkg1.exe'),
    )
@pytest.mark.plugin('slicer_package_manager')
def testUpdatePackages(server, fsAssetstore, external_data):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    package = _createOrUpdatePackage(
        server,
        'package',
        _packages[1]['meta'],
        external_data.join('pkg1.exe'),
        _user=_user,
        _app=_app
    )
    assert package['name'] == _packages[1]['name']
    # Update the same package
    newParams = _packages[1]['meta'].copy()
    newParams.update({
        'repository_url': 'https://AnotherURL.com',
        'repository_type': 'gitlab',
    })
    updatedPackage = _createOrUpdatePackage(server, 'package', newParams, _user=_user, _app=_app)
    # Check the same package has different metadata
    assert updatedPackage['_id'] == package['_id']
    assert updatedPackage['name'] == constants.APPLICATION_PACKAGE_TEMPLATE_NAME.format(**newParams)
    assert updatedPackage['meta'] != package['meta']


@pytest.mark.external_data(
    os.path.join(FIXTURE_DIR, 'pkg0.dmg'),
    os.path.join(FIXTURE_DIR, 'pkg1.exe'),
    os.path.join(FIXTURE_DIR, 'pkg2.tar.gz'),
    )
@pytest.mark.plugin('slicer_package_manager')
def testGetPackages(server, fsAssetstore, external_data):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create a new application package in the release "_release"
    package0 = _createOrUpdatePackage(
        server,
        'package',
        _packages[0]['meta'],
        external_data.join('pkg0.dmg'),
        _user=_user,
        _app=_app
    )
    assert package0['name'] == _packages[0]['name']
    assert ObjectId(package0['folderId']) == _release['_id']
    # Create an other application package in the "draft" release
    package1 = _createOrUpdatePackage(
        server,
        'package',
        _packages[1]['meta'],
        external_data.join('pkg1.exe'),
        _user=_user,
        _app=_app
    )
    assert package1['name'] == _packages[1]['name']
    # Create a third application package in the "draft" release
    package2 = _createOrUpdatePackage(
        server,
        'package',
        _packages[2]['meta'],
        external_data.join('pkg2.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert package2['name'] == _packages[2]['name']
    # Get all the package of the application
    resp = server.request(
        path='/app/%s/package' % _app['_id'],
        method='GET',
        user=_user
    )
    assertStatusOk(resp)
    assert len(resp.json) == 3
    # Get all the package of the application for Linux
    resp = server.request(
        path='/app/%s/package' % _app['_id'],
        method='GET',
        user=_user,
        params={
            'os': 'linux'
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 1
    assert resp.json[0]['meta']['os'] == 'linux'
    # Get all the package of the application for Linux and amd64 architecture
    resp = server.request(
        path='/app/%s/package' % _app['_id'],
        method='GET',
        user=_user,
        params={
            'os': 'macosx',
            'arch': 'i386'
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 0
    # Get all the package of the application which are in "release1"
    resp = server.request(
        path='/app/%s/package' % _app['_id'],
        method='GET',
        user=_user,
        params={
            'release_id_or_name': _release['_id']
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 1
    # Get all the package of the application which are in the draft release
    draftRelease = list(Folder().childFolders(
        _app,
        'Folder',
        user=_user,
        filters={'name': constants.DRAFT_RELEASE_NAME}))
    resp = server.request(
        path='/app/%s/package' % _app['_id'],
        method='GET',
        user=_user,
        params={
            'release_id_or_name': draftRelease[0]['_id']
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 2
    # Get a specific package by name
    resp = server.request(
        path='/app/%s/package' % _app['_id'],
        params={'package_name': package2['name']},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert resp.json[0]['_id'] == package2['_id']
    assert resp.json[0]['name'] == package2['name']
    # Get a specific extension with wrong name
    resp = server.request(
        path='/app/%s/package' % _app['_id'],
        params={'package_name': 'wrong_name'},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert len(resp.json) == 0
    assert resp.json == []


@pytest.mark.plugin('slicer_package_manager')
def testDeleteApplicationPackages(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    # Create a new application package in the release "_release"
    package = _createOrUpdatePackage(
        server,
        'package',
        _packages[0]['meta'],
        _user=_user,
        _app=_app
    )
    assert package['name'] == _packages[0]['name']
    assert ObjectId(package['folderId']) == _release['_id']
    # Get, delete, and try to re-get the package
    _deletePackages(server, 'package', package, _user=_user, _app=_app)


@pytest.mark.external_data(
    os.path.join(FIXTURE_DIR, 'extension0.tar.gz'),
    os.path.join(FIXTURE_DIR, 'extension1.tar.gz'),
    os.path.join(FIXTURE_DIR, 'extension2.tar.gz'),
    os.path.join(FIXTURE_DIR, 'extension3.tar.gz'),
    os.path.join(FIXTURE_DIR, 'extension4.tar.gz'),
    os.path.join(FIXTURE_DIR, 'pkg0.dmg'),
    os.path.join(FIXTURE_DIR, 'pkg1.exe'),
    os.path.join(FIXTURE_DIR, 'pkg2.tar.gz'),
    )
@pytest.mark.plugin('slicer_package_manager')
def testDownloadStats(server, fsAssetstore, external_data):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    extension0 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[0]['meta'],
        external_data.join('extension0.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension0['name'] == _extensions[0]['name']
    extension1 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[1]['meta'],
        external_data.join('extension1.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension1['name'] == _extensions[1]['name']
    extension2 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[2]['meta'],
        external_data.join('extension2.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension2['name'] == _extensions[2]['name']
    extension3 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[3]['meta'],
        external_data.join('extension3.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension3['name'] == _extensions[3]['name']
    extension4 = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[4]['meta'],
        external_data.join('extension4.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert extension4['name'] == _extensions[4]['name']
    package0 = _createOrUpdatePackage(
        server,
        'package',
        _packages[0]['meta'],
        external_data.join('pkg0.dmg'),
        _user=_user,
        _app=_app
    )
    assert package0['name'] == _packages[0]['name']
    package1 = _createOrUpdatePackage(
        server,
        'package',
        _packages[1]['meta'],
        external_data.join('pkg1.exe'),
        _user=_user,
        _app=_app
    )
    assert package1['name'] == _packages[1]['name']
    package2 = _createOrUpdatePackage(
        server,
        'package',
        _packages[2]['meta'],
        external_data.join('pkg2.tar.gz'),
        _user=_user,
        _app=_app
    )
    assert package2['name'] == _packages[2]['name']

    # Get the downloadStats
    expectedStats = expectedDownloadStats
    resp = server.request(
        path='/app/%s/downloadstats' % _app['_id'],
        method='GET',
        user=_user
    )
    assertStatusOk(resp)
    assert resp.json == expectedStats

    # Download multiple time an extension
    ext3_file = list(File().find({'itemId': ObjectId(extension3['_id'])}))
    ext4_file = list(File().find({'itemId': ObjectId(extension4['_id'])}))

    N = 5
    for _idx in range(N):
        _downloadFile(server, ext3_file[0]['_id'], _user=_user)
        _downloadFile(server, ext4_file[0]['_id'], _user=_user)

    expectedStats['0001']['extensions']['Ext2']['macosx'].update({
        'amd64': N + expectedStats['0001']['extensions']['Ext2']['macosx']['amd64'],
        'i386': N + expectedStats['0001']['extensions']['Ext2']['macosx']['i386']
    })
    resp = server.request(
        path='/app/%s/downloadstats' % _app['_id'],
        method='GET',
        user=_user
    )
    assertStatusOk(resp)
    assert resp.json == expectedStats

    # The download stats aren't affected by deletion of extension or revision
    # in the default release
    # Delete extensions
    resp = server.request(
        path='/app/%(app_id)s/extension/%(ext_id)s' % {
            'app_id': _app['_id'],
            'ext_id': extension3['_id']},
        method='DELETE',
        user=_user
    )
    assertStatusOk(resp)
    resp = server.request(
        path='/app/%(app_id)s/extension/%(ext_id)s' % {
            'app_id': _app['_id'],
            'ext_id': extension4['_id']},
        method='DELETE',
        user=_user
    )
    assertStatusOk(resp)
    # Delete the revision '0000' in the "draft" release
    resp = server.request(
        path='/app/%(app_id)s/release/%(release_id)s' % {
            'app_id': _app['_id'],
            'release_id': _draftRevision['_id']},
        method='DELETE',
        user=_user
    )
    assertStatusOk(resp)
    # Check if download Stats are the same
    resp = server.request(
        path='/app/%s/downloadstats' % _app['_id'],
        method='GET',
        user=_user
    )
    assertStatusOk(resp)
    assert resp.json == expectedStats


@pytest.mark.plugin('slicer_package_manager')
def testGetReleaseFolder(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()

    # Create an application package in the release "_release"
    release_package = _createOrUpdatePackage(
        server,
        'package',
        _packages[0]['meta'],
        _user=_user,
        _app=_app
    )
    assert release_package['name'] == _packages[0]['name']
    assert ObjectId(release_package['folderId']) == _release['_id']
    assert utilities.getReleaseFolder(release_package)['_id'] == _release['_id']

    # Create an application package in the "draft" release
    draft_package = _createOrUpdatePackage(
        server,
        'package',
        _packages[1]['meta'],
        _user=_user,
        _app=_app
    )
    assert draft_package['name'] == _packages[1]['name']
    assert utilities.getReleaseFolder(draft_package)['name'] == constants.DRAFT_RELEASE_NAME

    # Create an extension in the release "_release"
    release_extension = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[0]['meta'],
        _user=_user,
        _app=_app
    )
    assert release_extension['name'] == _extensions[0]['name']
    extensions_folder = Folder().load(release_extension['folderId'], user=_user)
    assert ObjectId(extensions_folder['parentId']) == _release['_id']
    assert utilities.getReleaseFolder(release_extension)['_id'] == _release['_id']

    # Create an extension in the "draft" release
    draft_extension = _createOrUpdatePackage(
        server,
        'extension',
        _extensions[1]['meta'],
        _user=_user,
        _app=_app
    )
    assert draft_extension['name'] == _extensions[1]['name']
    assert utilities.getReleaseFolder(draft_extension)['name'] == constants.DRAFT_RELEASE_NAME


@pytest.mark.plugin('slicer_package_manager')
def testIsApplicationFolder(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    assert utilities.isApplicationFolder(_app)
    assert not utilities.isApplicationFolder(_release)
    assert not utilities.isApplicationFolder(_draftRelease)
    assert not utilities.isApplicationFolder(_draftRevision)


@pytest.mark.plugin('slicer_package_manager')
def testIsReleaseFolder(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    assert not utilities.isReleaseFolder(_app)
    assert utilities.isReleaseFolder(_release)
    assert not utilities.isReleaseFolder(_draftRelease)
    assert utilities.isReleaseFolder(_draftRevision)


@pytest.mark.plugin('slicer_package_manager')
def testIsDraftReleaseFolder(server):
    _user, _collection, _app, _release, _draftRelease, _draftRevision, _extensions, _packages = _initialize()
    assert not utilities.isDraftReleaseFolder(_app)
    assert not utilities.isDraftReleaseFolder(_release)
    assert not utilities.isDraftReleaseFolder(_draftRelease)
    assert utilities.isDraftReleaseFolder(_draftRevision)


def _createApplicationCheck(server, appName, appDescription, collId=None,
                            collName=None, collDescription='', _user=None):
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
        collection = Collection().load(collId, user=_user)
        collName = collection['name']
    else:
        params.update({'collection_name': collName})

    resp = server.request(
        path='/app',
        method='POST',
        user=_user,
        params=params
    )
    # Check if it has created the application
    assertStatusOk(resp)
    assert resp.json['name'] == appName
    assert resp.json['description'] == appDescription
    assert resp.json['meta']['applicationPackageNameTemplate'] == constants.APPLICATION_PACKAGE_TEMPLATE_NAME
    assert resp.json['meta']['extensionPackageNameTemplate'] == constants.EXTENSION_PACKAGE_TEMPLATE_NAME
    # Check if it has created/load the collection
    topLevelFolder = Folder().load(resp.json['parentId'], user=_user)
    collection = Collection().load(topLevelFolder['parentId'], user=_user)
    assert collection['name'] == collName
    if collDescription:
        assert collection['description'] == collDescription
    # Check if it has created the "draft" release
    parent = Folder().load(resp.json['_id'], user=_user)
    draft = list(Folder().childFolders(parent, 'Folder', user=_user))
    assert len(draft) == 1
    assert draft[0]['name'] == constants.DRAFT_RELEASE_NAME
    assert draft[0]['description'] == 'Uploaded each night, always up-to-date'

    return resp.json


def _createReleaseCheck(server, name, app_id, app_revision, desc='', _user=None):
    resp = server.request(
        path='/app/%s/release' % app_id,
        method='POST',
        user=_user,
        params={
            'name': name,
            'app_revision': app_revision,
            'description': desc
        }
    )
    # Check if it has created the new release
    assertStatusOk(resp)
    assert resp.json['name'] == name
    assert resp.json['description'] == desc
    assert resp.json['meta']['revision'] == app_revision
    return resp.json


def _deleteRelease(server, identifier, _user=None, _app=None):
    # Create the release
    release = _createReleaseCheck(
        server,
        name='V3.2.1',
        app_id=_app['_id'],
        app_revision='001',
        desc='This is a new release',
        _user=_user
    )
    # Get the new release by name
    resp = server.request(
        path='/app/%s/release' % _app['_id'],
        params={'release_id_or_name': release[identifier]},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert resp.json['_id'] == release['_id']
    assert resp.json['name'] == release['name']
    # Delete the release by name
    resp = server.request(
        path='/app/%(app_id)s/release/%(id_or_name)s' % {
            'app_id': _app['_id'],
            'id_or_name': release[identifier]},
        method='DELETE',
        user=_user
    )
    assertStatusOk(resp)
    assert resp.json['_id'] == release['_id']
    # Try to get the release should failed
    resp = server.request(
        path='/app/%s/release' % _app['_id'],
        params={'release_id_or_name': release[identifier]},
        method='GET',
        user=_user,
    )
    assertStatusOk(resp)
    assert resp.json is None


# def _uploadExternalData(server, item, filePath, fileName=None, _user=None):
#     file = os.path.join(self.dataDir, filePath)
#     size = os.path.getsize(file)
#     offset = 0
#     if fileName is None:
#         fileName = filePath
#
#     # Initialize the upload
#     resp = server.request(
#         path='/file', method='POST', user=_user, params={
#             'parentType': 'item',
#             'parentId': item['_id'],
#             'name': fileName,
#             'size': size,
#             'mimeType': 'application/octet-stream'
#         })
#     assertStatusOk(resp)
#     uploadId = resp.json['_id']
#
#     # Upload content
#     with open(file, 'rb') as fp:
#         while True:
#             chunk = fp.read(min(self._MAX_CHUNK_SIZE, (size - offset)))
#             if not chunk:
#                 break
#             if isinstance(chunk, str):
#                 chunk = chunk.encode('utf8')
#             resp = server.request(
#                 path='/file/chunk',
#                 method='POST',
#                 user=_user,
#                 params={
#                     'offset': offset,
#                     'uploadId': uploadId
#                 },
#                 body=chunk,
#                 type='application/octet-stream'
#             )
#             assertStatusOk(resp)
#             offset += len(chunk)
#
#         uploadedFile = resp.json
#         assert 'itemId' in uploadedFile
#         assert uploadedFile['assetstoreId'] == str(self.assetstore['_id'])
#         assert uploadedFile['name'] == filePath
#         assert uploadedFile['size'] == size
#     return uploadedFile


def _downloadFile(server, id, _user=None):
    resp = server.request(
        path='/file/%s/download' % id,
        method='GET',
        user=_user,
        isJson=False)
    assertStatusOk(resp)
    return getResponseBody(resp, text=False)


def _createOrUpdatePackage(server, packageType, params, filePath=None, _user=None, _app=None):
    resp = server.request(
        path='/app/%s/%s' % (_app['_id'], packageType),
        method='POST',
        user=_user,
        params=params)
    assertStatusOk(resp)

    # Remove the app_id to check the metadata with these set during the creation
    metadata = resp.json['meta'].copy()
    metadata.pop('app_id')
    assert metadata == params

    if filePath:
        # Upload a package file
        item = resp.json
        with open(filePath, 'rb') as content:
            uploadedFile = server.uploadFile(
                filePath, content.read(), _user, item, parentType="item")

        # Download the package and compare checksum
        downloaded_checksum = computeContentChecksum('SHA512', _downloadFile(server, uploadedFile['_id'], _user=_user))
        local_checksum = computeFileChecksum('SHA512', filePath)
        assert downloaded_checksum == local_checksum
    return resp.json


def _deletePackages(server, packageType, pkg, _user=None, _app=None):
    # Get all the  application package, this should only be the new one
    resp = server.request(
        path='/app/%s/%s' % (_app['_id'], packageType),
        method='GET',
        user=_user
    )
    assertStatusOk(resp)
    assert len(resp.json) == 1
    assert resp.json[0]['_id'] == pkg['_id']
    # Delete the package
    resp = server.request(
        path='/app/%(app_id)s/%(type)s/%(pkg_id)s' % {
            'app_id': _app['_id'],
            'type': packageType,
            'pkg_id': pkg['_id']},
        method='DELETE',
        user=_user
    )
    assertStatusOk(resp)
    assert resp.json['_id'] == pkg['_id']
    # Try to get the package shouldn't success
    resp = server.request(
        path='/app/%s/%s' % (_app['_id'], packageType),
        method='GET',
        user=_user
    )
    assertStatusOk(resp)
    assert len(resp.json) == 0
