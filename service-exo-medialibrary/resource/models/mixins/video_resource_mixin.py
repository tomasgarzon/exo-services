from embed_video.backends import detect_backend, UnknownBackendException
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from ...conf import settings
from ...clients import VimeoClient
from ..tag import Tag


class VideoResourceMixin:

    @property
    def backend(self):
        return detect_backend(self.link) if self.link else None

    @property
    def vimeo_client(self):
        return VimeoClient()

    def get_code(self):
        return self.backend.code if self.backend else None

    @property
    def internal(self):
        try:
            internal = detect_backend(self.url).is_internal
        except (UnknownBackendException, TypeError):
            internal = False

        return internal

    def get_video_iframe(self):
        width = self.get_video_width()
        height = self.get_video_height()
        return self.backend.get_embed_code(width, height) if self.link else ''

    def get_video_width(self):
        return settings.RESOURCE_VIDEO_DEFAULT_WIDTH

    def get_video_height(self):
        return settings.RESOURCE_VIDEO_DEFAULT_HEIGHT

    def set_tags_in_vimeo(self):
        tags = self.tags.all().values_list("slug", flat=True)
        return self.vimeo_client.set_video_tags(self.get_code(), tags)

    def set_video_tags_from_vimeo(self):
        self.tags.clear()
        tags = self.vimeo_client.get_video_tags(self.get_code())
        vimeo_tags = Tag.objects.create_tags_vimeo(tags)
        Tag.objects.add_tags_to_resource(vimeo_tags, self)

    def upload_video_async(self, validated_data):
        layer = get_channel_layer()
        return async_to_sync(layer.send)(
            settings.RESOURCE_UPLOAD_CHANNEL_NAME, {
                "type": "video.upload",
                "pk": self.pk
            })

    def notificate_update_websocket(self):
        layer = get_channel_layer()
        return async_to_sync(layer.group_send)(
            settings.RESOURCE_UPLOAD_WEBSOCKET_GROUP_NAME, {
                'type': 'video.updated',
                'pk': self.pk
            })
