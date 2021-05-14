# -*- coding: utf-8 -*-

import pytest
import re
import os
from click.testing import CliRunner
from slicer_package_manager_client.cli import main


APPS = ['App', 'App1', 'App2']

RELEASES = [
    {
        'app_name': APPS[0],
        'name': 'Release',
        'revision': 'r000'
    },
    {
        'app_name': APPS[0],
        'name': 'Release1',
        'revision': 'r001'
    }
]

DRAFT_RELEASES = [
    {
        'revision': 'r002'
    }
]

PACKAGES = [
    {
        'filepath': './file1.txt',
        'app_name': APPS[0],
        'os': 'macosx',
        'arch': 'i386',
        'revision': DRAFT_RELEASES[0]['revision'],
        'repo_type': 'git',
        'repo_url': 'git@github.com:pkg1.git',
        'name': 'pkg1'
    },
    {
        'filepath': './file2.txt',
        'app_name': APPS[0],
        'os': 'macosx',
        'arch': 'amd64',
        'revision': DRAFT_RELEASES[0]['revision'],
        'repo_type': 'git',
        'repo_url': 'git@github.com:pkg2.git',
        'name': 'pkg2'
    },
    {
        'filepath': './file3.txt',
        'app_name': APPS[0],
        'os': 'win',
        'arch': 'i386',
        'revision': DRAFT_RELEASES[0]['revision'],
        'repo_type': 'git',
        'repo_url': 'git@github.com:pkg3.git',
        'name': 'pkg3'
    }
]

EXTENSIONS = [
    {
        'filepath': './file1.txt',
        'app_name': APPS[0],
        'os': 'macosx',
        'arch': 'i386',
        'revision': '000',
        'repo_type': 'git',
        'repo_url': 'git@github.com:ext1.git',
        'name': 'ext1',
        'app_revision': RELEASES[0]['revision']
    },
    {
        'filepath': './file2.txt',
        'app_name': APPS[0],
        'os': 'linux',
        'arch': 'amd64',
        'revision': '001',
        'repo_type': 'git',
        'repo_url': 'git@github.com:ext2.git',
        'name': 'ext2',
        'app_revision': RELEASES[0]['revision']
    },
    {
        'filepath': './file3.txt',
        'app_name': APPS[0],
        'os': 'win',
        'arch': 'amd64',
        'revision': '000',
        'repo_type': 'git',
        'repo_url': 'git@github.com:ext3.git',
        'name': 'ext3',
        'app_revision': DRAFT_RELEASES[0]['revision']
    }
]

CLI_COMMON_ARGS = [
    '--api-url', 'http://localhost:8080/api/v1',
    '--username', 'admin',
    '--password', 'password'
]

def _cli_upload_package(package):
    expected_package_name = getAppPkgName(package['name'], package['os'], package['arch'], package['revision'])

    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['package', 'upload', package['app_name'], package['filepath'],
                '--os', package['os'],
                '--arch', package['arch'],
                '--name', package['name'],
                '--revision', package['revision'],
                '--repo_type', package['repo_type'],
                '--repo_url', package['repo_url']])
    return [CliRunner().invoke(main, cmd), expected_package_name]


def _cli_upload_extension(extension):
    cmd = list(CLI_COMMON_ARGS)
    expected_package_name = getExtPkgName(
        extension['name'], extension['os'], extension['arch'], extension['revision'], extension['app_revision'])
    cmd.extend(['extension', 'upload', extension['app_name'], extension['filepath'],
                '--os', extension['os'],
                '--arch', extension['arch'],
                '--name', extension['name'],
                '--revision', extension['revision'],
                '--app_revision', extension['app_revision'],
                '--repo_type', extension['repo_type'],
                '--repo_url', extension['repo_url']])
    return [CliRunner().invoke(main, cmd), expected_package_name]


@pytest.mark.vcr()
@pytest.fixture(autouse=True)
def TearDown(server):
    yield
    for idx in range(len(APPS)):
        cmd = list(CLI_COMMON_ARGS)
        cmd.extend(['app', 'delete', APPS[idx]])
        CliRunner().invoke(main, cmd)


