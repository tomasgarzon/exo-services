import logging
import requests

from celery import Task

from django.conf import settings

from ..models import Applicant


logger = logging.getLogger('celery-task')

URL_CREATE_MESSAGE_IN_GROUP = 'api/{}/conversations/create-message/'


class AddMessageToConversationTask(Task):
    name = 'Add a message to conversation created for this applicant'

    def _get_authorization(self):
        return {'USERNAME': settings.AUTH_SECRET_KEY}

    def get_host(self, opp):
        host = settings.SERVICE_CONVERSATIONS_HOST
        if host is None:
            return None
        if not host.startswith('http'):
            host = settings.EXOLEVER_HOST + host
        host += URL_CREATE_MESSAGE_IN_GROUP.format(opp.uuid.__str__())
        return host

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        msg = 'CreateOportunityConversationTask.on_failure: {}-{}'.format(task_id, exc)
        logger.error(msg)
        super().on_failure(exc, task_id, args, kwargs, einfo)

    def create_message_for_applicant(self, opportunity, applicant, user_from, message):
        headers = self._get_authorization()
        url = self.get_host(opportunity)
        if not url:
            return None

        data = {
            'conversation_created_by': applicant.user.uuid.__str__(),
            'created_by': user_from,
            'message': message,
        }
        try:
            response = requests.post(url, json=data, headers=headers)
            assert response.status_code == requests.codes.ok
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)
        except Exception as err:
            message = 'Exception: {}-{}'.format(err, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)

    def run(self, *args, **kwargs):
        applicant_pk = kwargs.get('app_pk')
        try:
            applicant = Applicant.objects.get(pk=applicant_pk)
        except Applicant.DoesNotExist:
            logger.error('Applicant does not exist')
            raise Exception()
        opportunity = applicant.opportunity

        self.create_message_for_applicant(
            opportunity, applicant,
            user_from=kwargs.get('user_from'),
            message=kwargs.get('message'))
