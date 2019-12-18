import logging
import random

from django.core.management.base import BaseCommand

from ...faker_factories import VideoFactory
from ...models import Resource, Tag

logger = logging.getLogger('vimeo')


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('num_videos', nargs='+', type=int)
        parser.add_argument('num_tags', nargs='+', type=int)

    def handle(self, *args, **kwargs):
        num_videos = kwargs.get("num_videos")[0]
        num_tags = kwargs.get("num_tags")[0]
        video_resources = VideoFactory.create_batch(size=num_videos)

        for video_data in video_resources:
            resource, created = Resource.objects.update_or_create(**video_data)
            resource.tags.clear()

            for i in range(num_tags):
                number = random.randint(0, Tag.objects.count())
                tag = Tag.objects.all()[number]
                resource.tags.add(tag)
