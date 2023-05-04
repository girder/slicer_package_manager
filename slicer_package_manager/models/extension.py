import datetime

from girder.models.folder import Folder
from girder.models.item import Item
from girder.models.model_base import ValidationException


class Extension(Item):
    """
    The ``Extension`` class derive from the ``Item`` model in Girder and it uses to embedded
    extension binary files.
    """

    def initialize(self):
        super().initialize()
        # To be able to upload within an Extension the name has to stay as 'item'.
        self.name = 'item'

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
            params.get('description'),
        )
        return self.setMetadata(item, params)

    def validate(self, doc):
        """
        Validate the extension instance.

        :param doc: The extension instance
        :return: The extension instance once validated
        """
        # Call Item validate method
        doc = super().validate(doc)

        if not isinstance(doc.get('created'), datetime.datetime):
            msg = 'Extension field "created" must be a datetime.'
            raise ValidationException(msg)

        # Validate the meta field
        if doc.get('meta'):
            base_params = {'app_id', 'os', 'arch', 'revision', 'repository_type', 'repository_url',
                           'app_revision', 'baseName', 'description'}
            specs = []
            for meta in base_params:
                specs.append({
                    'name': meta,
                    'type': (str,),
                    'exception_msg': f'Extension field "{meta}" must be a non-empty string.',
                })
            for spec in specs:
                if doc['meta'].get(spec['name']) and not isinstance(
                   doc['meta'][spec['name']], spec['type']):
                    msg=spec['exception_msg']
                    raise ValidationException(msg)
            extraMeta = set(doc['meta'].keys()) - base_params
            if extraMeta:
                extra_params = {'icon_url', 'development_status', 'category',
                                'enabled', 'homepage', 'screenshots', 'contributors', 'dependency',
                                'license'}
                if extraMeta - extra_params:
                    msg = f'Extension has extra fields: {", ".join(sorted(extraMeta))}.'
                    raise ValidationException(msg)
                specs = []
                for meta in extra_params:
                    if meta == 'enabled':
                        specs.append({
                            'name': meta,
                            'type': bool,
                            'exception_msg': f'Extension field "{meta}" must be a boolean.',
                        })
                    else:
                        specs.append({
                            'name': meta,
                            'type': (str,),
                            'exception_msg': f'Extension field "{meta}" must be a non-empty string.',
                        })
                for spec in specs:
                    if doc['meta'].get(spec['name']) and not isinstance(
                       doc['meta'][spec['name']], spec['type']):
                        msg = spec['exception_msg']
                        raise ValidationException(msg)
            duplicateQuery = {
                'name': doc['name'],
                'os': doc['meta']['os'],
                'arch': doc['meta']['arch'],
                'app_revision': doc['meta']['app_revision'],
            }
            if '_id' in doc:
                duplicateQuery['_id'] = {'$ne': doc['_id']}
            if self.findOne(duplicateQuery, fields=['_id']):
                msg = 'An Extension with this name and characteristics already exists.'
                raise ValidationException(msg)
        return doc
