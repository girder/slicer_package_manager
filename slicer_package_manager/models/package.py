import datetime
import six

from girder.models.folder import Folder
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

    def get(self, release, limit=0, offset=0, sort=None, filters=None, **kwargs):
        """
        Get all the application packages available for a release.

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

    def createPackage(self, name, creator, folder, params, description):
        """
        Create and save in the DB a new application package.

        :param name: Name of the new package
        :param creator: The creator user
        :param folder: The release folder within the package will be created.
        :param params: All the metadata to set on the new application package
        :param description: A description for the application package.
        :return: The new application package item
        """
        item = self.createItem(
            name,
            creator,
            folder,
            description
        )
        return self.setMetadata(item, params)

    def validate(self, doc):
        """
        Validate the package instance.

        :param doc: The package instance
        :return: The package instance once validated
        """
        # Call Item validate method
        doc = super(Package, self).validate(doc)

        if not isinstance(doc.get('created'), datetime.datetime):
            raise ValidationException(
                'Package field "created" must be a datetime.')

        # Validate the meta field
        if doc.get('meta'):
            base_params = {'app_id', 'os', 'arch', 'repository_type', 'repository_url',
                           'revision', 'baseName'}
            specs = []
            for meta in base_params:
                specs.append({
                    'name': meta,
                    'type': six.string_types,
                    'exception_msg': 'Package field "%s" must be a non-empty string.' % meta
                })
            specs.append({
                'name': 'build_date ',
                'type': datetime.datetime,
                'exception_msg': 'Package field "%s" must be a datetime.' % 'build_date'
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
                    'A Package with this name and characteristics already exists.')
        return doc
