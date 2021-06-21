# -*- coding: utf-8 -*-

from girder.constants import AccessType
from girder.models.folder import Folder
from girder.utility.progress import ProgressContext

from . import constants


def isSlicerPackages(item):
    if 'meta' in item and all(k in item['meta'] for k in ('os', 'arch', 'baseName', 'revision')):
        return True
    return False


def isApplicationFolder(folder):
    """
    Return True if folder an application folder.

    An application folder is expected to have the ``applicationPackageNameTemplate`` and
    ``extensionPackageNameTemplate`` metadata as well as parent folder named after
    :const:`constants.TOP_LEVEL_FOLDER_NAME`.
    """
    meta = folder.get('meta', {})
    if not all(k in meta for k in ('applicationPackageNameTemplate', 'extensionPackageNameTemplate')):
        return False

    parent_folder = Folder().load(folder['parentId'], force=True)
    if parent_folder['name'] != constants.TOP_LEVEL_FOLDER_NAME:
        return False

    return True


def isReleaseFolder(folder):
    """
    Return True if folder is a release folder.

    A release folder is expected to have the ``revision`` metadata as well as
    an application parent or grandparent folder (see :func:`isApplicationFolder`).
    """
    if 'revision' not in folder.get('meta', {}):
        return False

    parent_folder = Folder().load(folder['parentId'], force=True)
    grandparent_folder = Folder().load(parent_folder['parentId'], force=True)
    if not any([isApplicationFolder(parent_folder), isApplicationFolder(grandparent_folder)]):
        return False

    return True


def isDraftReleaseFolder(folder):
    """
    Return True if folder is a draft release folder.

    A draft release folder is expected to be a release folder (see :func:`isReleaseFolder`)
    and to have a parent folder named after :const:`constants.DRAFT_RELEASE_NAME`.
    """
    if not isReleaseFolder(folder):
        return False
    parent_folder = Folder().load(folder['parentId'], force=True)
    return parent_folder['name'] == constants.DRAFT_RELEASE_NAME


def getOrCreateReleaseFolder(application, user, app_revision):
    """
    Get or create the release folder associated with the application revision.

    :param application: The parent folder containing the release.
    :param user: The user to check access against or to create the new folder
    :param app_revision: The revision of the application.
    :return: The created/existing release folder.
    """
    release_folder = None
    # Find the release by metadata revision
    releases = Folder().childFolders(application, 'Folder', user=user)
    for folder in releases:
        if 'meta' in folder:
            if 'revision' in folder['meta']:
                if folder['meta']['revision'] == app_revision:
                    release_folder = folder
                    break
    if not release_folder:
        # Only the draft release in the list
        release_folder = list(Folder().childFolders(
            application,
            'Folder',
            user=user,
            filters={'name': constants.DRAFT_RELEASE_NAME}))
        if not release_folder:
            raise Exception('The %s folder not found.' % constants.DRAFT_RELEASE_NAME)
        release_folder = release_folder[0]

        revision_folder = list(Folder().childFolders(
            release_folder,
            'Folder',
            user=user,
            filters={'meta.revision': app_revision}))
        if revision_folder:
            revision_folder = revision_folder[0]
        else:
            revision_folder = Folder().createFolder(
                parent=release_folder,
                name=app_revision,
                parentType='Folder',
                public=release_folder['public'],
                creator=user)
            revision_folder = Folder().setMetadata(
                revision_folder,
                {'revision': app_revision})
        release_folder = revision_folder

    return release_folder


def getReleaseFolder(item):
    """
    Get item release folder.

    The release folder is either the one the with name matching
    :const:`constants.DRAFT_RELEASE_NAME` (e,g ``draft``) or the release
    folder (e.g ``1.0``).

    ::

    Applications
        |--- packages
        |        |----- Slicer
        |        |         |----- 1.0
        |        |         |        |---- Package1
        .        .         .        .
        |        |         |        |---- extensions
        |        |         |        |         |---- Extension1
        .        .         .        .         .
        .        .         .
        .        .         .
        |        |         |----- draft
        |        |         |        |--- r100
        |        |         |        |      |---- Package1
        .        .         .        .      .
        |        |         |        |      |----- extensions
        |        |         |        |      |          |---- Extension1

    :param item: A package or extension instance.
    :return: The parent release folder or None.
    """
    if not isSlicerPackages(item):
        return None

    folder = Folder().load(item['folderId'], level=AccessType.READ)

    # Check if item folder is "extensions". If yes, get parent folder.
    if folder['name'] == constants.EXTENSIONS_FOLDER_NAME:
        extensions_folder = folder
        folder = Folder().load(extensions_folder['parentId'], level=AccessType.READ)

    package_folder = folder

    # Check if grand parent folder is "draft". If yes return it.
    grantparent_folder = Folder().load(package_folder['parentId'], level=AccessType.READ)
    if grantparent_folder['name'] == constants.DRAFT_RELEASE_NAME:
        return grantparent_folder
    else:
        return package_folder


def deleteFolder(folder, progress, user):
    with ProgressContext(progress, user=user,
                         title='Deleting folder %s' % folder['name'],
                         message='Calculating folder size...') as ctx:
        # Don't do the subtree count if we weren't asked for progress
        if progress:
            ctx.update(total=Folder().subtreeCount(folder))
        Folder().remove(folder, progress=ctx)
    return folder
