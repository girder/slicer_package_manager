#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#  Copyright Kitware Inc.
#
#  Licensed under the Apache License, Version 2.0 ( the "License" );
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
###############################################################################

import click
import platform

from girder_client import GirderClient
from . import SlicerPackageClient, __version__, Constant


# ---------------- UTILITIES ---------------- #

def _getOs():
    os = platform.system()
    if os == 'Linux':
        return 'linux'
    elif os == 'Darwin':
        return 'macosx'
    elif os == 'Windows':
        return 'win'

# ------------------------------------------- #


class SlicerPackageCli(SlicerPackageClient):
    """
    A command line Python client for interacting with a Girder instance's
    RESTful api, specifically for performing uploads into a Girder instance.
    """

    def __init__(self, username, password, host=None, port=None, apiRoot=None,
                 scheme=None, apiUrl=None, apiKey=None):
        """
        Initialization function to create a SlicerPackageCli instance, will attempt
        to authenticate with the designated Girder instance. Aside from username, password,
        apiKey, and sslVerify, all other kwargs are passed directly through to the
        :py:class:`girder_client.GirderClient` base class constructor.

        :param username: username to authenticate to Girder instance.
        :param password: password to authenticate to Girder instance, leave
            this blank to be prompted.
        """
        def _progressBar(*args, **kwargs):
            bar = click.progressbar(*args, **kwargs)
            bar.bar_template = "[%(bar)s]  %(info)s  %(label)s"
            bar.show_percent = True
            bar.show_pos = True
            return bar

        super(SlicerPackageCli, self).__init__(host=host, port=port, apiRoot=apiRoot, scheme=scheme, apiUrl=apiUrl,
                                               progressReporterCls=_progressBar)
        interactive = password is None
        if apiKey:
            self.authenticate(apiKey=apiKey)
        elif username:
            self.authenticate(username, password, interactive=interactive)

    def _requestFunc(self, *args, **kwargs):
        return super(SlicerPackageCli, self)._requestFunc(*args, **kwargs)


class _HiddenOption(click.Option):
    def get_help_record(self, ctx):
        pass


class _AdvancedOption(click.Option):
    pass


class _Group(click.Group):
    def format_options(self, ctx, formatter):
        opts = []
        advanced_opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is None:
                continue
            if isinstance(param, _AdvancedOption):
                advanced_opts.append(rv)
            else:
                opts.append(rv)

        if opts:
            with formatter.section('Options'):
                formatter.write_dl(opts)
        if advanced_opts:
            with formatter.section('Advanced Options'):
                formatter.write_dl(advanced_opts)
        self.format_commands(ctx, formatter)


_CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=_CONTEXT_SETTINGS)
@click.option('--api-url', default=None,
              help='RESTful API URL '
                   '(e.g https://girder.example.com:443/%s)' % GirderClient.DEFAULT_API_ROOT)
@click.option('--api-key', envvar='GIRDER_API_KEY', default=None,
              help='[default: GIRDER_API_KEY env. variable]')
@click.option('--username', default=None)
@click.option('--password', default=None)
# Advanced options
@click.option('--host', default=None,
              cls=_AdvancedOption,
              help="[default: %s]" % GirderClient.DEFAULT_HOST)
@click.option('--scheme', default=None,
              cls=_AdvancedOption,
              help="[default: %s if %s else %s]" % (
                  GirderClient.getDefaultScheme(GirderClient.DEFAULT_HOST),
                  GirderClient.DEFAULT_HOST,
                  GirderClient.getDefaultScheme("girder.example.com")))
@click.option('--port', default=None,
              cls=_AdvancedOption,
              help="[default: %s if %s; %s if %s else %s]" % (
                  GirderClient.DEFAULT_HTTPS_PORT, "https",
                  GirderClient.DEFAULT_LOCALHOST_PORT, "localhost",
                  GirderClient.DEFAULT_HTTP_PORT,
                  ))
@click.option('--api-root', default=None,
              help='relative path to the Girder REST API '
                   '[default: %s]' % GirderClient.DEFAULT_API_ROOT,
              show_default=True,
              cls=_AdvancedOption)
@click.option('--no-ssl-verify', is_flag=True, default=False,
              help='Disable SSL Verification',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--certificate', default=None,
              help='Specify path to SSL certificate',
              show_default=True,
              cls=_AdvancedOption)
