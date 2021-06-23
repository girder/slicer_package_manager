import json
import os

import pytest

from bson.objectid import ObjectId

from girder.models.collection import Collection
from girder.models.folder import Folder
from girder.models.file import File
from girder.models.user import User

from pytest_girder.assertions import assertStatus, assertStatusOk
from pytest_girder.utils import getResponseBody

from slicer_package_manager import constants, utilities

from . import (
    computeFileChecksum,
    computeContentChecksum,
    downloadExternals,
    expectedDownloadStats,
    DRAFT_EXTENSIONS,
    DRAFT_PACKAGES,
    DRAFT_RELEASES,
    EXTENSIONS,
    FIXTURE_DIR,
    PACKAGES,
    RELEASE_EXTENSIONS,
    RELEASE_PACKAGES,
    RELEASES
)


@pytest.fixture(name='user')
def fixture_user():
    yield User().createUser('usr0', 'passwd', 'tst', 'usr', 'u@u.com')


@pytest.fixture(name='collection')
def fixture_collection(user):
    yield Collection().createCollection(
        'testCollection',
        creator=user,
        description='Contain applications'
    )


@pytest.fixture(name='packages_folder')
def fixture_packages_folder(user, collection):
    yield Folder().createFolder(
        parent=collection,
        name=constants.TOP_LEVEL_FOLDER_NAME,
        parentType='Collection',
        public=True,
        creator=user
    )


@pytest.fixture(name='app_folder')
def fixture_app_folder(user, packages_folder):
    folder = Folder().createFolder(
        parent=packages_folder,
        name='application',
        description='app description',
        parentType='Folder',
        public=True,
        creator=user
    )
    folder = Folder().setMetadata(
        folder,
        {
            'applicationPackageNameTemplate': constants.APPLICATION_PACKAGE_TEMPLATE_NAME,
            'extensionPackageNameTemplate': constants.EXTENSION_PACKAGE_TEMPLATE_NAME
        }
    )
    yield folder


@pytest.fixture(name='draft_release_folder')
def fixture_draft_release_folder(user, app_folder):
    yield Folder().createFolder(
        parent=app_folder,
        name=constants.DRAFT_RELEASE_NAME,
        description='Uploaded each night, always up-to-date',
        parentType='Folder',
        public=True,
        creator=user
    )


@pytest.fixture(name='draft_release_revision_folder')
def fixture_draft_release_revision_folder(user, draft_release_folder):
    folder = Folder().createFolder(
        parent=draft_release_folder,
        name=DRAFT_RELEASES[0]['revision'],
        parentType='Folder',
        public=True,
        creator=user
    )
    folder = Folder().setMetadata(folder, {'revision': DRAFT_RELEASES[0]['revision']})
    yield folder


@pytest.fixture(name='release_folder')
def fixture_release_folder(user, app_folder):
    folder = Folder().createFolder(
        parent=app_folder,
        name='release1',
        description='release description',
        parentType='Folder',
        public=True,
        creator=user
    )
    folder = Folder().setMetadata(folder, {'revision': RELEASES[0]['revision']})
    yield folder


@pytest.fixture(name='release_extensions')
def fixture_release_extensions(server, user, app_folder, release_folder, tmpdir, fsAssetstore):
    downloadExternals(
        [os.path.join(FIXTURE_DIR, extension['filepath']) for extension in RELEASE_EXTENSIONS],
        tmpdir
    )

    extensions = [_createOrUpdatePackage(
        server, 'extension', extension['meta'],
        filePath=tmpdir.join(extension['filepath']),
        _user=user, _app=app_folder
    ) for extension in RELEASE_EXTENSIONS]

    for index, extension in enumerate(extensions):
        assert extension['name'] == RELEASE_EXTENSIONS[index]['name']
        isRelease = RELEASE_EXTENSIONS[index]['meta']['app_revision'] == release_folder['meta']['revision']
        assert isRelease
        extensions_folder = Folder().load(extension['folderId'], user=user)
        assert ObjectId(extensions_folder['parentId']) == release_folder['_id']

    yield extensions


