import logging
import os

from django.core.management.base import BaseCommand

from ...clients import FileStackClient
from ...models import Resource
from ...conf import settings

logger = logging.getLogger('filestack')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('directory', nargs='+', type=str)

    def handle(self, *args, **kwargs):
        logger.info("Script: Upload filestack files from folder")
        directory = kwargs.get("directory")[0]
        client = FileStackClient()
        resources = []

        for _, _, files in os.walk(directory):

            for filename in files:
                filepath = '{}/{}'.format(directory, filename)
                filelink = client.upload(filepath=filepath)
                metadata = filelink.metadata()

                defaults = {
                    'link': filelink.url,
                    'url': filelink.url,
                    'type': settings.RESOURCE_CH_TYPE_FILESTACK,
                    'status': settings.RESOURCE_CH_STATUS_AVAILABLE,
                    'sections': [],
                    'extra_data': metadata
                }

                resource, _ = Resource.objects.get_or_create(
                    name=filename)
                resource.__dict__.update(**defaults)
                resource.save()
                resources.append(resource)

        self.stdout.write('\nResources uploaded:\n')

        for resource in resources:
            print(resource.get_handle(), resource.extra_data)

        logger.info("Script finish: Upload filestack files from folder")
