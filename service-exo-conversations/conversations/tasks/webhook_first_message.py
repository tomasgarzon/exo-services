import logging
import requests

from celery import Task

from django.conf import settings

from ..models import Message


logger = logging.getLogger('celery-task')
URL_WEBOOK = 'api/webhook/first-message/'


class WebhookOpportunityFirstMessageTask(Task):
    name = 'WebhookOpportunityFirstMessageTask'

    def _get_authorization(self):
        return {'USERNAME': settings.AUTH_SECRET_KEY}

    def get_url(self):
        host = settings.SERVICE_OPPORTUNITIES_HOST
        url = settings.EXOLEVER_HOST + host + URL_WEBOOK
        return url

    def get_data(self, user, message, conversation):
        data = {
            'message': message.message,
            'created_by_uuid': message.created_by.uuid.__str__(),
            'other_user_uuid': user.uuid.__str__(),
            'opportunity_uuid': conversation.uuid_related_object.__str__(),
        }
        return data

    def run(self, *args, **kwargs):
        message_pk = kwargs.get('pk')

        try:
            message = Message.objects.get(pk=message_pk)
        except Message.DoesNotExist:
            logger.error('Message does not exist')
            raise Exception()
        url = self.get_url()
        headers = self._get_authorization()
        conversation = message.conversation
        for conversation_user in conversation.users.exclude(user=message.created_by):
            data = self.get_data(conversation_user.user, message, conversation)
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
