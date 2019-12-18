import requests
import logging

from django.conf import settings

from celery import Task

from utils.external_services import reverse

logger = logging.getLogger('service')


class MarketplaceUserPermsTaskMixin:
    host = settings.SERVICE_EXO_OPPORTUNITIES_HOST
    url = None
    ignore_result = True

    def _get_url(self, uuid):
        kwargs = {'uuid': uuid}
        return '{}{}{}'.format(
            settings.EXOLEVER_HOST,
            settings.SERVICE_EXO_OPPORTUNITIES_HOST,
            reverse(self.url, **kwargs)
        )

    def _get_authorization(self):
        return {
            'USERNAME': settings.AUTH_SECRET_KEY
        }

    def _do_request(self, uuid):
        url = self._get_url(uuid)
        headers = self._get_authorization()
        data = {
            'perm': settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL
        }

        try:
            response = requests.post(url, json=data, headers=headers)
            assert response.status_code == requests.codes.ok
        except Exception as err:
            message = 'Exception: {}-{}'.format(err, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.json(), url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)


class AddMarketplaceUserPermsTask(
        MarketplaceUserPermsTaskMixin,
        Task):
    name = 'AddMarketplaceUserPermsTask'
    url = 'opportunities-add-user-permission'

    def run(self, uuid, *args, **kwargs):
        if not settings.POPULATOR_MODE:
            self._do_request(uuid)


class RemoveMarketplaceUserPermsTask(
        MarketplaceUserPermsTaskMixin,
        Task):
    name = 'RemoveMarketplaceUserPermsTask'
    url = 'opportunities-remove-user-permission'

    def run(self, uuid, *args, **kwargs):
        if not settings.POPULATOR_MODE:
            self._do_request(uuid)
