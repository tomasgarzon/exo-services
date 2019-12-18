import logging

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from embed_video.backends import detect_backend

from ...clients import VimeoClient
from ...models import Resource
from ...conf import settings

logger = logging.getLogger('vimeo')


class Command(BaseCommand):

    def exists_dev_tag(self, video_link):
        client = VimeoClient()
        is_dev = False
        code = detect_backend(video_link).code

        try:
            tags = client.get_video_tags(code)

            for tag in tags:
                if tag.get('name') == settings.RESOURCE_DEVELOPMENT_TAG_NAME:
                    is_dev = True
        except Exception as e:
            logger.error('commands.import_vimeo_resources.get_video_tags.ValueError: {}'.format(e))
            is_dev = True

        return is_dev

    def create_internal_messages(self):
        Resource.objects.create_internal_messages(
            resources=self.resources_updated,
            level=settings.RESOURCE_CH_MESSAGE_SUCCESS)

        Resource.objects.create_internal_messages(
            resources=self.resources_error,
            level=settings.RESOURCE_CH_MESSAGE_ERROR)

    def get_resources_links_deleted(self):
        return Resource.objects.removed().values_list('link', flat=True)

    def get_resources_links_dev(self):
        return Resource.objects.get_development_resources().values_list('link', flat=True)

    def get_video_status(self, video_data):
        return video_data.get('status')

    def update_or_create_resource(self, resource, video_data):
        try:
            resource, created = Resource.objects.update_or_create(**video_data)

            try:
                self.resources_updated[resource.created_by.pk] += 1
            except KeyError:
                self.resources_updated[resource.created_by.pk] = 1
            except AttributeError:
                pass

            self.stdout.write('Resource with pk {} updated'.format(resource.pk))

        except Exception as e:
            logger.error('commands.import_vimeo_resources.update_or_create.Exception: {}'.format(e))

    def set_resource_status_error(self, resource):
        self.stdout.write('Resource with pk {} error'.format(resource.pk))

        resource.set_as_error()

        try:
            self.resources_error[resource.created_by.pk] += 1
        except KeyError:
            self.resources_error[resource.created_by.pk] = 1
        except AttributeError:
            pass

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

    def is_video_available(self, video_status):
        return video_status == settings.RESOURCE_PROVIDER_STATUS_AVAILABLE

    def is_video_error(self, video_status):
        return video_status == settings.RESOURCE_PROVIDER_STATUS_UPLOADING_ERROR

    def is_resource_deleted(self, video_link):
        return video_link in self.resources_deleted

    def is_resource_dev_local(self, video_link):
        return video_link in self.resources_dev_local

    def is_resource_dev_vimeo(self, video_link):
        return video_link in self.resources_dev_vimeo

    def handle(self, *args, **kwargs):
        self.stdout.write('Script init: Import vimeo videos')
        logger.info('Script init: Import vimeo videos')

        client = VimeoClient()
        num_pages = client.get_video_num_pages()

        self.resources_updated = {}
        self.resources_error = {}
        self.resources_dev_vimeo = []
        self.resources_dev_local = self.get_resources_links_dev()
        self.resources_deleted = self.get_resources_links_deleted()

        for page in range(0, num_pages):
            videos = client.get_videos_paginated(page + 1)

            for video_data in videos:
                video_link = video_data.get('link')

                try:
                    resource, _ = Resource.objects.get_or_create(link=video_link)

                    if resource.is_draft:
                        status = self.get_video_status(video_data)
                        video_data = self.set_video_thumbnail(video_data)

                        if self.exists_dev_tag(video_link):
                            self.resources_dev_vimeo.append(video_link)

                        if self.is_resource_deleted(video_link):
                            continue
                        elif (self.is_resource_dev_local(video_link) or self.is_resource_dev_vimeo(video_link)) \
                                and settings.UPLOAD_REAL:
                            continue

                        if self.is_video_available(status):
                            self.update_or_create_resource(resource, video_data)
                        elif self.is_video_error(status):
                            self.set_resource_status_error(resource)

                except ObjectDoesNotExist:
                    logger.error('commands.import_vimeo_resources.ObjectDoesNotExist: {}'.format(video_link))
                    continue

        self.create_internal_messages()

        self.stdout.write('Script finished: Import vimeo videos')
        logger.info('Script finished: Import vimeo videos')