@pytest.fixture(name='draft_extensions')
def fixture_draft_extensions(server, user, app_folder, release_folder, draft_release_folder, tmpdir, fsAssetstore):
    downloadExternals(
        [os.path.join(FIXTURE_DIR, extension['filepath']) for extension in DRAFT_EXTENSIONS],
        tmpdir
    )

    extensions = [_createOrUpdatePackage(
        server, 'extension', extension['meta'],
        filePath=tmpdir.join(extension['filepath']),
        _user=user, _app=app_folder
    ) for extension in DRAFT_EXTENSIONS]

    for index, extension in enumerate(extensions):
        assert extension['name'] == DRAFT_EXTENSIONS[index]['name']
        isRelease = DRAFT_EXTENSIONS[index]['meta']['app_revision'] == release_folder['meta']['revision']
        assert not isRelease

    yield extensions


@pytest.fixture(name='extensions')
def fixture_extensions(release_extensions, draft_extensions):
    extensions = []
    extensions.extend(release_extensions)
    extensions.extend(draft_extensions)
    yield extensions


@pytest.fixture(name='release_packages')
def fixture_release_packages(server, user, app_folder, release_folder, tmpdir, fsAssetstore):
    downloadExternals(
        [os.path.join(FIXTURE_DIR, package['filepath']) for package in RELEASE_PACKAGES],
        tmpdir
    )
    packages = [_createOrUpdatePackage(
        server, 'package', package['meta'],
        filePath=tmpdir.join(package['filepath']),
        _user=user, _app=app_folder
    ) for package in RELEASE_PACKAGES]

    for index, package in enumerate(packages):
        assert package['name'] == RELEASE_PACKAGES[index]['name']
        isRelease = RELEASE_PACKAGES[index]['meta']['revision'] == release_folder['meta']['revision']
        assert isRelease
        assert ObjectId(package['folderId']) == release_folder['_id']
        assert package['meta']['release'] == release_folder['name']

    yield packages


@pytest.fixture(name='draft_packages')
def fixture_draft_packages(server, user, app_folder, release_folder, draft_release_folder, tmpdir, fsAssetstore):
    downloadExternals(
        [os.path.join(FIXTURE_DIR, package['filepath']) for package in DRAFT_PACKAGES],
        tmpdir
    )
    packages = [_createOrUpdatePackage(
        server, 'package', package['meta'],
        filePath=tmpdir.join(package['filepath']),
        _user=user, _app=app_folder
    ) for package in DRAFT_PACKAGES]

    for index, package in enumerate(packages):
        assert package['name'] == DRAFT_PACKAGES[index]['name']
        isRelease = DRAFT_PACKAGES[index]['meta']['revision'] == release_folder['meta']['revision']
        assert not isRelease
        assert 'release' not in package['meta']

    yield packages


@pytest.fixture(name='packages')
def fixture_packages(release_packages, draft_packages):
    packages = []
    packages.extend(release_packages)
    packages.extend(draft_packages)
    yield packages


@pytest.mark.plugin('slicer_package_manager')
def testInitApp(server, user, collection):
    _createApplicationCheck(
        server,
        'App_test',
        'Application without specifying any collection',
        collDescription='Automatic creation of the collection Applications',
        _user=user
    )
    # Without any collection this should load the 'Applications' collection
    _createApplicationCheck(
        server,
        'App_test1',
        'Application without specifying any collection',
        _user=user
    )
    # With a collection ID this should load the collection
    _createApplicationCheck(
        server,
        'App_test2',
        'Application with a collection ID',
        collId=collection['_id'],
        _user=user
    )
    # With a collection name that match an existing collection name
    _createApplicationCheck(
        server,
        'App_test3',
        'Application with a collection name',
        collName=collection['name'],
        _user=user
    )
    # With a collection name that does not exist yet
    _createApplicationCheck(
        server,
        'App_test4',
        'Application with a collection name',
        collName='Collection_for_app',
        _user=user
    )