@click.version_option(version=__version__, prog_name='Girder command line interface')
@click.pass_context
def main(ctx, username, password,
         api_key, api_url, scheme, host, port, api_root,
         no_ssl_verify, certificate):
    """
    The recommended way to use credentials is to first generate an API key
    and then specify the ``api-key`` argument or set the ``GIRDER_API_KEY``
    environment variable.

    The client also supports ``username`` and ``password`` args. If only the
    ``username`` is specified, the client will prompt the user to interactively
    input his/her password.
    """
    # --api-url and URL by part arguments are mutually exclusive
    url_part_options = ['host', 'scheme', 'port', 'api_root']
    has_api_url = ctx.params.get('api_url', None)
    for name in url_part_options:
        has_url_part = ctx.params.get(name, None)
        if has_api_url and has_url_part:
            raise click.BadArgumentUsage(
                'Option "--api-url" and option "--%s" are mutually exclusive.' %
                name.replace("_", "-"))
    if certificate and no_ssl_verify:
        raise click.BadArgumentUsage(
            'Option "--no-ssl-verify" and option "--certificate" are mutually exclusive.')

    ctx.obj = SlicerPackageCli(
        username, password, host=host, port=port, apiRoot=api_root,
        scheme=scheme, apiUrl=api_url, apiKey=api_key)

    if certificate and ctx.obj.scheme != 'https':
        raise click.BadArgumentUsage(
            'A URI scheme of "https" is required for option "--certificate"')


@main.group(context_settings=_CONTEXT_SETTINGS)
@click.pass_obj
def app(sc):
    pass


@main.group(context_settings=_CONTEXT_SETTINGS)
@click.pass_obj
def release(sc):
    pass


@main.group(context_settings=_CONTEXT_SETTINGS)
@click.pass_obj
def draft(sc):
    pass


@main.group(context_settings=_CONTEXT_SETTINGS)
@click.pass_obj
def extension(sc):
    pass


@main.group(context_settings=_CONTEXT_SETTINGS)
@click.pass_obj
def package(sc):
    pass


@app.command('create')
@click.argument('name')
@click.option('--desc', default=None,
              help='Description of the application',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--coll_name', default=None,
              help='Name of the new collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--coll_desc', default=None,
              help='Description of the new collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--public', flag_value='public', default=None,
              help='Whether the collection should be publicly visible',
              show_default=True,
              cls=_AdvancedOption)

@click.pass_obj
def _cli_createApp(sc, *args, **kwargs):
    """
    Create a new application.
    """
    application = sc.createApp(*args, **kwargs)
    print('%s (%s)\t%s' % (application['_id'], application['name'], 'CREATED'))


@app.command('list')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--name', default=None,
              help='Name of the application',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_listApp(sc, *args, **kwargs):
    """
    List all the applications.
    """
    applications = sc.listApp(*args, **kwargs)
    print('%-25s\t%-20s\t%-50s' % ('APPLICATION ID', 'NAME', 'DESCRIPTION'))
    print('%-25s\t%-20s\t%-50s' % ('-' * 25, '-' * 20, '-' * 50))
    for application in applications:
        print('%-25s\t%-20s\t%-50s' %
              (application['_id'], application['name'], application['description'][0:50]))


