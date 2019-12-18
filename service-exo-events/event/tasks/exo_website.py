import requests
import logging

from django.conf import settings
from django.contrib.auth import get_user_model

from celery import Task

from auth_uuid.jwt_helpers import _build_jwt

logger = logging.getLogger('website')


URL_WEBSITE = 'api/landing/page/'


class WebsiteTaskMixin():
    def get_host(self):
        host = settings.SERVICE_WEBSITE_HOST
        if not host:
            return None
        if not host.startswith('http'):
            host = '{}{}'.format(settings.DOMAIN_NAME, host)
        return host

    def get_url_for_creating(self):
        host = self.get_host()
        if not host:
            return None
        return host + URL_WEBSITE

    def get_url_for_deleting(self, uuid):
        host = self.get_host()
        if not host:
            return None
        return '{}{}{}/'.format(host, URL_WEBSITE, uuid)


class CreateWorkshopWebsiteTask(WebsiteTaskMixin, Task):
    name = 'CreateWorkshopWebsiteTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        uuid = kwargs.get('uuid')
        slug = kwargs.get('slug')
        user_from = kwargs.get('user_from')
        token = _build_jwt(
            get_user_model().objects.get(pk=user_from))
        header = 'Bearer ' + token
        data = {'uuid': uuid, 'slug': slug, 'page_type': 'event'}

        server_url = self.get_url_for_creating()
        if not server_url:
            logger.error('ExO Website not settings properly')
            raise Exception('Wrong website service settings')
        if settings.POPULATOR_MODE:
            return None

        try:
            requests.post(
                server_url,
                data=data,
                headers={'Authorization': header})
        except Exception as err:
            message = 'Exception: {}-{}'.format(err, server_url)
            logger.error(message)


class DeleteWorkshopWebsiteTask(WebsiteTaskMixin, Task):
    name = 'DeleteWorkshopWebsiteTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        uuid = kwargs.get('uuid')
        user_from = kwargs.get('user_from')
        token = _build_jwt(
            get_user_model().objects.get(pk=user_from))
        header = 'Bearer ' + token
        server_url = self.get_url_for_deleting(uuid)
        if not server_url:
            logger.error('ExO Website not settings properly')
            raise Exception('Wrong website service settings')
        if settings.POPULATOR_MODE:
            return None
        try:
            requests.delete(
                server_url,
                headers={'Authorization': header})
        except Exception as err:
            message = 'Exception: {}-{}'.format(err, server_url)
            logger.error(message)
