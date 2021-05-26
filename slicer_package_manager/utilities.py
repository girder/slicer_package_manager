# -*- coding: utf-8 -*-

from girder.models.folder import Folder
from girder.utility.progress import ProgressContext

from . import constants


def isSlicerPackages(item):
    if 'meta' in item and all(k in item['meta'] for k in ('os', 'arch', 'baseName', 'revision')):
        return True
    return False


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


def deleteFolder(folder, progress, user):
    with ProgressContext(progress, user=user,
                         title='Deleting folder %s' % folder['name'],
                         message='Calculating folder size...') as ctx:
        # Don't do the subtree count if we weren't asked for progress
        if progress:
            ctx.update(total=Folder().subtreeCount(folder))
        Folder().remove(folder, progress=ctx)
    return folder
