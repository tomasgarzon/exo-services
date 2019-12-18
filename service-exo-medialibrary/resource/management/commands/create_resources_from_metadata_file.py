import os
import logging
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from ...models import Resource

logger = logging.getLogger('library')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        """
        Script will read from resources_default.json file resources metadata
        and create them in database
        """
        logger.info('Init: create_resources_from_metadata_file')

        path = 'utils/assignments/populator/resources_default.json'

        if os.path.exists(path):
            with open(path) as content:
                data = json.load(content)
                for key, metadata in data.items():
                    link = 'https://{}/{}'.format(settings.RESOURCE_FILESTACK_CDN_URL, key)

                    defaults = {
                        'link': link,
                        'url': link,
                        'type': settings.RESOURCE_CH_TYPE_FILESTACK,
                        'status': settings.RESOURCE_CH_STATUS_AVAILABLE,
                        'sections': [],
                        'extra_data': metadata
                    }
                    filename = metadata.get('filename')
                    resource, _ = Resource.objects.get_or_create(name=filename)
                    resource.__dict__.update(**defaults)
                    resource.save()
        else:
            logger.error('{} path not exists'.format(path))

        logger.info('Finish: create_resources_from_metadata_file')
