import json

from django.core.management.base import BaseCommand
from django.conf import settings

from resource.clients import FileStackClient

from ...models import Resource


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        """
        Script will write in resources_default.json file al the info related to filestack resources
        """
        client = FileStackClient()
        output = {}

        for resource in Resource.objects.filter_by_type(settings.RESOURCE_CH_TYPE_FILESTACK):
            handle = resource.get_handle()
            metadata = client.get_metadata(handle)
            output[handle] = metadata

        with open('utils/assignments/populator/resources_default.json', 'w') as outfile:
            json.dump(output, outfile)