@app.command('delete')
@click.argument('name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.pass_obj
def _cli_deleteApp(sc, *args, **kwargs):
    """
    Delete an application.
    """
    application = sc.deleteApp(*args, **kwargs)
    print('%s (%s)\t%s' % (application['name'], application['_id'], 'DELETED'))


@release.command('create')
@click.argument('app_name', required=True)
@click.option('--name', prompt=True,
              help='Name of the new release',
              cls=_AdvancedOption)
@click.option('--revision', prompt=True,
              help='Revision of the application',
              cls=_AdvancedOption)
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--desc', default=None,
              help='Description of the release',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_createRelease(sc, *args, **kwargs):
    """
    Create a new release.
    """
    rls = sc.createRelease(*args, **kwargs)
    print('%s (%s)\t%s' % (rls['name'], rls['_id'], 'CREATED'))


@release.command('list')
@click.argument('app_name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.pass_obj
def _cli_listRelease(sc, *args, **kwargs):
    """
    List all the release within an application.
    """
    releases = sc.listRelease(*args, **kwargs)
    print('%-25s\t%-20s\t%-10s\t%-50s' % ('RELEASE ID', 'NAME', 'REVISION', 'DESCRIPTION'))
    print('%-25s\t%-20s\t%-10s\t%-50s' % ('-' * 25, '-' * 20, '-' * 10, '-' * 50))
    for rls in releases:
        if 'meta' in rls and 'revision' in rls['meta']:
            revision = rls['meta']['revision']
        else:
            revision = ''
        print('%-25s\t%-20s\t%-15s\t%-50s' % (
            rls['_id'], rls['name'], revision, rls['description'][0:50]))


@release.command('delete')
@click.argument('app_name')
@click.argument('name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.pass_obj
def _cli_deleteRelease(sc, *args, **kwargs):
    """
    Delete a release.
    """
    rls = sc.deleteRelease(*args, **kwargs)
    print('%s (%s)\t%s' % (rls['name'], rls['_id'], 'DELETED'))


@draft.command('list')
@click.argument('app_name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--revision', default=None,
              help='Revision of the draft release',
              cls=_AdvancedOption)
@click.option('--offset', default=0,
              help='Offset of the list',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_listDraftRelease(sc, *args, **kwargs):
    """
    List all the revision of the default preview within an application.
    """
    releases = sc.listDraftRelease(*args, **kwargs)
    print('%-25s\t%-20s\t%-10s\t%-50s' % ('RELEASE ID', 'NAME', 'REVISION', 'DESCRIPTION'))
    print('%-25s\t%-20s\t%-10s\t%-50s' % ('-' * 25, '-' * 20, '-' * 10, '-' * 50))
    for rev in releases:
        if 'meta' in rev and 'revision' in rev['meta']:
            revision = rev['meta']['revision']
        else:
            revision = ''
        print('%-25s\t%-20s\t%-15s\t%-50s' % (
            rev['_id'], rev['name'], revision, rev['description'][0:50]))


@draft.command('delete')
@click.argument('app_name')
@click.argument('revision')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.pass_obj
def _cli_deleteDraftRelease(sc, *args, **kwargs):
    """
    Delete a specific revision within the Draft release.
    """
    rls = sc.deleteDraftRelease(*args, **kwargs)
    print('%s (%s)\t%s' % (rls['name'], rls['_id'], 'DELETED'))


@extension.command('upload')
@click.argument('app_name')
@click.argument('filepath')
@click.option('--os', 'ext_os', default=_getOs(),
              help='The target operating system of the package',
              cls=_AdvancedOption)
@click.option('--arch', default='amd64',
              help='Architecture that is supported by the extension',
              cls=_AdvancedOption)
@click.option('--name', prompt=True,
              help='The baseName of the extension',
              cls=_AdvancedOption)
@click.option('--repo_type', default='',
              help='Type of the repository where find the extension',
              cls=_AdvancedOption)
@click.option('--repo_url', default='',
              help='URL of the repository where find the extension',
              cls=_AdvancedOption)
@click.option('--revision', default='0.0.1',
              help='Revision of the extension',
              cls=_AdvancedOption)
@click.option('--app_revision', prompt=True,
              help='Revision of the application',
              cls=_AdvancedOption)
@click.option('--packagetype', default='',
              help='Type of the package (Installer, data...)',
              cls=_AdvancedOption)
@click.option('--codebase', default='',
              help='The codebase baseName',
              cls=_AdvancedOption)
@click.option('--desc', default='',
              help='Description of the extension',
              cls=_AdvancedOption)
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--force', default=False,
              help='Force the upload',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_uploadExtension(sc, *args, **kwargs):
    """
    Upload an extension.
    """
    print('Create the extension %s' % kwargs['name'])
    ext = sc.uploadExtension(*args, **kwargs)
    if ext == Constant.EXTENSION_AREADY_UP_TO_DATE:
        print('Extension "%s" is already up-to-date\t(Extension Item updated)' % kwargs['name'])
    elif ext == Constant.EXTENSION_NOW_UP_TO_DATE:
        print('%s\t%s\t%s' % (kwargs['name'], 'UPLOADED', 'The extension is now up-to-date'))
    else:
        print('%s (%s)\t%s' % (ext['name'], ext['_id'], 'UPLOADED'))


@extension.command('download')
@click.argument('app_name')
@click.argument('id_or_name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--dir_path', default=Constant.CURRENT_FOLDER,
              help='Path to the directory where will be downloaded the extension',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_downloadExtension(sc, *args, **kwargs):
    """
    Download an extension.
    """
    print('Start download...')
    ext = sc.downloadExtension(*args, **kwargs)
    print('%s (%s)\t%s\t[%s]' % (ext['name'], ext['_id'], 'DOWNLOADED', kwargs['dir_path']))


@extension.command('list')
@click.argument('app_name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--name', default=None,
              help='The baseName of the extension',
              cls=_AdvancedOption)
@click.option('--os', 'ext_os', type=click.Choice(['win', 'linux', 'macosx']))
@click.option('--arch', type=click.Choice(['amd64', 'i386']))
@click.option('--app_revision', default=None,
              help='The revision of the application',
              cls=_AdvancedOption)
@click.option('--release', default=Constant.DRAFT_RELEASE_NAME,
              help='List all extension within the release',
              cls=_AdvancedOption)
@click.option('--limit', default=Constant.DEFAULT_LIMIT,
              help='The limit number of listed extensions ',
              cls=_AdvancedOption)
@click.option('--all', 'all', flag_value='all',
              default=False,
              help='List all the extension of the application',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_listExtension(sc, *args, **kwargs):
    """
    List all the extension within an application.
    """
    extensions = sc.listExtension(*args, **kwargs)
    print('%-25s\t%-30s\t\t%-30s' % ('EXTENSION ID', 'NAME', 'REVISION'))
    print('%-25s\t%-30s\t\t%-30s' % ('-' * 25, '-' * 30, '-' * 30))
    for ext in extensions:
        print('%-25s\t%-30s\t\t%-30s' % (ext['_id'], ext['name'], ext['meta']['revision'][0:30]))


@extension.command('delete')
@click.argument('app_name')
@click.argument('id_or_name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.pass_obj
def _cli_deleteExtension(sc, *args, **kwargs):
    """
    Delete an extension by ID or Name.
    """
    ext = sc.deleteExtension(*args, **kwargs)
    print('%s (%s)\t%s' % (ext['name'], ext['_id'], 'DELETED'))


@package.command('upload')
@click.argument('app_name')
@click.argument('filepath')
@click.option('--os', 'pkg_os', default=_getOs(),
              help='The target operating system of the package',
              cls=_AdvancedOption)
@click.option('--arch', default='amd64',
              help='Architecture that is supported by the package',
              cls=_AdvancedOption)
@click.option('--name', prompt=True,
              help='The baseName of the package',
              cls=_AdvancedOption)
@click.option('--repo_type', default='',
              help='Type of the repository where find the package',
              cls=_AdvancedOption)
@click.option('--repo_url', default='',
              help='URL of the repository where find the package',
              cls=_AdvancedOption)
@click.option('--revision', prompt=True,
              help='Revision of the application',
              cls=_AdvancedOption)
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--desc', default='',
              help='Description of the package',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_uploadApplicationPackage(sc, *args, **kwargs):
    """
    Upload an application package.
    """
    print('Create the application package %s' % kwargs['name'])
    pkg = sc.uploadApplicationPackage(*args, **kwargs)
    if pkg == Constant.PACKAGE_NOW_UP_TO_DATE:
        print('%s\t%s\t%s' % (kwargs['name'], 'UPLOADED', 'The package is now up-to-date'))
    else:
        print('%s (%s)\t%s' % (pkg['name'], pkg['_id'], 'UPLOADED'))


@package.command('download')
@click.argument('app_name')
@click.argument('id_or_name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--dir_path', default=Constant.CURRENT_FOLDER,
              help='Path to the directory where will be downloaded the package',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_downloadApplicationPackage(sc, *args, **kwargs):
    """
    Download an application package.
    """
    print('Start download...')
    pkg = sc.downloadApplicationPackage(*args, **kwargs)
    print('%s (%s)\t%s\t[%s]' % (pkg['name'], pkg['_id'], 'DOWNLOADED', kwargs['dir_path']))


@package.command('list')
@click.argument('app_name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.option('--name', default=None,
              help='The baseName of the package',
              cls=_AdvancedOption)
@click.option('--os', 'pkg_os', type=click.Choice(['win', 'linux', 'macosx']))
@click.option('--arch', type=click.Choice(['amd64', 'i386']))
@click.option('--revision', default=None,
              help='The revision of the application',
              cls=_AdvancedOption)
@click.option('--release', default=None,
              help='List all extension within the release',
              cls=_AdvancedOption)
@click.option('--limit', default=Constant.DEFAULT_LIMIT,
              help='The limit number of listed extensions ',
              cls=_AdvancedOption)
@click.pass_obj
def _cli_listApplicationPackage(sc, *args, **kwargs):
    """
    List all the application package within an application.
    """
    packages = sc.listApplicationPackage(*args, **kwargs)
    print('%-25s\t%-30s\t\t%-30s' % ('PACKAGE ID', 'NAME', 'REVISION'))
    print('%-25s\t%-30s\t\t%-30s' % ('-' * 25, '-' * 30, '-' * 30))
    for pkg in packages:
        print('%-25s\t%-30s\t\t%-30s' % (pkg['_id'], pkg['name'], pkg['meta']['revision'][0:30]))


@package.command('delete')
@click.argument('app_name')
@click.argument('id_or_name')
@click.option('--coll_id', default=None, envvar='COLLECTION_ID',
              help='ID of an existing collection',
              show_default=True,
              cls=_AdvancedOption)
@click.pass_obj
def _cli_deleteApplicationPackage(sc, *args, **kwargs):
    """
    Delete an application package by ID or Name.
    """
    pkg = sc.deleteApplicationPackage(*args, **kwargs)
    print('%s (%s)\t%s' % (pkg['name'], pkg['_id'], 'DELETED'))
