import re

from django.conf import settings

from resource.clients import VimeoClient

from .mixins import VideoInternalMixin


class DropboxCustomBackend(VideoInternalMixin):
    client = VimeoClient
    re_detect = re.compile(r'^(http(s)?://(www\.)?)?dropbox\.com/.*', re.I)
    type_resource = settings.RESOURCE_CH_TYPE_VIDEO_DROPBOX

    def get_url_parsed(self, url):
        url_parsed = url.split("?dl=0")[0].replace(
            "dropbox.com", "dl.dropboxusercontent.com")
        return url_parsed