@pytest.mark.vcr()
@pytest.fixture
def apps(server):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['app', 'create', APPS[0]])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(APPS[0]), res.output)
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['app', 'create', APPS[1]])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(APPS[1]), res.output)
    yield


@pytest.mark.vcr()
@pytest.fixture
def releases(server):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['release', 'create', RELEASES[1]['app_name'], RELEASES[1]['name'], RELEASES[1]['revision']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) CREATED" % (RELEASES[1]['name'], RELEASES[1]['revision']), res.output)
    yield


@pytest.mark.vcr()
@pytest.fixture
def packages(server, apps, files):
    res = _cli_upload_package(PACKAGES[0])[0]
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getAppPkgName(PACKAGES[0]['name'], PACKAGES[0]['os'], PACKAGES[0]['arch'], PACKAGES[0]['revision'])
    ), res.output)

    res = _cli_upload_package(PACKAGES[1])[0]
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getAppPkgName(PACKAGES[1]['name'], PACKAGES[1]['os'], PACKAGES[1]['arch'], PACKAGES[1]['revision'])
    ), res.output)

    res = _cli_upload_package(PACKAGES[2])[0]
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getAppPkgName(PACKAGES[2]['name'], PACKAGES[2]['os'], PACKAGES[2]['arch'], PACKAGES[2]['revision'])
    ), res.output)


