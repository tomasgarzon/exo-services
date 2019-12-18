import re

from django.conf import settings

from resource.clients import FileStackClient

from .mixins import VideoBackendMixin


class FileStackCustomBackend(VideoBackendMixin):
    client = FileStackClient
    re_detect = re.compile(r'^(http(s)?://(www\.)?)?cdn.filestackcontent\.com/.*', re.I)
    type_resource = settings.RESOURCE_CH_TYPE_FILESTACK

    def is_valid_response(self, resource_info):
        return resource_info is not None

    def get_video_info(self, resource):
        return self.client().get_video_info(resource)

    def get_thumbnail(self, resource_info, resource):
        return self.client().get_url_screenshot(url=self._url, width=200, height=200)

    def get_video_duration(self, resource_info):
        return None

    def get_embed_code(self, width, height):
        return ''

    def post_upload_resource(self, resource):
        resource.set_as_available()
