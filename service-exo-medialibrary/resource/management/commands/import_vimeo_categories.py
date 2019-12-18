import logging

from django.core.management.base import BaseCommand

from ...clients import VimeoClient
from ...models import Category

logger = logging.getLogger('vimeo')


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        logger.info("Script init: Import vimeo categories")
        client = VimeoClient()
        Category.objects.create_categories_vimeo(client.get_categories())
        logger.info("Script finished: Import vimeo categories")