@pytest.mark.vcr()
@pytest.fixture
def extensions(server, apps, files):
    [res, name1] = _cli_upload_extension(EXTENSIONS[0])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    [res, name2] = _cli_upload_extension(EXTENSIONS[1])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)

    [res, name3] = _cli_upload_extension(EXTENSIONS[2])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name3), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateAppCLI(server):

    def _create(app):
        cmd = list(CLI_COMMON_ARGS)
        cmd.extend(['app', 'create', APPS[2]])
        return CliRunner().invoke(main, cmd)

    res = _create(APPS[2])
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(APPS[2]), res.output)

    # Try to create the same app
    res = _create(APPS[2])
    assert res.exit_code == 0
    assert re.match(r"The Application \"%s\" already exist\." % re.escape(APPS[2]),
                    res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListAppCLI(server, apps):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['app', 'list'])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *\w{24}" % re.escape(APPS[0]), res.output)
    assert re.search(r"%s *\w{24}" % re.escape(APPS[1]), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteAppCLI(server, apps):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['app', 'delete', APPS[0]])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s \(\w{24}\) DELETED" % re.escape(APPS[0]), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateReleaseCLI(server, apps):

    def _create(release):
        cmd = list(CLI_COMMON_ARGS)
        cmd.extend(['release', 'create', release['app_name'], release['name'], release['revision']])
        return CliRunner().invoke(main, cmd)

    res = _create(RELEASES[0])
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) CREATED" % (RELEASES[0]['name'], RELEASES[0]['revision']), res.output)

    # Try to create the same release
    res = _create(RELEASES[0])
    assert res.exit_code == 0
    assert re.match(r"The release \"%s\" already exist\." % re.escape(RELEASES[0]['name']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListReleaseCLI(server, apps, releases):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['release', 'list', RELEASES[1]['app_name']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *\w{24}" % (RELEASES[1]['revision'], RELEASES[1]['name']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteReleaseCLI(server, apps, releases):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['release', 'delete', RELEASES[1]['app_name'], RELEASES[1]['name']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (RELEASES[1]['name'], RELEASES[1]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testlistDraftCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['draft', 'list', APPS[0]])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *\w{24}" % ('r002', 'r002'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteDraftCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['draft', 'delete', APPS[0], 'r002'])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s %s \(\w{24}\) DELETED" % ('r002', 'r002'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadPackagesCLI(server, apps, files):
    [res, name1] = _cli_upload_package(PACKAGES[0])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    [res, name2] = _cli_upload_package(PACKAGES[1])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)

    [res, name3] = _cli_upload_package(PACKAGES[2])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name3), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListPackagesCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    name1 = getAppPkgName(PACKAGES[0]['name'], PACKAGES[0]['os'], PACKAGES[0]['arch'], PACKAGES[0]['revision'])
    name2 = getAppPkgName(PACKAGES[1]['name'], PACKAGES[1]['os'], PACKAGES[1]['arch'], PACKAGES[1]['revision'])
    name3 = getAppPkgName(PACKAGES[2]['name'], PACKAGES[2]['os'], PACKAGES[2]['arch'], PACKAGES[2]['revision'])
    cmd.extend(['package', 'list', APPS[0]])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *%s *\w{24}" % (PACKAGES[0]['revision'], name1, 'draft'), res.output)
    assert re.search(r"%s *%s *%s *\w{24}" % (PACKAGES[1]['revision'], name2, 'draft'), res.output)
    assert re.search(r"%s *%s *%s *\w{24}" % (PACKAGES[2]['revision'], name3, 'draft'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeletePackagesCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    name = getAppPkgName(PACKAGES[2]['name'], PACKAGES[2]['os'], PACKAGES[2]['arch'], PACKAGES[2]['revision'])
    cmd.extend(['package', 'delete', PACKAGES[2]['app_name'], name])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (name, PACKAGES[2]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDownloadPackagesCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    name = getAppPkgName(PACKAGES[0]['name'], PACKAGES[0]['os'], PACKAGES[0]['arch'], PACKAGES[0]['revision'])
    cmd.extend(['package', 'download', PACKAGES[0]['app_name'], name])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) DOWNLOADED \[.*]" % name, res.output)
    os.remove('%s.txt' % name)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadExtensionsCLI(server, apps, files):
    [res, name1] = _cli_upload_extension(EXTENSIONS[0])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    [res, name2] = _cli_upload_extension(EXTENSIONS[1])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListExtensionsCLI(server, extensions):
    cmd = list(CLI_COMMON_ARGS)
    name1 = getExtPkgName(EXTENSIONS[0]['name'], EXTENSIONS[0]['os'], EXTENSIONS[0]['arch'], EXTENSIONS[0]['revision'],
                          EXTENSIONS[0]['app_revision'])
    name2 = getExtPkgName(EXTENSIONS[1]['name'], EXTENSIONS[1]['os'], EXTENSIONS[1]['arch'], EXTENSIONS[1]['revision'],
                          EXTENSIONS[1]['app_revision'])
    name3 = getExtPkgName(EXTENSIONS[2]['name'], EXTENSIONS[2]['os'], EXTENSIONS[2]['arch'], EXTENSIONS[2]['revision'],
                          EXTENSIONS[2]['app_revision'])
    cmd.extend(['extension', 'list', APPS[0], '--all'])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (EXTENSIONS[0]['revision'], name1, 'draft',
                                                  EXTENSIONS[0]['app_revision']), res.output)
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (EXTENSIONS[1]['revision'], name2, 'draft',
                                                  EXTENSIONS[1]['app_revision']), res.output)
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (EXTENSIONS[2]['revision'], name3, 'draft',
                                                  EXTENSIONS[2]['app_revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteExtensionsCLI(server, extensions):
    cmd = list(CLI_COMMON_ARGS)
    name = getExtPkgName(EXTENSIONS[0]['name'], EXTENSIONS[0]['os'], EXTENSIONS[0]['arch'], EXTENSIONS[0]['revision'],
                         EXTENSIONS[0]['app_revision'])
    cmd.extend(['extension', 'delete', EXTENSIONS[0]['app_name'], name])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (name, EXTENSIONS[0]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDownloadExtensionsCLI(server, extensions):
    cmd = list(CLI_COMMON_ARGS)
    name = getExtPkgName(EXTENSIONS[0]['name'], EXTENSIONS[0]['os'], EXTENSIONS[0]['arch'], EXTENSIONS[0]['revision'],
                         EXTENSIONS[0]['app_revision'])
    cmd.extend(['extension', 'download', EXTENSIONS[0]['app_name'], name])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) DOWNLOADED \[.*]" % name, res.output)
    os.remove('%s.txt' % name)


def getAppPkgName(baseName, os, arch, rev):
    return "%s_%s_%s_%s" % (baseName, os, arch, rev)


def getExtPkgName(baseName, os, arch, rev, app_rev):
    return "%s_%s_%s_%s_%s" % (app_rev, baseName, os, arch, rev)
