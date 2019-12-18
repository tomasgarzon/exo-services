import re

from django.core.exceptions import ValidationError

from embed_video.backends import VideoBackend
from rest_framework import status


class VideoBackendMixin(VideoBackend):
    is_secure = True

    def get_url_parsed(self, url):
        return url

    def get_video_info(self, resource):
        return self.client().get_video_info(self.code)

    def upload_resource(self, resource):
        resource_info = self.get_video_info(resource)

        if not self.is_valid_response(resource_info):
            resource.set_as_error(websocket=True)
        else:
            resource_data = {
                'type': self.type_resource,
                'link': self._url,
                'thumbnail': self.get_thumbnail(resource_info),
                'duration': self.get_video_duration(resource_info),
                'extra_data': resource_info
            }
            resource.__dict__.update(resource_data)
            resource.save()
            self.post_upload_resource(resource)
        return resource

    def get_video_duration(self, resource_info):
        return resource_info.get("duration")

    def post_upload_resource(self, resource):
        pass


class VideoInternalMixin(VideoBackendMixin):
    re_code = re.compile(r'''vimeo\.com/(video/)?(channels/(.*/)?)?(?P<code>[0-9]+)''', re.I)
    pattern_url = '{protocol}://player.vimeo.com/video/{code}'
    pattern_info = '{protocol}://vimeo.com/api/v2/video/{code}.json'
    is_internal = True

    def get_url_parsed(self, url):
        raise NotImplementedError

    def is_valid_response(self, resource_info):
        return resource_info is not None

    def get_video_info(self, resource):
        url = self.get_url_parsed(resource.url)
        response = self.client().upload_video(resource.name, resource.description, url)

        if response.status_code == status.HTTP_201_CREATED:
            response_json = response.json()
            resource.link = response_json.get("link")
            self._url = response_json.get("link")
            self.set_resource_tags_in_vimeo(resource)
            return response_json
        else:
            raise ValidationError('Upload error')

    def get_thumbnail(self, resource_info):
        return resource_info.get("pictures").get("sizes")[3].get("link")

    def set_resource_tags_in_vimeo(self, resource):
        try:
            response_tags = resource.set_tags_in_vimeo()
            if not response_tags.status_code == status.HTTP_200_OK:
                self.delete_invalid_resource(resource)
                raise ValidationError('Upload error')
        except Exception as e:
            self.delete_invalid_resource(resource)
            raise ValidationError('Upload error: {}'.format(e))

    def delete_invalid_resource(self, resource):
        resource.delete()
