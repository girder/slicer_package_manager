# -*- coding: utf-8 -*-

import time
import os
import pytest

from slicer_package_manager_client import SlicerPackageClient, SlicerPackageManagerError


APPS = ['App', 'App1', 'App2']

RELEASES = [
    {
        'app_name': APPS[0],
        'name': 'Release',
        'revision': 'r000',
        'desc': 'random description 1',
    },
    {
        'app_name': APPS[0],
        'name': 'Release1',
        'revision': 'r001',
        'desc': 'random description 2',
    }
]

DRAFT_RELEASES = [
    {
        'revision': 'extR001'
    },
    {
        'revision': 'extR002'
    }
]

PACKAGES = [
    {
        'filepath': './file1.txt',
        'app_name': APPS[0],
        'os': 'macosx',
        'arch': 'amd64',
        'baseName': 'pkg1',
        'repo_type': 'git',
        'repo_url': 'git@github.com:pkg1.git',
        'revision': RELEASES[0]['revision']
    },
    {
        'filepath': './file2.txt',
        'app_name': APPS[0],
        'os': 'linux',
        'arch': 'amd64',
        'baseName': 'pkg2',
        'repo_type': 'git',
        'repo_url': 'git@github.com:pkg2.git',
        'revision': RELEASES[0]['revision']
    },
    {
        'filepath': './file3.txt',
        'app_name': APPS[0],
        'os': 'win',
        'arch': 'i386',
        'baseName': 'pkg3',
        'repo_type': 'git',
        'repo_url': 'git@github.com:pkg3.git',
        'revision': RELEASES[0]['revision']
    }
]

EXTENSIONS = [
    {
        'filepath': './file1.txt',
        'app_name': APPS[0],
        'os': 'macosx',
        'arch': 'amd64',
        'baseName': 'ext1',
        'repo_type': 'git',
        'repo_url': 'git@github.com:ext1.git',
        'app_revision': DRAFT_RELEASES[0]['revision'],
        'revision': 'r300'
    },
    {
        'filepath': './file2.txt',
        'app_name': APPS[0],
        'os': 'linux',
        'arch': 'amd64',
        'baseName': 'ext2',
        'repo_type': 'git',
        'repo_url': 'git@github.com:ext2.git',
        'app_revision': DRAFT_RELEASES[1]['revision'],
        'revision': 'r301'
    },
    {
        'filepath': './file3.txt',
        'app_name': APPS[0],
        'os': 'win',
        'arch': 'i386',
        'baseName': 'ext3',
        'repo_type': 'git',
        'repo_url': 'git@github.com:ext3.git',
        'app_revision': RELEASES[0]['revision'],
        'revision': 'r302'
    }
]


@pytest.mark.vcr()
@pytest.fixture
def spc(server):
    spc = SlicerPackageClient(apiUrl='http://localhost:8080/api/v1')
    spc.authenticate('admin', 'password')
    yield spc


@pytest.mark.vcr()
@pytest.fixture
def apps(server, spc):
    app1 = spc.createApp(name=APPS[0], desc='random description 1')
    app2 = spc.createApp(name=APPS[1], desc='random description 2')
    yield [app1, app2]


@pytest.mark.vcr()
@pytest.fixture
def releases(server, spc):
    rls1 = spc.createRelease(
        app_name=RELEASES[0]['app_name'],
        name=RELEASES[0]['name'],
        revision=RELEASES[0]['revision'],
        desc=RELEASES[0]['desc'])
    rls2 = spc.createRelease(
        app_name=RELEASES[1]['app_name'],
        name=RELEASES[1]['name'],
        revision=RELEASES[1]['revision'],
        desc=RELEASES[1]['desc'])
    yield [rls1, rls2]