@pytest.mark.plugin('slicer_package_manager')
def testListApp(server, user, collection, app_folder):
    # Create applications in the 'Applications' collection
    app1 = _createApplicationCheck(
        server,
        'App_test1',
        'Application without specifying any collection',
        collDescription='Automatic creation of the collection Applications',
        _user=user
    )
    app2 = _createApplicationCheck(
        server,
        'App_test2',
        'Application without specifying any collection',
        collDescription='Automatic creation of the collection Applications',
        _user=user
    )

    # Get application with application ID
    resp = server.request(
        path='/app',
        method='GET',
        user=user,
        params={'app_id': app_folder['_id']}
    )
    assertStatusOk(resp)
    assert ObjectId(resp.json['_id']) == app_folder['_id']
    assert resp.json['name'] == app_folder['name']
    assert resp.json['description'] == app_folder['description']
    assert resp.json['meta']['applicationPackageNameTemplate'] == constants.APPLICATION_PACKAGE_TEMPLATE_NAME
    assert resp.json['meta']['extensionPackageNameTemplate'] == constants.EXTENSION_PACKAGE_TEMPLATE_NAME
    # List all applications from 'Applications' collection (Default)
    resp = server.request(
        path='/app',
        method='GET',
        user=user
    )
    assertStatusOk(resp)
    assert len(resp.json) == 2
    assert resp.json[0]['_id'] == app1['_id']
    assert resp.json[1]['_id'] == app2['_id']
    # Get application with exact name
    resp = server.request(
        path='/app',
        method='GET',
        user=user,
        params={
            'collection_id': collection['_id'],
            'name': app_folder['name']}
    )
    assertStatusOk(resp)
    assert ObjectId(resp.json[0]['_id']) == app_folder['_id']
    assert resp.json[0]['name'] == app_folder['name']
    assert resp.json[0]['description'] == app_folder['description']
    assert resp.json[0]['meta']['applicationPackageNameTemplate'] == constants.APPLICATION_PACKAGE_TEMPLATE_NAME
    assert resp.json[0]['meta']['extensionPackageNameTemplate'] == constants.EXTENSION_PACKAGE_TEMPLATE_NAME


@pytest.mark.plugin('slicer_package_manager')
def testDeleteApp(server, user):
    # Create the application without any collection,
    # this should create the new 'Applications' collection
    app = _createApplicationCheck(
        server,
        'App_test',
        'Application without specifying any collection',
        collDescription='Automatic creation of the collection Applications',
        _user=user
    )
    # Get the new application by ID
    resp = server.request(
        path='/app',
        method='GET',
        user=user,
        params={'app_id': app['_id']}
    )
    assertStatusOk(resp)
    assert resp.json['_id'] == app['_id']
    assert resp.json['name'] == app['name']
    # Delete the application
    resp = server.request(
        path='/app/%s' % app['_id'],
        method='DELETE',
        user=user
    )
    assertStatusOk(resp)
    assert resp.json['_id'] == app['_id']
    # Try to get the application should failed
    resp = server.request(
        path='/app',
        method='GET',
        user=user,
        params={'app_id': app['_id']}
    )
    assertStatusOk(resp)
    assert resp.json is None


@pytest.mark.plugin('slicer_package_manager')
def testNewRelease(server, user, app_folder):
    _createReleaseCheck(
        server,
        name='V3.2.1',
        app_id=app_folder['_id'],
        app_revision='001',
        desc='This is a new release',
        _user=user
    )


