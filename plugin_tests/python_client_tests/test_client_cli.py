# -*- coding: utf-8 -*-

import logging
import os
import pytest
import re

from click.testing import CliRunner
from slicer_package_manager_client.cli import main


APPS = ['App', 'App1', 'App2']

RELEASES = [
    {
        'app_name': APPS[0],
        'name': 'Release',
        'revision': 'r000',
        'version': '1.0',
    },
    {
        'app_name': APPS[0],
        'name': 'Release1',
        'revision': 'r001',
        'version': '2.0',
    }
]

DRAFT_RELEASES = [
    {
        'revision': 'r002',
        'version': '3.0'
    },
    {
        'revision': 'r003',
        'version': '3.0'
    }
]

PACKAGES = [
    {
        'filepath': './file1.txt',
        'app_name': APPS[0],
        'os': 'macosx',
        'arch': 'i386',
        'baseName': 'pkg1',
        'repository_type': 'git',
        'repository_url': 'git@github.com:pkg1.git',
        'revision': DRAFT_RELEASES[0]['revision'],
        'version': DRAFT_RELEASES[0]['version']
    },
    {
        'filepath': './file2.txt',
        'app_name': APPS[0],
        'os': 'macosx',
        'arch': 'amd64',
        'baseName': 'pkg2',
        'repository_type': 'git',
        'repository_url': 'git@github.com:pkg2.git',
        'revision': DRAFT_RELEASES[0]['revision'],
        'version': DRAFT_RELEASES[0]['version']
    },
    {
        'filepath': './file3.txt',
        'app_name': APPS[0],
        'os': 'win',
        'arch': 'i386',
        'baseName': 'pkg3',
        'repository_type': 'git',
        'repository_url': 'git@github.com:pkg3.git',
        'revision': DRAFT_RELEASES[0]['revision'],
        'version': DRAFT_RELEASES[0]['version']
    },
    {
        'filepath': './file4.txt',
        'app_name': APPS[0],
        'os': 'linux',
        'arch': 'amd64',
        'baseName': 'pkg4',
        'repository_type': 'git',
        'repository_url': 'git@github.com:pkg4.git',
        'revision': DRAFT_RELEASES[1]['revision'],
        'version': DRAFT_RELEASES[1]['version']
    }
]

EXTENSIONS = [
    {
        'filepath': './file1.txt',
        'app_name': APPS[0],
        'os': 'macosx',
        'arch': 'i386',
        'baseName': 'ext1',
        'repository_type': 'git',
        'repository_url': 'git@github.com:ext1.git',
        'app_revision': RELEASES[0]['revision'],
        'revision': '000'
    },
    {
        'filepath': './file2.txt',
        'app_name': APPS[0],
        'os': 'linux',
        'arch': 'amd64',
        'baseName': 'ext2',
        'repository_type': 'git',
        'repository_url': 'git@github.com:ext2.git',
        'app_revision': RELEASES[0]['revision'],
        'revision': '001'
    },
    {
        'filepath': './file3.txt',
        'app_name': APPS[0],
        'os': 'win',
        'arch': 'amd64',
        'baseName': 'ext3',
        'repository_type': 'git',
        'repository_url': 'git@github.com:ext3.git',
        'app_revision': DRAFT_RELEASES[0]['revision'],
        'revision': '000'
    },
    {
        'filepath': './file4.txt',
        'app_name': APPS[0],
        'os': 'linux',
        'arch': 'amd64',
        'baseName': 'ext4',
        'repository_type': 'git',
        'repository_url': 'git@github.com:ext4.git',
        'app_revision': DRAFT_RELEASES[1]['revision'],
        'revision': '000'
    }
]

CLI_COMMON_ARGS = [
    '--api-url', 'http://localhost:8080/api/v1',
    '--username', 'admin',
    '--password', 'password'
]


def _cli_runner_invoke(main, cmd):
    res = CliRunner().invoke(main, cmd)
    if res.exit_code != 0:
        logging.error(res.exception)
    return res


