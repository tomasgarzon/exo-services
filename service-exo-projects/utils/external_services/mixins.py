import requests
import logging

from django.conf import settings

logger = logging.getLogger('service')


class ExternalServiceMixin:
    def __init__(self, *args, **kwargs):
        assert self.host
        self._fix_host()

    def _fix_host(self):
        if not self.host.startswith('http'):
            self.host = settings.EXOLEVER_HOST + self.host

    def _get_authorization(self):
        return {
            'USERNAME': settings.AUTH_SECRET_KEY
        }

    def _do_request(self, url, data={}):
        url = '{}{}'.format(self.host, url)
        headers = self._get_authorization()
        response = []

        try:
            response = requests.get(url, data=data, headers=headers).json()
            if 'results' in response.keys():
                response = response.get('results')
        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}'.format(err, url)
            logger.error(message)
        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}'.format(err, url)
            logger.error(message)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)

        return response

    def _do_request_put(self, url, data={}):
        url = '{}{}'.format(self.host, url)
        headers = self._get_authorization()
        response = []
        try:
            response = requests.put(url, data=data, headers=headers).json()
            if 'results' in response.keys():
                response = response.get('results')
        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}'.format(err, url)
            logger.error(message)
        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}'.format(err, url)
            logger.error(message)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)

        return response

    def _do_request_post(self, url, data):
        url = '{}{}'.format(self.host, url)
        headers = self._get_authorization()
        response = []
        try:
            response = requests.post(url, data=data, headers=headers).json()
            if 'results' in response.keys():
                response = response.get('results')
        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}'.format(err, url)
            logger.error(message)
        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}'.format(err, url)
            logger.error(message)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)

        return response
