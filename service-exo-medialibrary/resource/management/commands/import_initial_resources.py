import logging

from django.core.management.base import BaseCommand

from ...clients import VimeoClient
from ...models import Resource
from ...conf import settings

logger = logging.getLogger('vimeo')


class Command(BaseCommand):

    def is_video_available(self, video_status):
        return video_status == settings.RESOURCE_PROVIDER_STATUS_AVAILABLE

    def is_video_error(self, video_status):
        return video_status == settings.RESOURCE_PROVIDER_STATUS_UPLOADING_ERROR

    def update_or_create_resource(self, resource, video_data):
        try:
            resource, created = Resource.objects.update_or_create(**video_data)
            self.stdout.write('Resource with pk {} updated'.format(resource.pk))
        except Exception as e:
            logger.error('commands.import_vimeo_resources.update_or_create.Exception: {}'.format(e))

    def set_resource_status_error(self, resource):
        self.stdout.write('Resource with pk {} error'.format(resource.pk))
        resource.set_as_error(websocket=False)

    def set_video_thumbnail(self, video_data):
        video_pictures = video_data.get('pictures')

        if video_pictures and len(video_pictures):
            positions = [0, 1, 2, 3]

            for position in positions:
                try:
                    thumbnail = video_pictures.get('sizes')[position]
                    video_data['thumbnail'] = thumbnail.get('link')
                except IndexError:
                    pass
        return video_data

    def handle(self, *args, **kwargs):
        self.stdout.write('Script init: Import initial resources')
        logger.info('Script init: Import initial resources')

        client = VimeoClient()
        num_pages = client.get_video_num_pages()

        for page in range(0, num_pages):
            videos = client.get_videos_paginated(page + 1)

            for video_data in videos:
                video_link = video_data.get('link')
                resource, _ = Resource.objects.get_or_create(link=video_link)

                if resource.is_draft:
                    video_status = video_data.get('status')
                    video_data = self.set_video_thumbnail(video_data)

                    if self.is_video_available(video_status):
                        self.update_or_create_resource(resource, video_data)
                    elif self.is_video_error(video_status):
                        self.set_resource_status_error(resource)

        self.stdout.write('Script finished: Import initial resources')
        logger.info('Script finished: Import initial resources')
