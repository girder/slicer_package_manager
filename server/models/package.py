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

from girder.models.item import Item
from girder.models.model_base import ValidationException


class Package(Item):
    """
    The ``Package`` class derive from the ``Item`` model in Girder and it uses to embedded
    packages binary files.
    """

    def initialize(self):
        super(Package, self).initialize()
        # To be able to upload within a Package the name has to stay as 'item'.
        self.name = 'item'

    def createPackage(self, name, creator, folder, params):
        """
        Create and save in the DB a new application package.

        :param name: Name of the new package
        :param creator: The creator user
        :param folder: The release folder within the package will be created.
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
        doc = super(Package, self).validate(doc)

        if not isinstance(doc.get('created'), datetime.datetime):
            raise ValidationException(
                'Extension field "created" must be a datetime.')

        # Validate the meta field
        if doc.get('meta'):
            base_params = {'app_id', 'os', 'arch', 'repository_type', 'repository_url',
                           'app_revision', 'baseName'}
            specs = []
            for meta in base_params:
                specs.append({
                    'name': meta,
                    'type': six.string_types,
                    'exception_msg': 'Package field "%s" must be a non-empty string.' % meta
                })
            for spec in specs:
                if doc['meta'].get(spec['name']) and not isinstance(
                   doc['meta'][spec['name']], spec['type']):
                    raise ValidationException(spec['exception_msg'])
            duplicateQuery = {
                'name': doc['name'],
                'os': doc['meta']['os'],
                'arch': doc['meta']['arch'],
                'app_revision': doc['meta']['app_revision']
            }
            if '_id' in doc:
                duplicateQuery['_id'] = {'$ne': doc['_id']}
            if self.findOne(duplicateQuery, fields=['_id']):
                raise ValidationException(
                    'An Extension with this name and characteristics already exists.')
        return doc
