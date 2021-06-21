# -*- coding: utf-8 -*-

from girder import events, plugin
from girder.constants import AccessType
from girder.models.item import Item
from girder.models.folder import Folder
from .api.app import App
from . import constants, utilities
from .models.package import Package as PackageModel

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


def _onDownloadFileComplete(event):
    """
    Increment download count associated with item revision associated with the event.

    Count is stored in the ``downloadStats`` metadata organized as a json document
    set in the parent release folder.

    See :func:`utilities.getReleaseFolder()`.
    """
    item = Item().load(event.info['file']['itemId'], force=True)

    if not utilities.isSlicerPackages(item):
        return

    release = utilities.getReleaseFolder(item)
    if release is None:
        return

    meta = item['meta']
    is_draft_release = release['name'] == constants.DRAFT_RELEASE_NAME
    is_extension_item = 'app_revision' in meta

    if is_extension_item:
        folder_name = constants.EXTENSIONS_FOLDER_NAME
        if is_draft_release:
            field_template = 'meta.downloadStats.{app_revision}.{folder_name}.{baseName}.{os}.{arch}'
        else:
            field_template = 'meta.downloadStats.{folder_name}.{baseName}.{os}.{arch}'
    else:
        folder_name = 'applications'
        if is_draft_release:
            field_template = 'meta.downloadStats.{revision}.{folder_name}.{os}.{arch}'
        else:
            field_template = 'meta.downloadStats.{folder_name}.{os}.{arch}'

    Folder().increment(
        query={'_id': release['_id']},
        field=field_template.format(folder_name=folder_name, **meta),
        amount=1)


def _onItemSavedOrCopied(event):
    item = Item().load(event.info['_id'], force=True)

    if not utilities.isSlicerPackages(item):
        return

    release = utilities.getReleaseFolder(item)
    if release is None:
        return

    meta = item['meta']

    is_draft_release = release['name'] == constants.DRAFT_RELEASE_NAME
    is_extension_item = 'app_revision' in meta

    if is_extension_item:
        return

    if is_draft_release:
        if 'release' not in meta:
            return
        del meta['release']

    else:
        if meta.get('release') == release['name']:
            return
        meta['release'] = release['name']

    PackageModel().setMetadata(item, meta)


def _onReleaseFolderNameUpdated(event):
    folder = Folder().load(event.info['_id'], force=True)
    if not utilities.isReleaseFolder(folder):
        return

    release = folder
    if release['name'] == constants.DRAFT_RELEASE_NAME:
        return

    filters = {
        '$and': [
            {'meta.app_id': {'$exists': True}},
            {'meta.os': {'$exists': True}},
            {'meta.arch': {'$exists': True}},
            {'meta.revision': {'$exists': True}}]
    }
    items = Folder().childItems(
        folder=release,
        filters=filters,
        level=AccessType.READ
    )
    for item in items:
        item_meta = item['meta']
        if item_meta.get('release') == release['name']:
            continue
        item_meta['release'] = release['name']
        PackageModel().setMetadata(item, item_meta)


class GirderPlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'Slicer Package Manager'

    def load(self, info):
        # add plugin loading logic here
        info['apiRoot'].app = App()
        info['serverRoot'].updateHtmlVars({'title': 'Slicer package manager'})

        # Download statistics
        events.bind('model.file.download.complete', 'slicer_package_manager', _onDownloadFileComplete)

        # Update item "release" metadata
        events.bind('model.item.save.after', 'slicer_package_manager', _onItemSavedOrCopied)
        events.bind('model.item.copy.after', 'slicer_package_manager', _onItemSavedOrCopied)
        events.bind('model.folder.save.after', 'slicer_package_manager', _onReleaseFolderNameUpdated)

        # Mongo indexes
        Item().ensureIndex('meta.baseName')
        Item().ensureIndex('meta.os')
        Item().ensureIndex('meta.arch')
        Item().ensureIndex('meta.app_revision')
        Item().ensureIndex('updated')
        Folder().ensureIndex('meta.downloadExtensions')
