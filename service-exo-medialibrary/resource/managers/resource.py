import requests
from requests import exceptions
import logging

from django.db import models
from django.db.models import F
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from auth_uuid.jwt_helpers import _build_jwt

from ..querysets.resource import ResourceQueryset
from ..models import Tag
from ..conf import settings


class ResourceManager(models.Manager):
    queryset_class = ResourceQueryset
    use_for_related_fields = True
    use_in_migrations = True

    def get_queryset(self):
        return self.queryset_class(self.model, using=self._db)

    def filter_by_url(self, url):
        return self.get_queryset().filter_by_url(url)

    def filter_by_tags(self, tags):
        return self.get_queryset().filter_by_tags(tags)

    def filter_by_status(self, status):
        return self.get_queryset().filter_by_status(status)

    def filter_by_type(self, type_resource):
        return self.get_queryset().filter_by_type(type_resource)

    def filter_by_section(self, section):
        return self.get_queryset().filter_by_section(section)

    def filter_by_uuid(self, uuid):
        return self.get_queryset().filter_by_uuid(uuid)

    def drive(self):
        return self.get_queryset().drive()

    def dropbox(self):
        return self.get_queryset().dropbox()

    def available(self):
        return self.get_queryset().available()

    def draft(self):
        return self.get_queryset().draft()

    def draft_and_available(self):
        return self.get_queryset().draft_and_available()

    def removed(self):
        return self.get_queryset().removed()

    def error(self):
        return self.get_queryset().error()

    def get_development_resources(self):
        dev_tag, _ = Tag.objects.get_development_tag()
        return self.filter_by_tags([dev_tag])

    def update_or_create(self, *args, **kwargs):
        defaults = {
            'name': kwargs.get('name'),
            'link': kwargs.get('link'),
            'url': kwargs.get('url', F('url')),
            'type': kwargs.get('type', F('type')),
            'status': self.model.get_provider_status(kwargs.get("status")),
            'duration': kwargs.get('duration', None),
            'description': kwargs.get('description', None),
            'thumbnail': kwargs.get('thumbnail', None),
            'sections': kwargs.get('sections', F('sections')),
            'extra_data': kwargs
        }
        return super().update_or_create(link=kwargs.get('link'), defaults=defaults)

    def create_internal_messages(self, resources, level):
        logger = logging.getLogger('library')

        for key, value in resources.items():
            try:
                user = get_user_model().objects.get(pk=key)
            except ObjectDoesNotExist:
                continue
            token = _build_jwt(user)
            header = 'Bearer ' + token
            code = settings.RESOURCE_CH_CODE_MESSAGE_UPLOAD
            num_videos_ready = value

            variables = {
                'counter': num_videos_ready
            }
            data = {
                'user': user.uuid,
                'code': code,
                'level': level,
                'can_be_closed': True,
                'read_when_login': True,
                'variables': variables
            }
            url = '{}/api/internal-messages/'.format(
                settings.EXOLEVER_HOST)
            try:
                response = requests.post(
                    url,
                    json=data,
                    headers={'Authorization': header})
                if not response.ok:
                    logger.error('Wrong response {} - {}'.format(
                        response.status_code,
                        response.content))
            except exceptions.RequestException as e:
                logger.error('Exception during call {}'.format(e))