@pytest.mark.vcr()
@pytest.fixture
def packages(server, spc, releases, files):
    pkg1 = spc.uploadApplicationPackage(
        filepath=PACKAGES[0]['filepath'],
        app_name=PACKAGES[0]['app_name'],
        pkg_os=PACKAGES[0]['os'],
        arch=PACKAGES[0]['arch'],
        name=PACKAGES[0]['baseName'],
        repo_type=PACKAGES[0]['repo_type'],
        repo_url=PACKAGES[0]['repo_url'],
        revision='r300')
    time.sleep(0.1)
    pkg2 = spc.uploadApplicationPackage(
        filepath=PACKAGES[1]['filepath'],
        app_name=PACKAGES[1]['app_name'],
        pkg_os=PACKAGES[1]['os'],
        arch=PACKAGES[1]['arch'],
        name=PACKAGES[1]['baseName'],
        repo_type=PACKAGES[1]['repo_type'],
        repo_url=PACKAGES[1]['repo_url'],
        revision='r301')
    time.sleep(0.1)
    pkg3 = spc.uploadApplicationPackage(
        filepath=PACKAGES[2]['filepath'],
        app_name=PACKAGES[2]['app_name'],
        pkg_os=PACKAGES[2]['os'],
        arch=PACKAGES[2]['arch'],
        name=PACKAGES[2]['baseName'],
        repo_type=PACKAGES[2]['repo_type'],
        repo_url=PACKAGES[2]['repo_url'],
        revision=PACKAGES[2]['revision'])
    yield [pkg1, pkg2, pkg3]


@pytest.mark.vcr()
@pytest.fixture
def extensions(server, spc, releases, files):
    ext1 = spc.uploadExtension(
        filepath=EXTENSIONS[0]['filepath'],
        app_name=EXTENSIONS[0]['app_name'],
        ext_os=EXTENSIONS[0]['os'],
        arch=EXTENSIONS[0]['arch'],
        name=EXTENSIONS[0]['baseName'],
        repo_type=EXTENSIONS[0]['repo_type'],
        repo_url=EXTENSIONS[0]['repo_url'],
        app_revision=EXTENSIONS[0]['app_revision'],
        revision=EXTENSIONS[0]['revision'])
    time.sleep(0.1)
    ext2 = spc.uploadExtension(
        filepath=EXTENSIONS[1]['filepath'],
        app_name=EXTENSIONS[1]['app_name'],
        ext_os=EXTENSIONS[1]['os'],
        arch=EXTENSIONS[1]['arch'],
        name=EXTENSIONS[1]['baseName'],
        repo_type=EXTENSIONS[1]['repo_type'],
        repo_url=EXTENSIONS[1]['repo_url'],
        app_revision=EXTENSIONS[1]['app_revision'],
        revision=EXTENSIONS[1]['revision'])
    time.sleep(0.1)
    ext3 = spc.uploadExtension(
        filepath=EXTENSIONS[2]['filepath'],
        app_name=EXTENSIONS[2]['app_name'],
        ext_os=EXTENSIONS[2]['os'],
        arch=EXTENSIONS[2]['arch'],
        name=EXTENSIONS[2]['baseName'],
        repo_type=EXTENSIONS[2]['repo_type'],
        repo_url=EXTENSIONS[2]['repo_url'],
        app_revision=EXTENSIONS[2]['app_revision'],
        revision=EXTENSIONS[2]['revision'])

    yield [ext1, ext2, ext3]


@pytest.mark.vcr()
@pytest.fixture
def files():
    f1 = open('file1.txt', 'w+')
    f1.write('Content of the file number 1')
    f1.close()

    f2 = open('file2.txt', 'w+')
    f2.write('Content of the file number 2')
    f2.close()

    f3 = open('file3.txt', 'w+')
    f3.write('Content of the file number 3')
    f3.close()

    yield ['file1.txt', 'file2.txt', 'file3.txt']

    os.remove('file1.txt')
    os.remove('file2.txt')
    os.remove('file3.txt')


