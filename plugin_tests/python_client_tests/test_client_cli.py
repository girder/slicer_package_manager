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
@pytest.fixture
def packages(server, apps, files):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['package', 'upload', PACKAGES[0]['app_name'], './file1.txt',
                '--os', PACKAGES[0]['os'],
                '--arch', PACKAGES[0]['arch'],
                '--name', PACKAGES[0]['name'],
                '--revision', PACKAGES[0]['revision'],
                '--repo_type', PACKAGES[0]['repo_type'],
                '--repo_url', PACKAGES[0]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getPkgName(PACKAGES[0]['name'], PACKAGES[0]['os'], PACKAGES[0]['arch'], PACKAGES[0]['revision'])), res.output)

    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['package', 'upload', PACKAGES[1]['app_name'], './file2.txt',
                '--os', PACKAGES[1]['os'],
                '--arch', PACKAGES[1]['arch'],
                '--name', PACKAGES[1]['name'],
                '--revision', PACKAGES[1]['revision'],
                '--repo_type', PACKAGES[1]['repo_type'],
                '--repo_url', PACKAGES[1]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getPkgName(PACKAGES[1]['name'], PACKAGES[1]['os'], PACKAGES[1]['arch'], PACKAGES[1]['revision'])), res.output)

    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['package', 'upload', PACKAGES[2]['app_name'], './file3.txt',
                '--os', PACKAGES[2]['os'],
                '--arch', PACKAGES[2]['arch'],
                '--name', PACKAGES[2]['name'],
                '--revision', PACKAGES[2]['revision'],
                '--repo_type', PACKAGES[2]['repo_type'],
                '--repo_url', PACKAGES[2]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getPkgName(PACKAGES[2]['name'], PACKAGES[2]['os'], PACKAGES[2]['arch'], PACKAGES[2]['revision'])), res.output)