def _cli_upload_package(package):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['package', 'upload', package['app_name'], package['filepath'],
                '--os', package['os'],
                '--arch', package['arch'],
                '--name', package['baseName'],
                '--revision', package['revision'],
                '--version', package['version'],
                '--repo_type', package['repository_type'],
                '--repo_url', package['repository_url']])
    if package.get('build_date') is not None:
        cmd.extend(['--build_date', package['build_date']])
    return _cli_runner_invoke(main, cmd)


def _cli_upload_extension(extension):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['extension', 'upload', extension['app_name'], extension['filepath'],
                '--os', extension['os'],
                '--arch', extension['arch'],
                '--name', extension['baseName'],
                '--revision', extension['revision'],
                '--app_revision', extension['app_revision'],
                '--repo_type', extension['repository_type'],
                '--repo_url', extension['repository_url']])
    return _cli_runner_invoke(main, cmd)


@pytest.mark.vcr()
@pytest.fixture(autouse=True)
def TearDown(server):
    yield
    for idx in range(len(APPS)):
        cmd = list(CLI_COMMON_ARGS)
        cmd.extend(['app', 'delete', APPS[idx]])
        _cli_runner_invoke(main, cmd)


@pytest.mark.vcr()
@pytest.fixture
def apps(server):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['app', 'create', APPS[0]])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(APPS[0]), res.output)
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['app', 'create', APPS[1]])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(APPS[1]), res.output)
    yield


@pytest.mark.vcr()
@pytest.fixture
def releases(server):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['release', 'create', RELEASES[1]['app_name'], RELEASES[1]['name'], RELEASES[1]['revision']])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) CREATED" % (RELEASES[1]['name'], RELEASES[1]['revision']), res.output)
    yield


@pytest.mark.vcr()
@pytest.fixture
def packages(server, apps, files):
    res = _cli_upload_package(PACKAGES[0])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (getAppPkgName(PACKAGES[0])), res.output)

    res = _cli_upload_package(PACKAGES[1])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (getAppPkgName(PACKAGES[1])), res.output)

    res = _cli_upload_package(PACKAGES[2])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (getAppPkgName(PACKAGES[2])), res.output)

    res = _cli_upload_package(PACKAGES[3])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (getAppPkgName(PACKAGES[3])), res.output)


@pytest.mark.vcr()
@pytest.fixture
def extensions(server, apps, files):
    res = _cli_upload_extension(EXTENSIONS[0])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getExtPkgName(EXTENSIONS[0])), res.output)

    res = _cli_upload_extension(EXTENSIONS[1])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getExtPkgName(EXTENSIONS[1])), res.output)

    res = _cli_upload_extension(EXTENSIONS[2])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getExtPkgName(EXTENSIONS[2])), res.output)

    res = _cli_upload_extension(EXTENSIONS[3])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getExtPkgName(EXTENSIONS[3])), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateAppCLI(server):

    def _create(app):
        cmd = list(CLI_COMMON_ARGS)
        cmd.extend(['app', 'create', APPS[2]])
        return _cli_runner_invoke(main, cmd)

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
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *\w{24}" % re.escape(APPS[0]), res.output)
    assert re.search(r"%s *\w{24}" % re.escape(APPS[1]), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteAppCLI(server, apps):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['app', 'delete', APPS[0]])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s \(\w{24}\) DELETED" % re.escape(APPS[0]), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateReleaseCLI(server, apps):

    def _create(release):
        cmd = list(CLI_COMMON_ARGS)
        cmd.extend(['release', 'create', release['app_name'], release['name'], release['revision']])
        return _cli_runner_invoke(main, cmd)

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
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *\w{24}" % (RELEASES[1]['revision'], RELEASES[1]['name']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteReleaseCLI(server, apps, releases):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['release', 'delete', RELEASES[1]['app_name'], RELEASES[1]['name']])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (RELEASES[1]['name'], RELEASES[1]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testlistDraftCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['draft', 'list', APPS[0]])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *\w{24}" % ('r002', 'r002'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListDraftWithLimitCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['draft', 'list', APPS[0], '--limit', '1'])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *\w{24}" % ('r003', 'r003'), res.output)
    assert not re.search(r"%s *%s *\w{24}" % ('r002', 'r002'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteDraftCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['draft', 'delete', APPS[0], 'r002'])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s %s \(\w{24}\) DELETED" % ('r002', 'r002'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadPackagesCLI(server, apps, files):
    res = _cli_upload_package(PACKAGES[0])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getAppPkgName(PACKAGES[0])), res.output)

    res = _cli_upload_package(PACKAGES[1])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getAppPkgName(PACKAGES[1])), res.output)

    res = _cli_upload_package(PACKAGES[2])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getAppPkgName(PACKAGES[2])), res.output)