@pytest.mark.vcr()
@pytest.fixture(autouse=True)
def TearDown(server, spc, request):
    yield
    for idx in range(len(APPS)):
        try:
            spc.deleteApp(name=APPS[idx])
        except SlicerPackageManagerError:
            pass


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateApp(server, spc):
    app1 = spc.createApp(name=APPS[2])
    assert app1['name'] == APPS[2]

    # Try to create the same application
    with pytest.raises(Exception) as excinfo:
        spc.createApp(name=APPS[2])
    assert 'The Application "%s" already exist.' % APPS[2] in str(excinfo.value)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListApp(server, spc, apps):
    # List all the app
    app_list = spc.listApp()
    assert len(app_list) == 2
    assert app_list[0]['_id'] == apps[0]['_id']
    assert app_list[1]['_id'] == apps[1]['_id']

    # List one app by name
    app_list = spc.listApp(name=apps[0]['name'])
    assert len(app_list) == 1
    assert app_list[0]['_id'] == apps[0]['_id']


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteApp(server, spc, apps):
    app_list = spc.listApp()
    assert len(app_list) == 2

    deleted_app = spc.deleteApp(name=apps[1]['name'])
    app_list = spc.listApp()
    assert len(app_list) == 1
    assert app_list[0]['_id'] == apps[0]['_id']
    assert deleted_app['_id'] == apps[1]['_id']

    # Try to delete the same deleted app
    with pytest.raises(Exception) as excinfo:
        spc.deleteApp(name=apps[1]['name'])
    assert 'The Application "%s" doesn\'t exist.' % apps[1]['name'] in str(excinfo.value)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateRelease(server, spc, apps):
    release = spc.createRelease(
        app_name=apps[0]['name'], name=RELEASES[0]['name'], revision=RELEASES[0]['revision'])
    assert release['name'] == RELEASES[0]['name']
    assert release['meta']['revision'] == RELEASES[0]['revision']

    # Try to create the same release
    with pytest.raises(Exception) as excinfo:
        spc.createRelease(
            app_name=apps[0]['name'], name=RELEASES[0]['name'], revision=RELEASES[0]['revision'])
    assert 'The release "%s" already exist.' % RELEASES[0]['name'] in str(excinfo.value)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListRelease(server, spc, apps, releases):
    # List all the releases
    release_list = spc.listRelease(app_name=apps[0]['name'])
    assert len(release_list) == 2
    assert release_list[0]['_id'] == releases[1]['_id']
    assert release_list[1]['_id'] == releases[0]['_id']

    # List one release by name
    release_list = spc.listRelease(app_name=apps[0]['name'], name=releases[0]['name'])
    assert release_list['_id'] == releases[0]['_id']


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteRelease(server, spc, apps, releases):
    release_list = spc.listRelease(app_name=apps[0]['name'])
    assert len(release_list) == 2

    deleted_release = spc.deleteRelease(app_name=apps[0]['name'], name=releases[1]['name'])
    release_list = spc.listRelease(app_name=apps[0]['name'])
    assert len(release_list) == 1
    assert release_list[0]['_id'] == releases[0]['_id']
    assert deleted_release['_id'] == releases[1]['_id']

    # Try to delete the same deleted release
    with pytest.raises(Exception) as excinfo:
        spc.deleteRelease(app_name=apps[0]['name'], name=releases[1]['name'])
    assert 'The release "%s" doesn\'t exist.' % releases[1]['name'] in str(excinfo.value)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListDraftRelease(server, spc, apps, packages):
    # List all the draft releases
    draft_list = spc.listDraftRelease(app_name=apps[0]['name'])
    assert len(draft_list) == 2

    # List all the draft releases using an offset
    draft_list = spc.listDraftRelease(app_name=apps[0]['name'], offset=1)
    assert len(draft_list) == 1
    assert draft_list[0]['meta']['revision'] == 'r300'

    # List one draft release by revision
    draft_list = spc.listDraftRelease(app_name=apps[0]['name'], revision='r300')
    assert len(draft_list) == 1
    assert draft_list[0]['meta']['revision'] == 'r300'


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteDraftRelease(server, spc, apps, packages):
    draft_list = spc.listDraftRelease(app_name=apps[0]['name'])
    assert len(draft_list) == 2

    deleted_draft = spc.deleteDraftRelease(app_name=apps[0]['name'], revision='r301')
    draft_list = spc.listDraftRelease(app_name=apps[0]['name'])
    assert len(draft_list) == 1
    assert deleted_draft['meta']['revision'] == 'r301'

    # Try to delete the same deleted draft release
    with pytest.raises(Exception) as excinfo:
        spc.deleteDraftRelease(app_name=apps[0]['name'], revision='r301')
    assert 'The release with the revision "%s" doesn\'t exist.' % 'r301' in str(excinfo.value)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadAndDownloadApplicationPackage(server, spc, apps, releases, files):
    # Upload
    pkg1 = spc.uploadApplicationPackage(
        filepath=PACKAGES[0]['filepath'],
        app_name=apps[0]['name'],
        pkg_os=PACKAGES[0]['os'],
        arch=PACKAGES[0]['arch'],
        name=PACKAGES[0]['baseName'],
        repo_type=PACKAGES[0]['repo_type'],
        repo_url=PACKAGES[0]['repo_url'],
        revision=releases[0]['meta']['revision'])
    assert pkg1['meta']['baseName'] == PACKAGES[0]['baseName']

    pkg2 = spc.uploadApplicationPackage(
        filepath=PACKAGES[1]['filepath'],
        app_name=apps[0]['name'],
        pkg_os=PACKAGES[1]['os'],
        arch=PACKAGES[1]['arch'],
        name=PACKAGES[1]['baseName'],
        repo_type=PACKAGES[1]['repo_type'],
        repo_url=PACKAGES[1]['repo_url'],
        revision=releases[0]['meta']['revision'])
    assert pkg2['meta']['baseName'] == PACKAGES[1]['baseName']

    # Download
    downloaded_pkg1 = spc.downloadApplicationPackage(
        app_name=apps[0]['name'], id_or_name=pkg1['_id'])
    downloaded_pkg1_name = apps[0]['meta']['applicationPackageNameTemplate'].format(
        **PACKAGES[0])
    assert downloaded_pkg1['name'] == downloaded_pkg1_name
    downloaded_pkg2 = spc.downloadApplicationPackage(
        app_name=apps[0]['name'], id_or_name=pkg2['_id'])
    downloaded_pkg2_name = apps[0]['meta']['applicationPackageNameTemplate'].format(
        **PACKAGES[1])
    assert downloaded_pkg2['name'] == downloaded_pkg2_name

    # Compare downloaded files
    downloaded_f1 = open('%s.txt' % downloaded_pkg1_name, 'r')
    f1 = open(files[0], 'r')
    assert downloaded_f1.read() == f1.read()

    downloaded_f2 = open('%s.txt' % downloaded_pkg2_name, 'r')
    f2 = open(files[1], 'r')
    assert downloaded_f2.read() == f2.read()

    f1.close()
    downloaded_f1.close()
    f2.close()
    downloaded_f2.close()

    os.remove('%s.txt' % downloaded_pkg1_name)
    os.remove('%s.txt' % downloaded_pkg2_name)

    # Update an existing package
    spc.uploadApplicationPackage(
        filepath=PACKAGES[1]['filepath'],
        app_name=apps[0]['name'],
        pkg_os=PACKAGES[0]['os'],
        arch=PACKAGES[0]['arch'],
        name=PACKAGES[0]['baseName'],
        repo_type=PACKAGES[0]['repo_type'],
        repo_url=PACKAGES[0]['repo_url'],
        revision=releases[0]['meta']['revision'])
    assert pkg1['meta']['baseName'] == PACKAGES[0]['baseName']
    # Download
    downloaded_pkg1_bis = spc.downloadApplicationPackage(
        app_name=apps[0]['name'], id_or_name=pkg1['_id'])
    downloaded_pkg1_name_bis = apps[0]['meta']['applicationPackageNameTemplate'].format(
        **PACKAGES[0])
    assert downloaded_pkg1_bis['name'] == downloaded_pkg1_name_bis
    # Compare, the file should have changed
    downloaded_f1_bis = open('%s.txt' % downloaded_pkg1_name_bis, 'r')
    f1_bis = open(files[1], 'r')
    assert downloaded_f1_bis.read() == f1_bis.read()

    f1_bis.close()
    downloaded_f1_bis.close()
    os.remove('%s.txt' % downloaded_pkg1_name_bis)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListApplicationPackage(server, spc, apps, releases, packages):
    # List all the application packages
    pkg_list = spc.listApplicationPackage(app_name=apps[0]['name'])
    assert len(pkg_list) == 3

    # List all the application packages from a release
    pkg_list = spc.listApplicationPackage(app_name=apps[0]['name'], release=RELEASES[0]['name'])
    assert len(pkg_list) == 1
    assert pkg_list[0]['_id'] == packages[2]['_id']

    # List with special filters
    pkg_list = spc.listApplicationPackage(app_name=apps[0]['name'], pkg_os='macosx')
    assert len(pkg_list) == 1
    assert pkg_list[0]['meta']['os'] == 'macosx'


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeletePackage(server, spc, apps, packages):
    pkg_list = spc.listApplicationPackage(app_name=apps[0]['name'])
    assert len(pkg_list) == 3

    deleted_pkg = spc.deleteApplicationPackage(
        app_name=apps[0]['name'], id_or_name=packages[0]['name'])
    pkg_list = spc.listApplicationPackage(app_name=apps[0]['name'])
    assert len(pkg_list) == 2
    assert deleted_pkg['_id'] == packages[0]['_id']

    # Try to delete the same deleted package
    with pytest.raises(Exception) as excinfo:
        spc.deleteApplicationPackage(
            app_name=apps[0]['name'], id_or_name=packages[0]['name'])
    assert 'The package "%s" doesn\'t exist.' % packages[0]['name'] in str(excinfo.value)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadAndDownloadExtension(server, spc, apps, releases, files):
    pass
    # Upload
    ext1 = spc.uploadExtension(
        filepath=EXTENSIONS[0]['filepath'],
        app_name=apps[0]['name'],
        ext_os=EXTENSIONS[0]['os'],
        arch=EXTENSIONS[0]['arch'],
        name=EXTENSIONS[0]['baseName'],
        repo_type=EXTENSIONS[0]['repo_type'],
        repo_url=EXTENSIONS[0]['repo_url'],
        app_revision=releases[0]['meta']['revision'],
        revision=EXTENSIONS[0]['revision'])
    assert ext1['meta']['baseName'] == EXTENSIONS[0]['baseName']

    ext2 = spc.uploadExtension(
        filepath=EXTENSIONS[1]['filepath'],
        app_name=apps[0]['name'],
        ext_os=EXTENSIONS[1]['os'],
        arch=EXTENSIONS[1]['arch'],
        name=EXTENSIONS[1]['baseName'],
        repo_type=EXTENSIONS[1]['repo_type'],
        repo_url=EXTENSIONS[1]['repo_url'],
        app_revision=releases[0]['meta']['revision'],
        revision=EXTENSIONS[1]['revision'])
    assert ext2['meta']['baseName'] == EXTENSIONS[1]['baseName']

    # Download
    downloaded_ext1 = spc.downloadExtension(
        app_name=apps[0]['name'], id_or_name=ext1['_id'])
    params1 = EXTENSIONS[0].copy()
    params1['app_revision'] = releases[0]['meta']['revision']
    downloaded_ext1_name = apps[0]['meta']['extensionPackageNameTemplate'].format(
        **params1)
    assert downloaded_ext1['name'] == downloaded_ext1_name
    # Download using a different dir_path
    downloaded_ext2 = spc.downloadExtension(
        app_name=apps[0]['name'], id_or_name=ext2['_id'], dir_path='../')
    params2 = EXTENSIONS[1].copy()
    params2['app_revision'] = releases[0]['meta']['revision']
    downloaded_ext2_name = apps[0]['meta']['extensionPackageNameTemplate'].format(
        **params2)
    assert downloaded_ext2['name'] == downloaded_ext2_name

    # Compare downloaded files
    downloaded_f1 = open('%s.txt' % downloaded_ext1_name, 'r')
    f1 = open(files[0], 'r')
    assert downloaded_f1.read() == f1.read()

    downloaded_f2 = open('../%s.txt' % downloaded_ext2_name, 'r')
    f2 = open(files[1], 'r')
    assert downloaded_f2.read() == f2.read()

    f1.close()
    downloaded_f1.close()
    f2.close()
    downloaded_f2.close()

    os.remove('%s.txt' % downloaded_ext1_name)
    os.remove('../%s.txt' % downloaded_ext2_name)

    # Update an existing package by changing the revision
    spc.uploadExtension(
        filepath=EXTENSIONS[1]['filepath'],
        app_name=apps[0]['name'],
        ext_os=EXTENSIONS[0]['os'],
        arch=EXTENSIONS[0]['arch'],
        name=EXTENSIONS[0]['baseName'],
        repo_type=EXTENSIONS[0]['repo_type'],
        repo_url=EXTENSIONS[0]['repo_url'],
        app_revision=releases[0]['meta']['revision'],
        revision='newRev')
    assert ext1['meta']['baseName'] == EXTENSIONS[0]['baseName']
    # Download
    downloaded_ext1_bis = spc.downloadExtension(
        app_name=apps[0]['name'], id_or_name=ext1['_id'])
    downloaded_ext1_name_bis = apps[0]['meta']['extensionPackageNameTemplate'].format(
        **params1)
    assert downloaded_ext1_bis['name'] != downloaded_ext1_name_bis
    # Compare, the file should have changed
    downloaded_f1_bis = open('%s.txt' % downloaded_ext1_bis['name'], 'r')
    f1_bis = open(files[1], 'r')
    assert downloaded_f1_bis.read() == f1_bis.read()

    f1_bis.close()
    downloaded_f1_bis.close()
    os.remove('%s.txt' % downloaded_ext1_bis['name'])


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListExtension(server, spc, apps, extensions):
    # List all the extension packages from draft release
    ext_list = spc.listExtension(app_name=apps[0]['name'])
    assert len(ext_list) == 2

    # List all the extension packages
    ext_list = spc.listExtension(app_name=apps[0]['name'], all=True)
    assert len(ext_list) == 3

    # List all the extension packages from a release
    ext_list = spc.listExtension(app_name=apps[0]['name'], release=RELEASES[0]['name'])
    assert len(ext_list) == 1
    assert ext_list[0]['_id'] == extensions[2]['_id']

    # List with special filters
    ext_list = spc.listExtension(app_name=apps[0]['name'], ext_os='macosx')
    assert len(ext_list) == 1
    assert ext_list[0]['meta']['os'] == 'macosx'


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteExtension(server, spc, apps, extensions):
    ext_list = spc.listExtension(app_name=apps[0]['name'])
    assert len(ext_list) == 2

    deleted_ext = spc.deleteExtension(
        app_name=apps[0]['name'], id_or_name=extensions[0]['name'])
    ext_list = spc.listExtension(app_name=apps[0]['name'])
    assert len(ext_list) == 1
    assert deleted_ext['_id'] == extensions[0]['_id']

    # Try to delete the same deleted extension
    with pytest.raises(Exception) as excinfo:
        spc.deleteExtension(
            app_name=apps[0]['name'], id_or_name=extensions[0]['name'])
    assert 'The extension "%s" doesn\'t exist.' % extensions[0]['name'] in str(excinfo.value)
