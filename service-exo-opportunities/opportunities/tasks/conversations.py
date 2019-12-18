import logging
import requests

from celery import Task

from django.contrib.auth import get_user_model
from django.apps import apps
from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt


logger = logging.getLogger('service')

URL_CREATE_CONVERSATION_GROUP = 'api/{}/conversations/create-group/'


class CreateOportunityConversationTask(Task):
    name = 'CreateOportunityConversationTask'

    def _get_authorization(self, user_from):
        token = _build_jwt(user_from)
        return {'Authorization': 'Bearer ' + token}

    def get_host(self, opp):
        host = settings.SERVICE_CONVERSATIONS_HOST
        if host is None:
            return None
        if not host.startswith('http'):
            host = settings.EXOLEVER_HOST + host
        host += URL_CREATE_CONVERSATION_GROUP.format(opp.uuid.__str__())
        return host

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'CreateOportunityConversationTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def run(self, *args, **kwargs):
        Opportunity = apps.get_model('opportunities', 'Opportunity')
        try:
            opportunity = Opportunity.objects.get(pk=kwargs.get('opportunity_id'))
        except Opportunity.DoesNotExist:
            return

        user_from = get_user_model().objects.get(pk=kwargs.get('user_from_id'))
        try:
            user_to = get_user_model().objects.get(
                pk=kwargs.get('user_to_id', None))
        except Exception:
            user_to = None
        logging.info('Opportunity {}, creating conversation'.format(opportunity.title))

        group_name, users, icon = opportunity.get_info_for_start_conversation(
            user_from,
            user_to=user_to)
        groups = [
            {'name': group_name, 'users': users, 'icon': icon}
        ]
        headers = self._get_authorization(user_from)
        url = self.get_host(opportunity)
        if not url:
            return None

        data = {
            'user_from': str(user_from.uuid),
            'groups': groups,
            'group_type': 'O',  # CH_OPPORTUNITY
            'message': kwargs.get('message'),
            'files': kwargs.get('files'),
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            assert response.status_code == requests.codes.ok
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)