@pytest.mark.vcr()
@pytest.fixture
def extensions(server, apps, files):
    cmd = list(CLI_COMMON_ARGS)
    name1 = getPkgName(EXTENSIONS[0]['name'], EXTENSIONS[0]['os'], EXTENSIONS[0]['arch'], EXTENSIONS[0]['revision'],
                       EXTENSIONS[0]['app_revision'])
    cmd.extend(['extension', 'upload', EXTENSIONS[0]['app_name'], './file1.txt',
                '--os', EXTENSIONS[0]['os'],
                '--arch', EXTENSIONS[0]['arch'],
                '--name', EXTENSIONS[0]['name'],
                '--revision', EXTENSIONS[0]['revision'],
                '--app_revision', EXTENSIONS[0]['app_revision'],
                '--repo_type', EXTENSIONS[0]['repo_type'],
                '--repo_url', EXTENSIONS[0]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    cmd = list(CLI_COMMON_ARGS)
    name2 = getPkgName(EXTENSIONS[1]['name'], EXTENSIONS[1]['os'], EXTENSIONS[1]['arch'], EXTENSIONS[1]['revision'],
                       EXTENSIONS[1]['app_revision'])
    cmd.extend(['extension', 'upload', EXTENSIONS[1]['app_name'], './file2.txt'])
    options = ['--os', EXTENSIONS[1]['os'],
               '--arch', EXTENSIONS[1]['arch'],
               '--name', EXTENSIONS[1]['name'],
               '--revision', EXTENSIONS[1]['revision'],
               '--app_revision', EXTENSIONS[1]['app_revision'],
               '--repo_type', EXTENSIONS[1]['repo_type'],
               '--repo_url', EXTENSIONS[1]['repo_url']]
    cmd.extend(options)
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)

    cmd = list(CLI_COMMON_ARGS)
    name3 = getPkgName(EXTENSIONS[2]['name'], EXTENSIONS[2]['os'], EXTENSIONS[2]['arch'], EXTENSIONS[2]['revision'])
    cmd.extend(['extension', 'upload', EXTENSIONS[2]['app_name'], './file3.txt'])
    options = ['--os', EXTENSIONS[2]['os'],
               '--arch', EXTENSIONS[2]['arch'],
               '--name', EXTENSIONS[2]['name'],
               '--revision', EXTENSIONS[2]['revision'],
               '--app_revision', EXTENSIONS[2]['app_revision'],
               '--repo_type', EXTENSIONS[2]['repo_type'],
               '--repo_url', EXTENSIONS[2]['repo_url']]
    cmd.extend(options)
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name3), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateAppCLI(server):
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['app', 'create', APPS[2]])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(APPS[2]), res.output)

    # Try to create the same app
    res = CliRunner().invoke(main, cmd)
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
    cmd = list(CLI_COMMON_ARGS)
    cmd.extend(['release', 'create', RELEASES[0]['app_name'], RELEASES[0]['name'], RELEASES[0]['revision']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) CREATED" % (RELEASES[0]['name'], RELEASES[0]['revision']), res.output)
    # Try to create the same release
    res = CliRunner().invoke(main, cmd)
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
    cmd = list(CLI_COMMON_ARGS)
    name1 = getPkgName(PACKAGES[0]['name'], PACKAGES[0]['os'], PACKAGES[0]['arch'], PACKAGES[0]['revision'])
    cmd.extend(['package', 'upload', PACKAGES[0]['app_name'], './file1.txt',
                '--os', PACKAGES[0]['os'],
                '--arch', PACKAGES[0]['arch'],
                '--name', PACKAGES[0]['name'],
                '--revision', PACKAGES[0]['revision'],
                '--repo_type', PACKAGES[0]['repo_type'],
                '--repo_url', PACKAGES[0]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    cmd = list(CLI_COMMON_ARGS)
    name2 = getPkgName(PACKAGES[1]['name'], PACKAGES[1]['os'], PACKAGES[1]['arch'], PACKAGES[1]['revision'])
    cmd.extend(['package', 'upload', PACKAGES[1]['app_name'], './file2.txt',
                '--os', PACKAGES[1]['os'],
                '--arch', PACKAGES[1]['arch'],
                '--name', PACKAGES[1]['name'],
                '--revision', PACKAGES[1]['revision'],
                '--repo_type', PACKAGES[1]['repo_type'],
                '--repo_url', PACKAGES[1]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)

    cmd = list(CLI_COMMON_ARGS)
    name3 = getPkgName(PACKAGES[2]['name'], PACKAGES[2]['os'], PACKAGES[2]['arch'], PACKAGES[2]['revision'])
    cmd.extend(['package', 'upload', PACKAGES[2]['app_name'], './file3.txt',
                '--os', PACKAGES[2]['os'],
                '--arch', PACKAGES[2]['arch'],
                '--name', PACKAGES[2]['name'],
                '--revision', PACKAGES[2]['revision'],
                '--repo_type', PACKAGES[2]['repo_type'],
                '--repo_url', PACKAGES[2]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name3), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListPackagesCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    name1 = getPkgName(PACKAGES[0]['name'], PACKAGES[0]['os'], PACKAGES[0]['arch'], PACKAGES[0]['revision'])
    name2 = getPkgName(PACKAGES[1]['name'], PACKAGES[1]['os'], PACKAGES[1]['arch'], PACKAGES[1]['revision'])
    name3 = getPkgName(PACKAGES[2]['name'], PACKAGES[2]['os'], PACKAGES[2]['arch'], PACKAGES[2]['revision'])
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
    name = getPkgName(PACKAGES[2]['name'], PACKAGES[2]['os'], PACKAGES[2]['arch'], PACKAGES[2]['revision'])
    cmd.extend(['package', 'delete', PACKAGES[2]['app_name'], name])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (name, PACKAGES[2]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDownloadPackagesCLI(server, packages):
    cmd = list(CLI_COMMON_ARGS)
    name = getPkgName(PACKAGES[0]['name'], PACKAGES[0]['os'], PACKAGES[0]['arch'], PACKAGES[0]['revision'])
    cmd.extend(['package', 'download', PACKAGES[0]['app_name'], name])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) DOWNLOADED \[.*]" % name, res.output)
    os.remove('%s.txt' % name)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadExtensionsCLI(server, apps, files):
    cmd = list(CLI_COMMON_ARGS)
    name1 = getPkgName(EXTENSIONS[0]['name'], EXTENSIONS[0]['os'], EXTENSIONS[0]['arch'], EXTENSIONS[0]['revision'],
                       EXTENSIONS[0]['app_revision'])
    cmd.extend(['extension', 'upload', EXTENSIONS[0]['app_name'], './file1.txt',
                '--os', EXTENSIONS[0]['os'],
                '--arch', EXTENSIONS[0]['arch'],
                '--name', EXTENSIONS[0]['name'],
                '--revision', EXTENSIONS[0]['revision'],
                '--app_revision', EXTENSIONS[0]['app_revision'],
                '--repo_type', EXTENSIONS[0]['repo_type'],
                '--repo_url', EXTENSIONS[0]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    cmd = list(CLI_COMMON_ARGS)
    name2 = getPkgName(EXTENSIONS[1]['name'], EXTENSIONS[1]['os'], EXTENSIONS[1]['arch'], EXTENSIONS[1]['revision'],
                       EXTENSIONS[1]['app_revision'])
    cmd.extend(['extension', 'upload', EXTENSIONS[1]['app_name'], './file2.txt',
                '--os', EXTENSIONS[1]['os'],
                '--arch', EXTENSIONS[1]['arch'],
                '--name', EXTENSIONS[1]['name'],
                '--revision', EXTENSIONS[1]['revision'],
                '--app_revision', EXTENSIONS[1]['app_revision'],
                '--repo_type', EXTENSIONS[1]['repo_type'],
                '--repo_url', EXTENSIONS[1]['repo_url']])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListExtensionsCLI(server, extensions):
    cmd = list(CLI_COMMON_ARGS)
    name1 = getPkgName(EXTENSIONS[0]['name'], EXTENSIONS[0]['os'], EXTENSIONS[0]['arch'], EXTENSIONS[0]['revision'],
                       EXTENSIONS[0]['app_revision'])
    name2 = getPkgName(EXTENSIONS[1]['name'], EXTENSIONS[1]['os'], EXTENSIONS[1]['arch'], EXTENSIONS[1]['revision'],
                       EXTENSIONS[1]['app_revision'])
    name3 = getPkgName(EXTENSIONS[2]['name'], EXTENSIONS[2]['os'], EXTENSIONS[2]['arch'], EXTENSIONS[2]['revision'],
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
    name = getPkgName(EXTENSIONS[0]['name'], EXTENSIONS[0]['os'], EXTENSIONS[0]['arch'], EXTENSIONS[0]['revision'],
                      EXTENSIONS[0]['app_revision'])
    cmd.extend(['extension', 'delete', EXTENSIONS[0]['app_name'], name])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (name, EXTENSIONS[0]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDownloadExtensionsCLI(server, extensions):
    cmd = list(CLI_COMMON_ARGS)
    name = getPkgName(EXTENSIONS[0]['name'], EXTENSIONS[0]['os'], EXTENSIONS[0]['arch'], EXTENSIONS[0]['revision'],
                      EXTENSIONS[0]['app_revision'])
    cmd.extend(['extension', 'download', EXTENSIONS[0]['app_name'], name])
    res = CliRunner().invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) DOWNLOADED \[.*]" % name, res.output)
    os.remove('%s.txt' % name)


def getPkgName(baseName, os, arch, rev, app_rev=None):
    if app_rev:
        return "%s_%s_%s_%s_%s" % (app_rev, baseName, os, arch, rev)
    return "%s_%s_%s_%s" % (baseName, os, arch, rev)
