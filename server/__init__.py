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

import os

from girder import events
from girder.constants import AccessType
from girder.models.item import Item
from girder.models.folder import Folder
from girder.utility.plugin_utilities import getPluginDir, registerPluginWebroot
from girder.utility.webroot import WebrootBase
from .api.app import App
import constants


class Webroot(WebrootBase):
    """
    The webroot endpoint simply serves the main index HTML file.
    """
    def __init__(self, templatePath=None):
        if not templatePath:
            templatePath = os.path.join(
                getPluginDir(),
                'slicer_extension_manager',
                'server',
                'webroot.mako')
        super(Webroot, self).__init__(templatePath)
        self.vars = {
            'apiRoot': '/api/v1',
            'staticRoot': '/static',
            'title': 'Slicer extension manager'
        }


def _onDownloadFileComplete(event):
    item = Item().load(event.info['file']['itemId'], level=AccessType.READ)
    meta = item['meta']
    release = Folder().load(item['folderId'], level=AccessType.READ)
    release = Folder().load(release['parentId'], level=AccessType.READ)
    if release['name'] == constants.NIGHTLY_RELEASE_NAME:
        Folder().increment(
            query={'_id': release['_id']},
            field='meta.downloadExtensions.%s.%s.%s' % (meta['baseName'], meta['os'], meta['arch']),
            amount=1)
    else:
        Folder().increment(
            query={'_id': item['folderId']},
            field='meta.downloadExtensions.%s.%s.%s' % (meta['baseName'], meta['os'], meta['arch']),
            amount=1)


def load(info):
    info['apiRoot'].app = App()
    info['serverRoot'].updateHtmlVars({'title': 'Slicer extension manager'})

    # Download statistics
    events.bind('model.file.download.complete', 'slicer_extension_manager', _onDownloadFileComplete)

    registerPluginWebroot(Webroot(), info['name'])
