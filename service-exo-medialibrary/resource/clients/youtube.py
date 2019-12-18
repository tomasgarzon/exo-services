import requests
import json
import logging

from requests.exceptions import ReadTimeout, ConnectionError

from rest_framework import status

from ..conf import settings

logger = logging.getLogger('youtube')


class YoutubeClient:
    URL_PATTERN = "https://www.googleapis.com/youtube/v3/videos"
    URL_VIDEO_INFO = "{pattern}?part=contentDetails,snippet&id={video_id}&key={key}"

    def __init__(self):
        self.key = settings.YOUTUBE_API_KEY

    def log(self, msg, url, exception=None):
        logger.error('{}: {}-{}'.format(msg, url, getattr(exception, 'message', '')))

    def get_video_info(self, video_id):
        response_value = None
        url = self.URL_VIDEO_INFO.format(
            pattern=self.URL_PATTERN,
            video_id=video_id,
            key=self.key)

        try:
            response = requests.get(url)
        except ConnectionError:
            self.log("requests.exceptions.ConnectionError", url)
            self.log("clients.Youtube.ConnectionError", url)
        except ReadTimeout:
            self.log("requests.exceptions.ReadTimeout", url)
            self.log("clients.Youtube.ReadTimeout", url)

        if response.status_code == status.HTTP_200_OK:
            response_value = json.loads(response.content)
        else:
            self.log("resource.clients.youtube.error", url)
            self.log("clients.Youtube.ResponseError", url)

        return response_value
