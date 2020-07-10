# -*- coding: utf-8 -*-

import pytest
import re
import os
from click.testing import CliRunner
from slicer_package_manager_client.cli import main


app_name = ['App', 'App1', 'App2']
rls = [{
    'name': 'Release',
    'revision': 'r000'
}, {
    'name': 'Release1',
    'revision': 'r001'
}]
pkgs = [{
    'os': 'macosx',
    'arch': 'i386',
    'revision': 'r002',
    'repo_type': 'git',
    'repo_url': 'git@github.com:pkg1.git',
    'name': 'pkg1'
}, {
    'os': 'macosx',
    'arch': 'amd64',
    'revision': 'r002',
    'repo_type': 'git',
    'repo_url': 'git@github.com:pkg2.git',
    'name': 'pkg2'
}, {
    'os': 'win',
    'arch': 'i386',
    'revision': 'r002',
    'repo_type': 'git',
    'repo_url': 'git@github.com:pkg3.git',
    'name': 'pkg3'
}]
exts = [{
    'os': 'macosx',
    'arch': 'i386',
    'revision': '000',
    'repo_type': 'git',
    'repo_url': 'git@github.com:ext1.git',
    'name': 'ext1',
    'app_revision': 'r000'
}, {
    'os': 'linux',
    'arch': 'amd64',
    'revision': '001',
    'repo_type': 'git',
    'repo_url': 'git@github.com:ext2.git',
    'name': 'ext2',
    'app_revision': 'r000'
}, {
    'os': 'win',
    'arch': 'amd64',
    'revision': '000',
    'repo_type': 'git',
    'repo_url': 'git@github.com:ext3.git',
    'name': 'ext3',
    'app_revision': 'r002'
}]


@pytest.mark.vcr()
@pytest.fixture
def runner():
    yield CliRunner()


@pytest.mark.vcr()
@pytest.fixture
def spc(server, runner):
    yield ['--api-url', 'http://localhost:8080/api/v1', '--username', 'admin',
           '--password', 'password']


@pytest.mark.vcr()
@pytest.yield_fixture(autouse=True)
def TearDown(server, runner, spc):
    yield
    for idx in range(len(app_name)):
        cmd = list(spc)
        cmd.extend(['app', 'delete', app_name[idx]])
        runner.invoke(main, cmd)


@pytest.mark.vcr()
@pytest.fixture
def apps(server, runner, spc):
    cmd = list(spc)
    cmd.extend(['app', 'create', app_name[0]])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(app_name[0]), res.output)
    cmd = list(spc)
    cmd.extend(['app', 'create', app_name[1]])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(app_name[1]), res.output)
    yield


