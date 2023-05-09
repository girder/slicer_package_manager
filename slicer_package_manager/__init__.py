from girder import events, plugin
from girder.constants import AccessType
from girder.models.file import File
from girder.models.item import Item
from girder.models.folder import Folder
from .api.app import App
from . import constants, utilities
from .models.extension import Extension as ExtensionModel
from .models.package import Package as PackageModel

from girder_hashsum_download import SUPPORTED_ALGORITHMS

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
    """
    Set or update "release" metadata when an application package item is
    moved or copied into or out of a release folder.

    See :func:`utilities.isSlicerPackages()` and :func:`utilities.getReleaseFolder()`.
    """
    item = Item().load(event.info['_id'], force=True)

    if not utilities.isSlicerPackages(item):
        return

    release = utilities.getReleaseFolder(item, force=True)
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


def _onFileEvent(event):
    """Update checksum metadata for an application or extension package item when a file is saved, copied
    or about to be removed.

    See :func:`utilities.isChildOfSlicerPackages()`.
    """
    file = File().load(event.info['_id'], force=True)
    if not utilities.isChildOfSlicerPackages(file):
        return

    item = Item().load(file['itemId'], force=True)

    # Both application and extension packages are expected to have these metadata
    if not all(meta in item.get('meta', {}) for meta in ['app_id', 'os', 'arch', 'revision']):
        return

    # ... but only extension packages have "app_revision"
    is_extension_package = 'app_revision' in item

    if event.name == "model.file.save.after":
        if Item().childFiles(item).count() > 1:
            # If the update is not related to the first file, ignore
            return

        # Collect checksums associated if the file
        checksums = {algo: file[algo] for algo in SUPPORTED_ALGORITHMS if algo in file}

    if event.name == "model.file.remove":
        item_files = list(Item().childFiles(item))

        if len(item_files) > 2:
            return

        elif len(item_files) == 2:
            # If after removing this file, there are only one file left, update the item with
            # the checksum of the remaining file.
            remaining_file = [_file for _file in item_files if _file["_id"] != file["_id"]][0]

            # Collect checksums associated if the remaining file
            checksums = {algo: remaining_file[algo] for algo in SUPPORTED_ALGORITHMS if algo in remaining_file}

        elif len(item_files) == 1:
            # If after removing this file, there are no file left, set the checksum to empty string.
            # Collect checksums associated if the remaining file
            checksums = {algo: "" for algo in SUPPORTED_ALGORITHMS}

    # Update metadata overwriting existing checksum values if any
    meta = {**item['meta'], **checksums}

    if is_extension_package:
        ExtensionModel().setMetadata(item, meta)
    else:
        PackageModel().setMetadata(item, meta)


def _onReleaseFolderNameUpdated(event):
    """
    Update "release" metadata on all application package items in a release folder when its name is changed.

    See :func:`utilities.isReleaseFolder()`.
    """
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
            {'meta.revision': {'$exists': True}}],
    }
    items = Folder().childItems(
        folder=release,
        filters=filters,
        level=AccessType.READ,
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
        plugin.getPlugin('hashsum_download').load(info)

        info['apiRoot'].app = App()
        info['serverRoot'].updateHtmlVars({'title': 'Slicer package manager'})

        # Download statistics
        events.bind('model.file.download.complete', 'slicer_package_manager', _onDownloadFileComplete)

        # Update item "release" metadata
        events.bind('model.item.save.after', 'slicer_package_manager', _onItemSavedOrCopied)
        events.bind('model.item.copy.after', 'slicer_package_manager', _onItemSavedOrCopied)
        events.bind('model.folder.save.after', 'slicer_package_manager', _onReleaseFolderNameUpdated)

        # Update item metadata with file checksums
        events.bind('model.file.save.after', 'slicer_package_manager', _onFileEvent)
        events.bind('model.file.remove', 'slicer_package_manager', _onFileEvent)

        # Mongo indexes
        Item().ensureIndex('meta.baseName')
        Item().ensureIndex('meta.os')
        Item().ensureIndex('meta.arch')
        Item().ensureIndex('meta.app_revision')
        Item().ensureIndex('updated')
        Folder().ensureIndex('meta.downloadExtensions')
