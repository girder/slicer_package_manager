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

from girder.utility.plugin_utilities import getPluginDir, registerPluginWebroot
from girder.utility.webroot import WebrootBase
from .api.app import App


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


def load(info):
    info['apiRoot'].app = App()
    info['serverRoot'].updateHtmlVars({'title': 'Slicer extension manager'})

    registerPluginWebroot(Webroot(), info['name'])
