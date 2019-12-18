import logging
import requests

from django.conf import settings

from celery import Task

logger = logging.getLogger('celery')


class SyncParticipantTask(Task):
    name = 'SyncParticipantPublicTask'
    ignore_result = True

    def get_url(self):
        return settings.EXOLEVER_HOST + '/api/accounts/signup-event/'

    def get_headers(self):
        return {'USERNAME': settings.AUTH_SECRET_KEY}

    def run(self, name, email, entry_point, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return None

        logger.info('SyncParticipantTask: {}-{}'.format(name, email))

        data = {
            'name': name,
            'email': email,
            'entry_point': entry_point,
        }

        server_url = self.get_url()

        try:
            requests.post(server_url, data=data, headers=self.get_headers())
        except Exception as err:
            message = 'Exception: {}-{}'.format(err, server_url)
            logger.error(message)