@pytest.mark.vcr()
@pytest.fixture
def rl(server, runner, spc):
    cmd = list(spc)
    cmd.extend(['release', 'create', app_name[0], rls[1]['name'], rls[1]['revision']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) CREATED" % (rls[1]['name'], rls[1]['revision']), res.output)
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
def pkg(server, runner, spc, apps, files):
    cmd = list(spc)
    cmd.extend(['package', 'upload', app_name[0], './file1.txt', '--os', pkgs[0]['os'],
                '--arch', pkgs[0]['arch'], '--name', pkgs[0]['name'], '--revision',
                pkgs[0]['revision'], '--repo_type', pkgs[0]['repo_type'], '--repo_url',
                pkgs[0]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getPkgName(pkgs[0]['name'], pkgs[0]['os'], pkgs[0]['arch'], pkgs[0]['revision'])),
        res.output)

    cmd = list(spc)
    cmd.extend(['package', 'upload', app_name[0], './file2.txt', '--os', pkgs[1]['os'],
                '--arch', pkgs[1]['arch'], '--name', pkgs[1]['name'], '--revision',
                pkgs[1]['revision'], '--repo_type', pkgs[1]['repo_type'], '--repo_url',
                pkgs[1]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getPkgName(pkgs[1]['name'], pkgs[1]['os'], pkgs[1]['arch'], pkgs[1]['revision'])),
        res.output)

    cmd = list(spc)
    cmd.extend(['package', 'upload', app_name[0], './file3.txt', '--os', pkgs[2]['os'],
                '--arch', pkgs[2]['arch'], '--name', pkgs[2]['name'], '--revision',
                pkgs[2]['revision'], '--repo_type', pkgs[2]['repo_type'], '--repo_url',
                pkgs[2]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % (
        getPkgName(pkgs[2]['name'], pkgs[2]['os'], pkgs[2]['arch'], pkgs[2]['revision'])),
        res.output)


@pytest.mark.vcr()
@pytest.fixture
def ext(server, runner, spc, apps, files):
    cmd = list(spc)
    name1 = getPkgName(exts[0]['name'], exts[0]['os'], exts[0]['arch'], exts[0]['revision'],
                       exts[0]['app_revision'])
    cmd.extend(['extension', 'upload', app_name[0], './file1.txt',
                '--os', exts[0]['os'], '--arch', exts[0]['arch'], '--name', exts[0]['name'],
                '--revision', exts[0]['revision'], '--app_revision', exts[0]['app_revision'],
                '--repo_type', exts[0]['repo_type'], '--repo_url', exts[0]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    cmd = list(spc)
    name2 = getPkgName(exts[1]['name'], exts[1]['os'], exts[1]['arch'], exts[1]['revision'],
                       exts[1]['app_revision'])
    cmd.extend(['extension', 'upload', app_name[0], './file2.txt'])
    options = ['--os', exts[1]['os'], '--arch', exts[1]['arch'], '--name', exts[1]['name'],
               '--revision', exts[1]['revision'], '--app_revision', exts[1]['app_revision'],
               '--repo_type', exts[1]['repo_type'], '--repo_url', exts[1]['repo_url']]
    cmd.extend(options)
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)

    cmd = list(spc)
    name3 = getPkgName(exts[2]['name'], exts[2]['os'], exts[2]['arch'], exts[2]['revision'])
    cmd.extend(['extension', 'upload', app_name[0], './file3.txt'])
    options = ['--os', exts[2]['os'], '--arch', exts[2]['arch'], '--name', exts[2]['name'],
               '--revision', exts[2]['revision'], '--app_revision', exts[2]['app_revision'],
               '--repo_type', exts[2]['repo_type'], '--repo_url', exts[2]['repo_url']]
    cmd.extend(options)
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name3), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateAppCLI(server, runner, spc):
    cmd = list(spc)
    cmd.extend(['app', 'create', app_name[2]])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"\w{24} \(%s\) CREATED" % re.escape(app_name[2]), res.output)

    # Try to create the same app
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"The Application \"%s\" already exist\." % re.escape(app_name[2]),
                    res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListAppCLI(server, runner, spc, apps):
    cmd = list(spc)
    cmd.extend(['app', 'list'])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *\w{24}" % re.escape(app_name[0]), res.output)
    assert re.search(r"%s *\w{24}" % re.escape(app_name[1]), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteAppCLI(server, runner, spc, apps):
    cmd = list(spc)
    cmd.extend(['app', 'delete', app_name[0]])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s \(\w{24}\) DELETED" % re.escape(app_name[0]), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testCreateReleaseCLI(server, runner, spc, apps):
    cmd = list(spc)
    cmd.extend(['release', 'create', app_name[0], rls[0]['name'], rls[0]['revision']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) CREATED" % (rls[0]['name'], rls[0]['revision']), res.output)
    # Try to create the same release
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"The release \"%s\" already exist\." % re.escape(rls[0]['name']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListReleaseCLI(server, runner, spc, apps, rl):
    cmd = list(spc)
    cmd.extend(['release', 'list', app_name[0]])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *\w{24}" % (rls[1]['revision'], rls[1]['name']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteReleaseCLI(server, runner, spc, apps, rl):
    cmd = list(spc)
    cmd.extend(['release', 'delete', app_name[0], rls[1]['name']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (rls[1]['name'], rls[1]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testlistDraftCLI(server, runner, spc, pkg):
    cmd = list(spc)
    cmd.extend(['draft', 'list', app_name[0]])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *\w{24}" % ('r002', 'r002'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteDraftCLI(server, runner, spc, pkg):
    cmd = list(spc)
    cmd.extend(['draft', 'delete', app_name[0], 'r002'])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s %s \(\w{24}\) DELETED" % ('r002', 'r002'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadPackagesCLI(server, runner, spc, apps, files):
    cmd = list(spc)
    name1 = getPkgName(pkgs[0]['name'], pkgs[0]['os'], pkgs[0]['arch'], pkgs[0]['revision'])
    cmd.extend(['package', 'upload', app_name[0], './file1.txt', '--os', pkgs[0]['os'], '--arch',
                pkgs[0]['arch'], '--name', pkgs[0]['name'], '--revision', pkgs[0]['revision'],
                '--repo_type', pkgs[0]['repo_type'], '--repo_url', pkgs[0]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    cmd = list(spc)
    name2 = getPkgName(pkgs[1]['name'], pkgs[1]['os'], pkgs[1]['arch'], pkgs[1]['revision'])
    cmd.extend(['package', 'upload', app_name[0], './file2.txt', '--os', pkgs[1]['os'], '--arch',
                pkgs[1]['arch'], '--name', pkgs[1]['name'], '--revision', pkgs[1]['revision'],
                '--repo_type', pkgs[1]['repo_type'], '--repo_url', pkgs[1]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)

    cmd = list(spc)
    name3 = getPkgName(pkgs[2]['name'], pkgs[2]['os'], pkgs[2]['arch'], pkgs[2]['revision'])
    cmd.extend(['package', 'upload', app_name[0], './file3.txt', '--os', pkgs[2]['os'],
                '--arch', pkgs[2]['arch'], '--name', pkgs[2]['name'], '--revision',
                pkgs[2]['revision'], '--repo_type', pkgs[2]['repo_type'], '--repo_url',
                pkgs[2]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name3), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListPackagesCLI(server, runner, spc, pkg):
    cmd = list(spc)
    name1 = getPkgName(pkgs[0]['name'], pkgs[0]['os'], pkgs[0]['arch'], pkgs[0]['revision'])
    name2 = getPkgName(pkgs[1]['name'], pkgs[1]['os'], pkgs[1]['arch'], pkgs[1]['revision'])
    name3 = getPkgName(pkgs[2]['name'], pkgs[2]['os'], pkgs[2]['arch'], pkgs[2]['revision'])
    cmd.extend(['package', 'list', app_name[0]])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *%s *\w{24}" % (pkgs[0]['revision'], name1, 'draft'), res.output)
    assert re.search(r"%s *%s *%s *\w{24}" % (pkgs[1]['revision'], name2, 'draft'), res.output)
    assert re.search(r"%s *%s *%s *\w{24}" % (pkgs[2]['revision'], name3, 'draft'), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeletePackagesCLI(server, runner, spc, pkg):
    cmd = list(spc)
    name = getPkgName(pkgs[2]['name'], pkgs[2]['os'], pkgs[2]['arch'], pkgs[2]['revision'])
    cmd.extend(['package', 'delete', app_name[0], name])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (name, pkgs[2]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDownloadPackagesCLI(server, runner, spc, pkg):
    cmd = list(spc)
    name = getPkgName(pkgs[0]['name'], pkgs[0]['os'], pkgs[0]['arch'], pkgs[0]['revision'])
    cmd.extend(['package', 'download', app_name[0], name])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) DOWNLOADED \[.*]" % name, res.output)
    os.remove('%s.txt' % name)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testUploadExtensionsCLI(server, runner, spc, apps, files):
    cmd = list(spc)
    name1 = getPkgName(exts[0]['name'], exts[0]['os'], exts[0]['arch'], exts[0]['revision'],
                       exts[0]['app_revision'])
    cmd.extend(['extension', 'upload', app_name[0], './file1.txt', '--os', exts[0]['os'],
                '--arch', exts[0]['arch'], '--name', exts[0]['name'], '--revision',
                exts[0]['revision'], '--app_revision', exts[0]['app_revision'],
                '--repo_type', exts[0]['repo_type'], '--repo_url', exts[0]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name1), res.output)

    cmd = list(spc)
    name2 = getPkgName(exts[1]['name'], exts[1]['os'], exts[1]['arch'], exts[1]['revision'],
                       exts[1]['app_revision'])
    cmd.extend(['extension', 'upload', app_name[0], './file2.txt', '--os', exts[1]['os'],
                '--arch', exts[1]['arch'], '--name', exts[1]['name'], '--revision',
                exts[1]['revision'], '--app_revision', exts[1]['app_revision'],
                '--repo_type', exts[1]['repo_type'], '--repo_url', exts[1]['repo_url']])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) UPLOADED" % re.escape(name2), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testListExtensionsCLI(server, runner, spc, ext):
    cmd = list(spc)
    name1 = getPkgName(exts[0]['name'], exts[0]['os'], exts[0]['arch'], exts[0]['revision'],
                       exts[0]['app_revision'])
    name2 = getPkgName(exts[1]['name'], exts[1]['os'], exts[1]['arch'], exts[1]['revision'],
                       exts[1]['app_revision'])
    name3 = getPkgName(exts[2]['name'], exts[2]['os'], exts[2]['arch'], exts[2]['revision'],
                       exts[2]['app_revision'])
    cmd.extend(['extension', 'list', app_name[0], '--all'])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (exts[0]['revision'], name1, 'draft',
                                                  exts[0]['app_revision']), res.output)
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (exts[1]['revision'], name2, 'draft',
                                                  exts[1]['app_revision']), res.output)
    assert re.search(r"%s *%s *%s *%s *\w{24}" % (exts[2]['revision'], name3, 'draft',
                                                  exts[2]['app_revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDeleteExtensionsCLI(server, runner, spc, ext):
    cmd = list(spc)
    name = getPkgName(exts[0]['name'], exts[0]['os'], exts[0]['arch'], exts[0]['revision'],
                      exts[0]['app_revision'])
    cmd.extend(['extension', 'delete', app_name[0], name])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.match(r"%s %s \(\w{24}\) DELETED" % (name, exts[0]['revision']), res.output)


@pytest.mark.vcr()
@pytest.mark.plugin('slicer_package_manager')
def testDownloadExtensionsCLI(server, runner, spc, ext):
    cmd = list(spc)
    name = getPkgName(exts[0]['name'], exts[0]['os'], exts[0]['arch'], exts[0]['revision'],
                      exts[0]['app_revision'])
    cmd.extend(['extension', 'download', app_name[0], name])
    res = runner.invoke(main, cmd)
    assert res.exit_code == 0
    assert re.search(r"%s \(\w{24}\) DOWNLOADED \[.*]" % name, res.output)
    os.remove('%s.txt' % name)


def getPkgName(baseName, os, arch, rev, app_rev=None):
    if app_rev:
        return "%s_%s_%s_%s_%s" % (app_rev, baseName, os, arch, rev)
    return "%s_%s_%s_%s" % (baseName, os, arch, rev)
