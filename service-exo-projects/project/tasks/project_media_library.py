import requests
import logging
from celery import Task

from django.conf import settings
from django.apps import apps


logger = logging.getLogger('library')
SPRINT_AUTOMATED = 'sprintautomated'
URL_ASSIGN_RESOURCES_TO_PROJECT = 'api/resources/post-save-project/'


class AssignResourcesToProjectTask(Task):
    name = 'AssignResourcesToProjectTask'
    ignore_result = True

    def _get_authorization(self):
        return {'USERNAME': settings.AUTH_SECRET_KEY}

    def _get_url(self):
        url = '{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.MEDIA_LIBRARY_HOST)
        return url + URL_ASSIGN_RESOURCES_TO_PROJECT

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return
        Project = apps.get_model('project', 'Project')
        try:
            project = Project.objects.get(pk=kwargs.get('project_id'))
        except Project.DoesNotExist:
            logger.info('Project does not exists {}'.format(kwargs.get('project_id')))
            return
        url = self._get_url()

        payload = {
            'uuid': str(project.uuid),
            'type_project_lower': SPRINT_AUTOMATED
        }

        headers = self._get_authorization()

        try:
            requests.post(url, json=payload, headers=headers)
        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}'.format(err, url)
            logger.error(message)
        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}'.format(err, url)
            logger.error(message)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
