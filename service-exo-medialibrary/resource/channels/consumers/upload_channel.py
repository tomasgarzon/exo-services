import logging

from django.core.exceptions import ObjectDoesNotExist

from channels.consumer import SyncConsumer

from embed_video.backends import detect_backend

from ...models import Resource

logger = logging.getLogger('library')


class UploadChannelConsumer(SyncConsumer):

    def video_upload(self, event):
        try:
            resource = Resource.objects.get(pk=event['pk'])
            detect_backend(resource.url).upload_resource(resource=resource)
            logger.info("Async task video upload: {}".format(resource.url))
        except ObjectDoesNotExist:
            logger.error("UploadChannelConsumer.video_upload.ObjectDoesNotExist: {}".format(event.get("pk")))
