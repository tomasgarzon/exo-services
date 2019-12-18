import isodate

from django.conf import settings

from embed_video.backends import YoutubeBackend

from resource.clients import YoutubeClient

from .mixins import VideoBackendMixin


class YoutubeCustomBackend(VideoBackendMixin, YoutubeBackend):
    client = YoutubeClient
    type_resource = settings.RESOURCE_CH_TYPE_VIDEO_YOUTUBE
    is_internal = False

    def is_valid_response(self, resource_info):
        return resource_info and len(resource_info.get("items"))

    def get_video_duration(self, resource_info):
        item = resource_info.get("items")[0]
        duration = item.get("contentDetails").get("duration")
        return isodate.parse_duration(duration).total_seconds()

    def get_thumbnail(self, resource_info):
        return self.get_thumbnail_url()

    def post_upload_resource(self, resource):
        resource.set_as_available()
