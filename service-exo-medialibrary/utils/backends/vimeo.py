from django.conf import settings

from embed_video.backends import VimeoBackend
from resource.clients import VimeoClient

from .mixins import VideoBackendMixin


class VimeoCustomBackend(VideoBackendMixin, VimeoBackend):
    client = VimeoClient
    type_resource = settings.RESOURCE_CH_TYPE_VIDEO_VIMEO
    is_internal = False

    def is_valid_response(self, resource_info):
        return resource_info is not None

    def get_thumbnail(self, resource_info):
        return resource_info.get("pictures").get("sizes")[3].get("link")

    def post_upload_resource(self, resource):
        resource.set_as_available()
