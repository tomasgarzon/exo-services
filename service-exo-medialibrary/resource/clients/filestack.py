import requests
import logging

from django.conf import settings

from filestack import Client

logger = logging.getLogger('vimeo')


class FileStackClient:
    logger = 'filestack'
    URL_API = 'https://www.filestackapi.com/api/file'

    def __init__(self, *args, **kwargs):
        self.client = Client(settings.FILESTACK_KEY)

    def log(self, msg, url, exception=None):
        logger.error('{}: {}-{}'.format(msg, url, getattr(exception, 'message', '')))

    def get_video_info(self, resource):
        handle = resource.get_handle()
        url = '{}/{}/metadata'.format(self.URL_API, handle)
        return requests.get(url).json()

    def get_metadata(self, handle):
        url = '{}/{}/metadata'.format(self.URL_API, handle)
        return requests.get(url).json()

    def upload(self, filepath=None, file_obj=None):
        return self.client.upload(filepath=filepath, file_obj=file_obj)

    def upload_png(self, filepath, intelligent=False):
        params = {'mimetype': 'image/png'}
        filelink = self.client.upload(filepath=filepath, params=params, intelligent=intelligent)
        return filelink

    def upload_url(self, url, intelligent=False):
        return self.client.upload(url=url)

    def get_url_screenshot(self, url, width, height):
        screenshot = self.client.urlscreenshot(external_url=url, width=width, height=height)

        try:
            filelink = screenshot.store()
            url = filelink.url
        except Exception as exception:
            self.log("FileStackClient.get_url_screenshot.Exception", url, exception)
            url = None
        return url

    def get_filelink_tags(self, filelink):
        return filelink.tags()

    def rotate_filelink(self, filelink, width, height, deg=90):
        transform = filelink.resize(width=width, height=height).rotate(deg=deg)
        new_filelink = transform.store()
        return new_filelink
