import vimeo
import math
import logging

from django.conf import settings
from django.core.exceptions import ValidationError

from requests.exceptions import ReadTimeout, ConnectionError

from embed_video.backends import detect_backend

logger = logging.getLogger('vimeo')


class VimeoClient:
    """
    https://developer.vimeo.com/api/endpoints/videos
    """

    URL_ME = '/me'
    URL_ALBUMS = '/me/albums'
    URL_VIDEOS = '/me/videos?per_page={per_page}'
    URL_VIDEOS_PAGINATED = '/me/videos?page={page}&per_page={per_page}&fields={fields}'
    URL_VIDEO_CREATE = '/me/videos'
    URL_VIDEO_INFO = '/videos/{video_id}'
    URL_VIDEO_EDIT = '/videos/{video_id}'
    URL_VIDEO_TAGS_ADD = '/videos/{video_id}/tags/{word}'
    URL_VIDEO_TAGS = '/videos/{video_id}/tags?fields={fields}'
    URL_VIDEO_THUMBNAIL = '/videos/{video_id}/pictures'
    URL_CATEGORIES = '/categories?per_page={per_page}&fields={fields}'
    URL_VIDEO_CATEGORIES = '/videos/{video_id}/categories?fields={fields}'
    URL_VIDEO_ALLOW_DOMAIN = '/videos/{video_id}/privacy/domains/{domain}'
    URL_VIDEO_DOMAINS = '/videos/{video_id}/privacy/domains?fields={fields}'
    VIDEO_FIELDS = 'name,link,description,status,duration,created_time,modified_time,pictures.sizes.link'
    CATEGORY_FIELDS = 'name,subcategories.name'
    TAG_FIELDS = 'name,tag,canonical'
    DOMAIN_FIELDS = 'domain'
    PER_PAGE = 50

    def __init__(self):
        self.client = vimeo.VimeoClient(
            token=settings.VIMEO_TOKEN,
            key=settings.VIMEO_CLIENT_ID,
            secret=settings.VIMEO_CLIENT_SECRET)

    def log(self, msg, url, exception=None):
        logger.error('{}: {}-{}'.format(msg, url, getattr(exception, 'message', '')))

    def get_response(self, url, data=True):
        response_value = None
        try:
            response = self.client.get(url).json()
            error = response.get("error")
            if error:
                raise ValidationError(error)
            else:
                response_value = response.get("data") if data else response

        except vimeo.auth.GrantFailed:
            self.log("vimeo.auth.GrantFailed", url)
        except vimeo.exceptions.APIRateLimitExceededFailure as exception:
            self.log("vimeo.exceptions.APIRateLimitExceededFailure",
                     url, exception)
        except ReadTimeout:
            self.log("requests.exceptions.ReadTimeout", url)
        except ConnectionError:
            self.log("requests.exceptions.ConnectionError", url)
        except ValidationError:
            self.log("exceptions.ValidationError", url)
        return response_value

    def get_profile(self):
        return self.get_response(self.URL_ME)

    def get_albums(self):
        return self.get_response(self.URL_ALBUMS)

    def get_categories(self):
        url = self.URL_CATEGORIES.format(
            fields=self.CATEGORY_FIELDS,
            per_page=self.PER_PAGE)
        return self.get_response(url)

    def get_videos_paginated(self, page=1):
        url = self.URL_VIDEOS_PAGINATED.format(
            fields=self.VIDEO_FIELDS,
            page=page,
            per_page=self.PER_PAGE)
        return self.get_response(url)

    def get_video_tags(self, video_id):
        url = self.URL_VIDEO_TAGS.format(
            video_id=video_id,
            fields=self.TAG_FIELDS)
        return self.get_response(url)

    def get_video_categories(self, video_id):
        url = self.URL_VIDEO_CATEGORIES.format(
            video_id=video_id,
            fields=self.CATEGORY_FIELDS,
            per_page=self.PER_PAGE)
        return self.get_response(url)

    def get_video_thumbnails(self, video_id):
        url = self.URL_VIDEO_THUMBNAIL.format(
            video_id=video_id)
        return self.get_response(url)

    def get_video_id(self, video_data):
        backend = detect_backend(video_data.get("link"))
        return int(backend.code)

    def get_video_num_pages(self):
        url = self.URL_VIDEOS.format(per_page=self.PER_PAGE)
        response = self.get_response(url, False)
        pages = response.get("total") / response.get("per_page")
        return math.ceil(pages)

    def get_video_domains(self, video_id):
        url = self.URL_VIDEO_DOMAINS.format(
            video_id=video_id,
            fields=self.DOMAIN_FIELDS)
        return self.get_response(url)

    def get_video_info(self, video_id):
        url = self.URL_VIDEO_INFO.format(video_id=video_id)
        return self.get_response(url, data=False)

    def set_video_domain_allowed(self, video_id, domain):
        url = self.URL_VIDEO_ALLOW_DOMAIN.format(
            video_id=video_id,
            domain=domain)
        return self.client.put(url)

    def set_video_privacy_embed(self, video_id):
        url = self.URL_VIDEO_EDIT.format(
            video_id=video_id)
        data = {"privacy": {"embed": "whitelist"}}
        return self.client.patch(url, data=data)

    def set_video_tags(self, video_id, tags):
        for tag in tags:
            url = self.URL_VIDEO_TAGS_ADD.format(
                video_id=video_id,
                word=tag)
            response = self.client.put(url)
        return response

    def delete_video(self, video_id):
        url = self.URL_VIDEO_EDIT.format(video_id=video_id)
        return self.client.delete(url)

    def upload_video(self, name, description, link):
        url = self.URL_VIDEO_CREATE
        data = {
            "upload": {
                "approach": "pull",
                "link": link
            },
            "name": name,
            "description": description,
            "privacy": {
                "embed": "whitelist",
                "download": False
            }
        }
        return self.client.post(url, data=data)
