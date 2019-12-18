import requests
import logging

from django.conf import settings

from utils.external_services import reverse

from ...tasks import AssignResourcesToProjectTask, AssignProjectToResourceTask

logger = logging.getLogger('library')


class ResourceLibraryMixin:

    def _get_media_libray_authorization(self, user_from):
        return {'USERNAME': settings.AUTH_SECRET_KEY}

    def get_media_library_host(self):
        return '{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.MEDIA_LIBRARY_HOST)

    def get_resources_from_media_library(self, user_from, page, page_size, uuid=''):
        host = self.get_media_library_host()
        if not host:
            logger.error('Media Library not configured')
            return None

        if uuid:
            api_url = reverse('media-library-resource-project-list')
        else:
            api_url = reverse('media-library-resource-list')

        url = '{}{}/?page={}&page_size={}&projects={}'.format(
            host,
            api_url,
            page,
            page_size,
            uuid)
        headers = self._get_media_libray_authorization(user_from)

        try:
            return requests.get(url, data={}, headers=headers)
        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}-{}'.format(err, user_from.id, url)
            logger.error(message)
        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}-{}'.format(err, user_from.id, url)
            logger.error(message)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)

    def assign_resources_from_media_library(self, user_from, type_project=None):
        host = self.get_media_library_host()
        if not host:
            logger.error('Media Library not configured')
            return None
        url = '{}{}/'.format(
            host,
            reverse('media-library-post-save-project'))
        payload = {
            'uuid': str(self.uuid),
            'type_project_lower': type_project or self.type_project_lower
        }
        headers = self._get_media_libray_authorization(user_from)

        AssignResourcesToProjectTask().s(
            url=url,
            data=payload,
            headers=headers
        ).apply_async()

    def add_resource_to_project(self, resource_pk, user_from):
        host = self.get_media_library_host()
        if not host:
            logger.error('Media Library not configured')
            return None
        url = '{}{}/{}/{}/'.format(
            host,
            reverse('media-library-resource-list'),
            resource_pk,
            settings.PROJECT_MEDIA_LIBRARY_API_RESOURCES_LIST_DETAIL_ROUTE_ADD_TO_PROJECTS)
        payload = {
            'uuid': self.uuid.hex,
        }
        headers = self._get_media_libray_authorization(user_from)

        AssignProjectToResourceTask().s(
            url=url,
            data=payload,
            headers=headers
        ).apply_async()

    def remove_resource_to_project(self, resource_pk, user_from):
        host = self.get_media_library_host()
        if not host:
            logger.error('Media Library not configured')
            return None

        url = '{}{}/{}/{}/'.format(
            host,
            reverse('media-library-resource-list'),
            resource_pk,
            settings.PROJECT_MEDIA_LIBRARY_API_RESOURCES_LIST_DETAIL_ROUTE_REMOVE_FROM_PROJECTS)
        payload = {
            'uuid': self.uuid,
        }
        headers = self._get_media_libray_authorization(user_from)

        try:
            return requests.put(url, data=payload, headers=headers)
        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}-{}'.format(err, user_from.id, url)
            logger.error(message)
        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}-{}'.format(err, user_from.id, url)
            logger.error(message)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
