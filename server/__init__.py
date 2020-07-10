# -*- coding: utf-8 -*-

import os

from girder import events
from girder.constants import AccessType
from girder.models.item import Item
from girder.models.folder import Folder
from girder.utility.plugin_utilities import getPluginDir, registerPluginWebroot
from girder.utility.webroot import WebrootBase
from .api.app import App
from . import constants, utilities


class Webroot(WebrootBase):
    """
    The webroot endpoint simply serves the main index HTML file.
    """
    def __init__(self, templatePath=None):
        if not templatePath:
            templatePath = os.path.join(
                getPluginDir(),
                'slicer_package_manager',
                'server',
                'webroot.mako')
        super(Webroot, self).__init__(templatePath)
        self.vars = {
            'apiRoot': '/api/v1',
            'staticRoot': '/static',
            'title': 'Slicer package manager'
        }


def _onDownloadFileComplete(event):
    item = Item().load(event.info['file']['itemId'], level=AccessType.READ)
    meta = item['meta']
    if utilities.isSlicerPackages(item):
        item_folder = Folder().load(item['folderId'], level=AccessType.READ)
        release = Folder().load(item_folder['parentId'], level=AccessType.READ)
        if item_folder['name'] == constants.EXTENSIONS_FOLDER_NAME:
            release = Folder().load(release['parentId'], level=AccessType.READ)
            if release['name'] == constants.DRAFT_RELEASE_NAME:
                Folder().increment(
                    query={'_id': release['_id']},
                    field='meta.downloadStats.%s.%s.%s.%s.%s' % (
                        meta['app_revision'], constants.EXTENSIONS_FOLDER_NAME,
                        meta['baseName'], meta['os'], meta['arch']),
                    amount=1)
            else:
                Folder().increment(
                    query={'_id': item_folder['parentId']},
                    field='meta.downloadStats.%s.%s.%s.%s' %
                          (constants.EXTENSIONS_FOLDER_NAME, meta['baseName'],
                           meta['os'], meta['arch']),
                    amount=1)
        else:
            if release['name'] == constants.DRAFT_RELEASE_NAME:
                Folder().increment(
                    query={'_id': release['_id']},
                    field='meta.downloadStats.%s.%s.%s.%s' % (
                        meta['revision'], 'applications', meta['os'], meta['arch']),
                    amount=1)
            else:
                Folder().increment(
                    query={'_id': item_folder['_id']},
                    field='meta.downloadStats.%s.%s.%s' % (
                        'applications', meta['os'], meta['arch']),
                    amount=1)


def load(info):
    info['apiRoot'].app = App()
    info['serverRoot'].updateHtmlVars({'title': 'Slicer package manager'})

    # Download statistics
    events.bind('model.file.download.complete', 'slicer_package_manager', _onDownloadFileComplete)

    # Mongo indexes
    Item().ensureIndex('meta.baseName')
    Item().ensureIndex('meta.os')
    Item().ensureIndex('meta.arch')
    Item().ensureIndex('meta.app_revision')
    Item().ensureIndex('updated')
    Folder().ensureIndex('meta.downloadExtensions')

    registerPluginWebroot(Webroot(), info['name'])