@pytest.mark.plugin('slicer_package_manager')
def testGetRelease(server, user, app_folder, release_folder, draft_release_folder):
    release1 = _createReleaseCheck(
        server,
        name='V3.2.1',
        app_id=app_folder['_id'],
        app_revision='002',
        desc='This is a new release',
        _user=user
    )

    resp = server.request(
        path='/app/%s/release' % app_folder['_id'],
        method='GET',
        user=user
    )
    # Check if it has return all the stable releases
    assertStatusOk(resp)
    assert len(resp.json) == 2
    assert resp.json[0]['_id'] == release1['_id']
    assert ObjectId(resp.json[1]['_id']) == release_folder['_id']

    # Get one release by ID
    resp = server.request(
        path='/app/%s/release' % app_folder['_id'],
        params={'release_id_or_name': release_folder['_id']},
        method='GET',
        user=user,
    )
    assertStatusOk(resp)
    assert resp.json['name'] == release_folder['name']
    assert resp.json['description'] == release_folder['description']
    assert ObjectId(resp.json['_id']) == release_folder['_id']

    # Get one release by name
    resp = server.request(
        path='/app/%s/release' % app_folder['_id'],
        params={'release_id_or_name': release_folder['name']},
        method='GET',
        user=user,
    )
    assertStatusOk(resp)
    assert resp.json['name'] == release_folder['name']
    assert resp.json['description'] == release_folder['description']
    assert ObjectId(resp.json['_id']) == release_folder['_id']

    resp = server.request(
        path='/app/%s/release' % app_folder['_id'],
        params={'release_id_or_name': constants.DRAFT_RELEASE_NAME},
        method='GET',
        user=user,
    )
    assertStatusOk(resp)
    assert resp.json['name'] == constants.DRAFT_RELEASE_NAME
    assert ObjectId(resp.json['_id']) == draft_release_folder['_id']


@pytest.mark.plugin('slicer_package_manager')
def testGetAllDraftRelease(server, user, app_folder, draft_release_revision_folder):
    resp = server.request(
        path='/app/%s/draft' % app_folder['_id'],
        method='GET',
        user=user
    )
    # Check if it has return all the revision from the default release
    assertStatusOk(resp)
    assert len(resp.json) == 1
    assert ObjectId(resp.json[0]['_id']) == draft_release_revision_folder['_id']
    assert resp.json[0]['meta']['revision'] == draft_release_revision_folder['meta']['revision']
    # With the parameter 'revision'
    resp = server.request(
        path='/app/%s/draft' % app_folder['_id'],
        method='GET',
        user=user,
        params={'revision': draft_release_revision_folder['meta']['revision']}
    )
    # Check if it has return the good revision from the draft folder
    assertStatusOk(resp)
    assert len(resp.json) == 1
    assert ObjectId(resp.json[0]['_id']) == draft_release_revision_folder['_id']
    assert resp.json[0]['meta']['revision'] == draft_release_revision_folder['meta']['revision']
    # With the parameter 'revision' set to a wrong value
    resp = server.request(
        path='/app/%s/draft' % app_folder['_id'],
        method='GET',
        user=user,
        params={'revision': 'wrongRev'}
    )
    # Check if it has return the good revision from the draft folder
    assertStatusOk(resp)
    assert len(resp.json) == 0


@pytest.mark.plugin('slicer_package_manager')
def testDeleteReleaseByID(server, user, app_folder):
    _deleteRelease(server, '_id', _user=user, _app=app_folder)


@pytest.mark.plugin('slicer_package_manager')
def testDeleteReleaseByName(server, user, app_folder):
    _deleteRelease(server, 'name', _user=user, _app=app_folder)


@pytest.mark.plugin('slicer_package_manager')
def testDeleteRevisionRelease(server, user, app_folder, packages, extensions):
    resp = server.request(
        path='/app/%s/draft' % app_folder['_id'],
        method='GET',
        user=user
    )

    # Check if it has return all the revision from the default release
    assertStatusOk(resp)
    assert len(resp.json) == 2

    # Delete by Name the revision release '0001' in the "draft" release
    resp = server.request(
        path='/app/%s/release/%s' %
             (app_folder['_id'], EXTENSIONS[3]['meta']['app_revision']),
        method='DELETE',
        user=user
    )
    assertStatusOk(resp)

    resp = server.request(
        path='/app/%s/draft' % app_folder['_id'],
        method='GET',
        user=user
    )
    # Check if it has return all the revision from the default release
    assertStatusOk(resp)
    assert len(resp.json) == 1


@pytest.mark.plugin('slicer_package_manager')
def testUpdateExtensions(server, user, app_folder, extensions):
    # Update the same extension
    newParams = EXTENSIONS[1]['meta'].copy()
    newParams.update({
        'revision': '0000',
        'repository_type': 'gitlab',
        'description': 'Extension for Slicer 4 new version 2'
    })
    updatedExtension = _createOrUpdatePackage(server, 'extension', newParams, _user=user, _app=app_folder)
    # Check the same extension has different metadata
    assert updatedExtension['_id'] == extensions[1]['_id']
    assert updatedExtension['name'] == constants.EXTENSION_PACKAGE_TEMPLATE_NAME.format(**newParams)
    assert updatedExtension['meta'] != extensions[1]['meta']


