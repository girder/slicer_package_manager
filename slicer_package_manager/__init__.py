# -*- coding: utf-8 -*-

from girder import events, plugin
from girder.constants import AccessType
from girder.models.item import Item
from girder.models.folder import Folder
from .api.app import App
from . import constants, utilities

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


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
                    field='meta.downloadStats.{app_revision}.{folder_name}.{baseName}.{os}.{arch}'.format(
                        folder_name=constants.EXTENSIONS_FOLDER_NAME, **meta),
                    amount=1)
            else:
                Folder().increment(
                    query={'_id': item_folder['parentId']},
                    field='meta.downloadStats.{folder_name}.{baseName}.{os}.{arch}'.format(
                        folder_name=constants.EXTENSIONS_FOLDER_NAME, **meta),
                    amount=1)
        else:
            if release['name'] == constants.DRAFT_RELEASE_NAME:
                Folder().increment(
                    query={'_id': release['_id']},
                    field='meta.downloadStats.{revision}.{folder_name}.{os}.{arch}'.format(
                        folder_name='applications', **meta),
                    amount=1)
            else:
                Folder().increment(
                    query={'_id': item_folder['_id']},
                    field='meta.downloadStats.{folder_name}.{os}.{arch}'.format(
                        folder_name='applications', **meta),
                    amount=1)


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'Slicer Package Manager'

    def load(self, info):
        # add plugin loading logic here
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