@pytest.mark.parametrize(
    'build_date,exit_code', [
        ('2021-06-21T00:00:00+00:00', 0),
        ('abcdef', 1)
    ],
    ids=[
        'timezone',
        'invalid'
    ]
)
@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadPackagesWithBuildDateCLI(build_date, exit_code, server, apps, files):
    package = PACKAGES[0].copy()
    package['build_date'] = build_date
    res = _cli_upload_package(package)
    assert res.exit_code == exit_code
    if exit_code != 0:
        return
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getAppPkgName(package)), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListPackagesCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['package', 'list', APPS[0]])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0

    name = getAppPkgName(PACKAGES[0])
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (
        PACKAGES[0]['revision'], PACKAGES[0]['version'], name, 'draft'), res.output)

    name = getAppPkgName(PACKAGES[1])
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (
        PACKAGES[1]['revision'], PACKAGES[1]['version'], name, 'draft'), res.output)

    name = getAppPkgName(PACKAGES[2])
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (
        PACKAGES[2]['revision'], PACKAGES[2]['version'], name, 'draft'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeletePackagesCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    name = getAppPkgName(PACKAGES[2])
    cmd.extend(['package', 'delete', PACKAGES[2]['app_name'], name])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (name, PACKAGES[2]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDownloadPackagesCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    name = getAppPkgName(PACKAGES[0])
    cmd.extend(['package', 'download', PACKAGES[0]['app_name'], name])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) DOWNLOADED \[.*]" % name, res.output)
    os.remove('%s.txt' % name)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadExtensionsCLI(server, apps, files):
    res = _cli_upload_extension(EXTENSIONS[0])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getExtPkgName(EXTENSIONS[0])), res.output)

    res = _cli_upload_extension(EXTENSIONS[1])
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(getExtPkgName(EXTENSIONS[1])), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListExtensionsCLI(server, extensions):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['extension', 'list', APPS[0], '--all'])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0

    name = getExtPkgName(EXTENSIONS[0])
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (EXTENSIONS[0]['revision'], name, 'draft',
                                                  EXTENSIONS[0]['app_revision']), res.output)

    name = getExtPkgName(EXTENSIONS[1])
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (EXTENSIONS[1]['revision'], name, 'draft',
                                                  EXTENSIONS[1]['app_revision']), res.output)

    name = getExtPkgName(EXTENSIONS[2])
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (EXTENSIONS[2]['revision'], name, 'draft',
                                                  EXTENSIONS[2]['app_revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteExtensionsCLI(server, extensions):
    cmd = list(CLI_COMMON_ARGS)
    name = getExtPkgName(EXTENSIONS[0])
    cmd.extend(['extension', 'delete', EXTENSIONS[0]['app_name'], name])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (name, EXTENSIONS[0]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDownloadExtensionsCLI(server, extensions):
    cmd = list(CLI_COMMON_ARGS)
    name = getExtPkgName(EXTENSIONS[0])
    cmd.extend(['extension', 'download', EXTENSIONS[0]['app_name'], name])
    res = _cli_runner_invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) DOWNLOADED \[.*]" % name, res.output)
    os.remove('%s.txt' % name)


def getAppPkgName(package):
    return "{baseName}_{os}_{arch}_{revision}".format(**package)


def getExtPkgName(extension):
    return "{app_revision}_{baseName}_{os}_{arch}_{revision}".format(**extension)
