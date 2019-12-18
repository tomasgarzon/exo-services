import requests
import logging

from django.conf import settings


logger = logging.getLogger('service')


class EmailMixin:
    URL_GROUPS = '{}/api/accounts/groups/{}/'

    def get_group_destinataries(self, group_name):
        url = self.URL_GROUPS.format(
            settings.EXOLEVER_HOST,
            group_name)
        response = None

        try:
            response = requests.get(
                url,
                headers={'USERNAME': settings.AUTH_SECRET_KEY})
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
            response = None

        if response and response.status_code == requests.codes.ok:
            return response.json().get('user_set')
        return None