@pytest.mark.plugin('slicer_package_manager')
def testGetExtensions(server, user, app_folder, release_folder, extensions):
    # Get all the extension of the application
    resp = server.request(
        path='/app/%s/extension' % app_folder['_id'],
        method='GET',
        user=user
    )
    assertStatusOk(resp)
    assert len(resp.json) == len(EXTENSIONS)

    # Get all the extension of the application for Linux
    resp = server.request(
        path='/app/%s/extension' % app_folder['_id'],
        method='GET',
        user=user,
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
        path='/app/%s/extension' % app_folder['_id'],
        method='GET',
        user=user,
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
        path='/app/%s/extension' % app_folder['_id'],
        method='GET',
        user=user,
        params={
            'release_id': release_folder['_id']
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 1

    # Get all the extension of the application which are in the draft release
    draftRelease = list(Folder().childFolders(
        app_folder,
        'Folder',
        user=user,
        filters={'name': constants.DRAFT_RELEASE_NAME}))
    resp = server.request(
        path='/app/%s/extension' % app_folder['_id'],
        method='GET',
        user=user,
        params={
            'release_id': draftRelease[0]['_id']
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 4

    # Get a specific extension by name
    resp = server.request(
        path='/app/%s/extension' % app_folder['_id'],
        params={'extension_name': extensions[1]['name']},
        method='GET',
        user=user,
    )
    assertStatusOk(resp)
    assert resp.json[0]['_id'] == extensions[1]['_id']
    assert resp.json[0]['name'] == extensions[1]['name']

    # Get a specific extension with wrong name
    resp = server.request(
        path='/app/%s/extension' % app_folder['_id'],
        params={'extension_name': 'wrong_name'},
        method='GET',
        user=user,
    )
    assertStatusOk(resp)
    assert len(resp.json) == 0
    assert resp.json == []


@pytest.mark.plugin('slicer_package_manager')
def testDeleteExtensionPackages(server, user, app_folder, release_folder):
    # Create a new extension in the release "_release"
    extension = _createOrUpdatePackage(
        server,
        'extension',
        EXTENSIONS[0]['meta'],
        _user=user,
        _app=app_folder
    )
    assert extension['name'] == EXTENSIONS[0]['name']
    extensions_folder = Folder().load(extension['folderId'], user=user)
    assert ObjectId(extensions_folder['parentId']) == release_folder['_id']
    # Get, delete, and try to re-get the package
    _deletePackages(server, 'extension', extension, _user=user, _app=app_folder)


@pytest.mark.external_data(
    os.path.join(FIXTURE_DIR, PACKAGES[2]['filepath'])
)
@pytest.mark.plugin('slicer_package_manager')
def testUploadAndDownloadPackages(server, user, app_folder, packages, external_data):
    # Try to create the same application package should just get the same one
    package2 = _createOrUpdatePackage(
        server,
        'package',
        PACKAGES[2]['meta'],
        external_data.join(PACKAGES[2]['filepath']),
        _user=user,
        _app=app_folder
    )
    assert package2['name'] == packages[2]['name']


@pytest.mark.plugin('slicer_package_manager')
def testUpdatePackages(server, user, app_folder, packages):
    # Update the same package
    newParams = PACKAGES[1]['meta'].copy()
    newParams.update({
        'repository_url': 'https://AnotherURL.com',
        'repository_type': 'gitlab',
    })
    updatedPackage = _createOrUpdatePackage(server, 'package', newParams, _user=user, _app=app_folder)
    # Check the same package has different metadata
    assert updatedPackage['_id'] == packages[1]['_id']
    assert updatedPackage['name'] == constants.APPLICATION_PACKAGE_TEMPLATE_NAME.format(**newParams)
    assert updatedPackage['meta'] != packages[1]['meta']


@pytest.mark.plugin('slicer_package_manager')
def testGetPackages(server, user, app_folder, release_folder, packages):
    # Get all the package of the application
    resp = server.request(
        path='/app/%s/package' % app_folder['_id'],
        method='GET',
        user=user
    )
    assertStatusOk(resp)
    assert len(resp.json) == 3

    # Get all the package of the application for Linux
    resp = server.request(
        path='/app/%s/package' % app_folder['_id'],
        method='GET',
        user=user,
        params={
            'os': 'linux'
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 1
    assert resp.json[0]['meta']['os'] == 'linux'

    # Get all the package of the application for Linux and amd64 architecture
    resp = server.request(
        path='/app/%s/package' % app_folder['_id'],
        method='GET',
        user=user,
        params={
            'os': 'macosx',
            'arch': 'i386'
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 0

    # Get all the package of the application which are in "release1"
    resp = server.request(
        path='/app/%s/package' % app_folder['_id'],
        method='GET',
        user=user,
        params={
            'release_id_or_name': release_folder['_id']
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 1

    # Get all the package of the application which are in the draft release
    draftRelease = list(Folder().childFolders(
        app_folder,
        'Folder',
        user=user,
        filters={'name': constants.DRAFT_RELEASE_NAME}))
    resp = server.request(
        path='/app/%s/package' % app_folder['_id'],
        method='GET',
        user=user,
        params={
            'release_id_or_name': draftRelease[0]['_id']
        }
    )
    assertStatusOk(resp)
    assert len(resp.json) == 2

    # Get a specific package by name
    resp = server.request(
        path='/app/%s/package' % app_folder['_id'],
        params={'package_name': packages[1]['name']},
        method='GET',
        user=user,
    )
    assertStatusOk(resp)
    assert resp.json[0]['_id'] == packages[1]['_id']
    assert resp.json[0]['name'] == packages[1]['name']

    # Get a specific extension with wrong name
    resp = server.request(
        path='/app/%s/package' % app_folder['_id'],
        params={'package_name': 'wrong_name'},
        method='GET',
        user=user,
    )
    assertStatusOk(resp)
    assert len(resp.json) == 0
    assert resp.json == []


@pytest.mark.plugin('slicer_package_manager')
def testDeleteApplicationPackages(server, user, app_folder, release_folder):
    package = _createOrUpdatePackage(
        server,
        'package',
        PACKAGES[0]['meta'],
        _user=user,
        _app=app_folder
    )
    assert package['name'] == PACKAGES[0]['name']
    assert ObjectId(package['folderId']) == release_folder['_id']

    # Get, delete, and try to re-get the package
    _deletePackages(server, 'package', package, _user=user, _app=app_folder)


@pytest.mark.plugin('slicer_package_manager')
def testDownloadStats(server, user, app_folder, draft_release_revision_folder, packages, extensions):
    # Get the downloadStats
    expectedStats = expectedDownloadStats
    resp = server.request(
        path='/app/%s/downloadstats' % app_folder['_id'],
        method='GET',
        user=user
    )
    assertStatusOk(resp)
    assert resp.json == expectedStats

    # Download multiple time an extension
    ext3_file = list(File().find({'itemId': ObjectId(extensions[3]['_id'])}))
    ext4_file = list(File().find({'itemId': ObjectId(extensions[4]['_id'])}))

    N = 5
    for _idx in range(N):
        _downloadFile(server, ext3_file[0]['_id'], _user=user)
        _downloadFile(server, ext4_file[0]['_id'], _user=user)

    expectedStats['0001']['extensions']['Ext2']['macosx'].update({
        'amd64': N + expectedStats['0001']['extensions']['Ext2']['macosx']['amd64'],
        'i386': N + expectedStats['0001']['extensions']['Ext2']['macosx']['i386']
    })
    resp = server.request(
        path='/app/%s/downloadstats' % app_folder['_id'],
        method='GET',
        user=user
    )
    assertStatusOk(resp)
    assert resp.json == expectedStats

    # The download stats aren't affected by deletion of extension or revision
    # in the default release
    # Delete extensions
    resp = server.request(
        path='/app/%(app_id)s/extension/%(ext_id)s' % {
            'app_id': app_folder['_id'],
            'ext_id': extensions[3]['_id']},
        method='DELETE',
        user=user
    )
    assertStatusOk(resp)
    resp = server.request(
        path='/app/%(app_id)s/extension/%(ext_id)s' % {
            'app_id': app_folder['_id'],
            'ext_id': extensions[4]['_id']},
        method='DELETE',
        user=user
    )
    assertStatusOk(resp)

    # Delete the revision '0000' in the "draft" release
    resp = server.request(
        path='/app/%(app_id)s/release/%(release_id)s' % {
            'app_id': app_folder['_id'],
            'release_id': draft_release_revision_folder['_id']},
        method='DELETE',
        user=user
    )
    assertStatusOk(resp)

    # Check if download Stats are the same
    resp = server.request(
        path='/app/%s/downloadstats' % app_folder['_id'],
        method='GET',
        user=user
    )
    assertStatusOk(resp)
    assert resp.json == expectedStats


@pytest.mark.plugin('slicer_package_manager')
def testGetReleaseFolder(server, user, release_folder, packages, extensions):
    # Release package
    release_package = packages[0]
    assert utilities.getReleaseFolder(release_package)['_id'] == release_folder['_id']

    # Draft package
    draft_package = packages[1]
    assert utilities.getReleaseFolder(draft_package)['name'] == constants.DRAFT_RELEASE_NAME

    # Release extension
    release_extension = extensions[0]
    extensions_folder = Folder().load(release_extension['folderId'], user=user)
    assert ObjectId(extensions_folder['parentId']) == release_folder['_id']
    assert utilities.getReleaseFolder(release_extension)['_id'] == release_folder['_id']

    # Draft extension
    draft_extension = extensions[1]
    assert utilities.getReleaseFolder(draft_extension)['name'] == constants.DRAFT_RELEASE_NAME


@pytest.mark.plugin('slicer_package_manager')
def testIsApplicationFolder(server, app_folder, release_folder, draft_release_folder, draft_release_revision_folder):
    assert utilities.isApplicationFolder(app_folder)
    assert not utilities.isApplicationFolder(release_folder)
    assert not utilities.isApplicationFolder(draft_release_folder)
    assert not utilities.isApplicationFolder(draft_release_revision_folder)


@pytest.mark.plugin('slicer_package_manager')
def testIsReleaseFolder(server, app_folder, release_folder, draft_release_folder, draft_release_revision_folder):
    assert not utilities.isReleaseFolder(app_folder)
    assert utilities.isReleaseFolder(release_folder)
    assert not utilities.isReleaseFolder(draft_release_folder)
    assert utilities.isReleaseFolder(draft_release_revision_folder)


@pytest.mark.plugin('slicer_package_manager')
def testIsDraftReleaseFolder(server, app_folder, release_folder, draft_release_folder, draft_release_revision_folder):
    assert not utilities.isDraftReleaseFolder(app_folder)
    assert not utilities.isDraftReleaseFolder(release_folder)
    assert not utilities.isDraftReleaseFolder(draft_release_folder)
    assert utilities.isDraftReleaseFolder(draft_release_revision_folder)


@pytest.mark.parametrize(
    "action,method,src_folder,dest_folder,items,release_before,release_after",
    [
        (
            'copy',
            'POST',
            pytest.lazy_fixture('draft_release_revision_folder'),
            pytest.lazy_fixture('release_folder'),
            pytest.lazy_fixture('draft_packages'),
            None,
            RELEASES[0]['name']
        ),
        (
            'copy',
            'POST',
            pytest.lazy_fixture('release_folder'),
            pytest.lazy_fixture('draft_release_revision_folder'),
            pytest.lazy_fixture('release_packages'),
            RELEASES[0]['name'],
            None
        ),
        (
            'move',
            'PUT',
            pytest.lazy_fixture('draft_release_revision_folder'),
            pytest.lazy_fixture('release_folder'),
            pytest.lazy_fixture('draft_packages'),
            None,
            RELEASES[0]['name']
        ),
        (
            'move',
            'PUT',
            pytest.lazy_fixture('release_folder'),
            pytest.lazy_fixture('draft_release_revision_folder'),
            pytest.lazy_fixture('release_packages'),
            RELEASES[0]['name'],
            None
        ),
    ],
    ids=[
        'copy_package_from_draft_to_release',
        'copy_package_from_release_to_draft',
        'move_package_from_draft_to_release',
        'move_package_from_release_to_draft'
    ]
)
@pytest.mark.plugin('slicer_package_manager')
def testApplicationPackageMetadataAutoUpdate(
        server, user, action, method, src_folder, dest_folder, items, release_before, release_after):

    item = items[0]

    assert ObjectId(item['folderId']) == src_folder['_id']
    assert item['meta'].get('release', None) == release_before

    resp = server.request(
        path='/resource/%s' % action,
        method=method,
        user=user,
        params={
            'resources': json.dumps({'item': [item['_id']]}),
            'parentType': 'folder',
            'parentId': dest_folder['_id']
        }
    )
    assertStatusOk(resp)

    resp = server.request(
        path='/item',
        method='GET',
        user=user,
        params={
            'folderId': dest_folder['_id'],
            'name': item['name']
        }
    )
    assertStatusOk(resp)
    item_after = resp.json[0]

    for key in ['name', 'size']:
        assert item_after[key] == item[key]

    for key in ['app_id', 'arch', 'baseName', 'os', 'revision']:
        assert item_after['meta'][key] == item['meta'][key]

    assert ObjectId(item_after['folderId']) == dest_folder['_id']
    assert item_after['meta'].get('release', None) == release_after


@pytest.mark.parametrize(
    'build_date,expected_build_date,status_code', [
        (None, None, 200),
        ('2021-06-21 22:00:26', '2021-06-21T22:00:26+00:00', 200),
        ('2021-06-21T22:00:26+0000', '2021-06-21T22:00:26+00:00', 200),
        ('2021-06-21T22:00:26+00:00', '2021-06-21T22:00:26+00:00', 200),
        ('2021-06-21 11:37:36 -0400', '2021-06-21T15:37:36+00:00', 200),
        ('2021-06-23 02:54:11-04:00', '2021-06-23T06:54:11+00:00', 200),
        ('abcdef', None, 400)
    ],
    ids=[
        'default',
        'no-timezone',
        'timezone-without-colon',
        'timezone-with-colon',
        'git-date-iso-local',
        'date-rfc-3339-seconds',
        'invalid'
    ]
)
@pytest.mark.plugin('slicer_package_manager')
def testMetadataBuildDate(build_date, expected_build_date, status_code, server, user, app_folder, draft_release_folder):
    newParams = PACKAGES[0]['meta'].copy()
    if build_date is not None:
        newParams['build_date'] = build_date
    package = _createOrUpdatePackage(
        server,
        'package',
        newParams,
        _user=user,
        _app=app_folder,
        status_code=status_code
    )
    if status_code != 200:
        return
    assert package['name'] == PACKAGES[0]['name']
    assert package['meta'].get('build_date')
    if expected_build_date is not None:
        assert package['meta'].get('build_date') == expected_build_date


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


def _createOrUpdatePackage(server, packageType, params, filePath=None, _user=None, _app=None, status_code=200):
    resp = server.request(
        path='/app/%s/%s' % (_app['_id'], packageType),
        method='POST',
        user=_user,
        params=params)
    assertStatus(resp, status_code)

    if status_code != 200:
        return None

    def _filtered(metadata):
        return {k: v for (k, v) in metadata.items() if k not in (
            'app_id',
            'build_date',
        )}

    # assert every other field (besides unique ones) are identical
    assert _filtered(resp.json['meta']) == _filtered(params)

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

    resp = server.request(
        path='/app/%s/%s' % (_app['_id'], packageType),
        method='GET',
        user=_user,
        params={'%s_id' % packageType: resp.json['_id']}
    )
    assertStatusOk(resp)

    assert len(resp.json) == 1

    return resp.json[0]


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
