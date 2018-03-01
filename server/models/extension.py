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
##############################################################################

import datetime
import six

from girder.constants import AccessType
from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.model_base import ValidationException


class Extension(Item):
    """
    The ``Extension`` class derive from the ``Item`` model in Girder and it uses to embedded
    extension binary files.
    """

    def initialize(self):
        self.name = 'item'

        self.ensureIndices(['extension_id', 'item_id'])
        self.ensureTextIndex({
            'name': 10,
            'description': 1
        })
        self.exposeFields(level=AccessType.READ, fields=('extension_id', 'item_id', 'meta'))

    def get(self, release, limit=0, offset=0, sort=None, filters=None, **kwargs):
        """
        Get all the extensions available for a release.

        :param release: The release folder
        :return: Generator containing all the child items of the release.
        """
        return Folder().childItems(
            release,
            limit=limit,
            offset=offset,
            sort=sort,
            filters=filters,
            **kwargs)

    def createExtension(self, name, creator, folder, params):
        """
        Create and save in the DB a new extension.

        :param name: Name of the new extension
        :param creator: The creator user
        :param folder: The release folder within the extension will be created.
        :param params: All the metadata to set on the new extension
        :return: The new extension item
        """
        item = self.createItem(
            name,
            creator,
            folder,
            params.get('description')
        )
        return self.setMetadata(item, params)

    def validate(self, doc):
        """
        Validate the extension instance.

        :param doc: The extension instance
        :return: The extension instance once validated
        """
        # Call Item validate method
        doc = super(Extension, self).validate(doc)

        if not isinstance(doc.get('created'), datetime.datetime):
            raise ValidationException(
                'Extension field "created" must be a datetime.')

        # Validate the meta field
        if doc.get('meta'):
            base_params = {'app_id', 'os', 'arch', 'revision', 'repository_type', 'repository_url',
                           'app_revision', 'packagetype', 'codebase', 'baseName', 'description'}
            specs = []
            for meta in base_params:
                specs.append({
                    'name': meta,
                    'type': six.string_types,
                    'exception_msg': 'Extension field "{}" must be a non-empty string.'
                                     .format(meta)
                })
            for spec in specs:
                if doc['meta'].get(spec['name']) and not isinstance(
                   doc['meta'][spec['name']], spec['type']):
                    raise ValidationException(spec['exception_msg'])
            extraMeta = set(six.viewkeys(doc['meta'])) - base_params
            if extraMeta:
                extra_params = {'release', 'icon_url', 'development_status', 'category',
                                'enabled', 'homepage', 'screenshots', 'contributors', 'dependency'}
                if extraMeta - extra_params:
                    raise ValidationException('Extension has extra fields: %s.' %
                                              ', '.join(sorted(extraMeta)))
                specs = []
                for meta in extra_params:
                    if meta == 'enabled':
                        specs.append({
                            'name': meta,
                            'type': bool,
                            'exception_msg': 'Extension field "{}" must be a boolean.'
                                             .format(meta)
                        })
                    else:
                        specs.append({
                            'name': meta,
                            'type': six.string_types,
                            'exception_msg': 'Extension field "{}" must be a non-empty string.'
                                             .format(meta)
                        })
                for spec in specs:
                    if doc['meta'].get(spec['name']) and not isinstance(
                       doc['meta'][spec['name']], spec['type']):
                        raise ValidationException(spec['exception_msg'])
            duplicateQuery = {
                'name': doc['name'],
                'os': doc['meta']['os'],
                'arch': doc['meta']['arch'],
                'revision': doc['meta']['revision']
            }
            if '_id' in doc:
                duplicateQuery['_id'] = {'$ne': doc['_id']}
            if self.findOne(duplicateQuery, fields=['_id']):
                raise ValidationException(
                    'An Extension with this name and characteristics already exists.')
        return doc
