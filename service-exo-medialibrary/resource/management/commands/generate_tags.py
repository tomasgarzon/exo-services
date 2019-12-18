import logging

from django.core.management.base import BaseCommand

from ...faker_factories import TagFactory
from ...models import Tag

logger = logging.getLogger('vimeo')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('num_tags', nargs='+', type=int)

    def handle(self, *args, **kwargs):
        num_tags = kwargs.get("num_tags")[0]
        tags = TagFactory.create_batch(size=num_tags)
        Tag.objects.create_tags_vimeo(tags)
