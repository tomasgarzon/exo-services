import logging

from django.core.exceptions import ObjectDoesNotExist

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from ...models import Resource
from ...api.serializers.resource_list import ResourceListSerializer
from ...conf import settings

logger = logging.getLogger('library')


class LibraryWebsocketConsumer(JsonWebsocketConsumer):

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            settings.RESOURCE_UPLOAD_WEBSOCKET_GROUP_NAME,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            settings.RESOURCE_UPLOAD_WEBSOCKET_GROUP_NAME,
            self.channel_name
        )
        self.close()

    def receive_json(self, content, **kwargs):
        self.send_json(content)

    def video_updated(self, event):
        try:
            instance = Resource.objects.get(pk=event.get("pk"))
            data = {
                'type': settings.RESOURCE_UPLOAD_WEBSOCKET_GROUP_NAME,
                'payload': ResourceListSerializer(instance).data
            }
            self.send_json(data)
        except ObjectDoesNotExist:
            logger.error("LibraryWebsocketConsumer.video_updated.ObjectDoesNotExist: {}".format(event.get("pk")))
