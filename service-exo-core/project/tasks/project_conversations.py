import logging
import requests

from celery import Task

from django.contrib.auth import get_user_model
from django.apps import apps
from django.conf import settings

from custom_auth.jwt_helpers import _build_jwt
from utils.external_services import reverse

from ..conversation_helpers import create_conversation_groups


logger = logging.getLogger('service')


class CreateConversationProjectTask(Task):
    name = 'CreateConversationProjectTask'
    ignore_result = True

    def _get_authorization(self, user_from):
        token = _build_jwt(user_from)
        return {'Authorization': 'Bearer ' + token}

    def get_host(self):
        if settings.POPULATOR_MODE:
            return None
        return '{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_CONVERSATIONS_HOST)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'CreateConversationProjectTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def run(self, *args, **kwargs):
        Project = apps.get_model('project', 'Project')
        try:
            project = Project.objects.get(pk=kwargs.get('project_id'))
        except Project.DoesNotExist:
            return

        user_from = get_user_model().objects.get(pk=kwargs.get('user_from_id'))
        logging.info('Project {}, creating conversations'.format(project.name))

        groups = create_conversation_groups(project)

        headers = self._get_authorization(user_from)
        url = self.get_host()
        if not url:
            return None
        url += reverse('create-conversation-group', uuid=str(project.uuid))
        data = {
            'user_from': str(user_from.uuid),
            'groups': groups,
            'group_type': 'P',  # CH_PROJECT
        }
        try:
            requests.post(url, json=data, headers=headers)
        except Exception as err:
            message = 'Exception: {}-{}'.format(err, url)
            logger.error(message)
            self.retry(countdown=10, max_retries=20)
