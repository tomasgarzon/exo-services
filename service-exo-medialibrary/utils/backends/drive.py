import re

from django.conf import settings

from resource.clients import VimeoClient

from .mixins import VideoInternalMixin


class GoogleDriveCustomBackend(VideoInternalMixin):
    client = VimeoClient
    re_detect = re.compile(r'^(http(s)?://(www\.)?)?drive.google\.com/.*', re.I)
    type_resource = settings.RESOURCE_CH_TYPE_VIDEO_DRIVE

    def get_url_parsed(self, url):
        video_id = url.split("id=")[1]
        url_parsed = "https://docs.google.com/uc?export=download&id={}".format(video_id)
        return url_parsed
