import requests
import logging

from celery import Task

logger = logging.getLogger('library')


class AssignResourcesToProjectTask(Task):
    name = 'AssignResourcesToProjectTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        url = kwargs.get('url')
        data = kwargs.get('data')
        headers = kwargs.get('headers')

        try:
            requests.post(url, data=data, headers=headers)
        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}'.format(err, url)
            logger.error(message)
        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}'.format(err, url)
            logger.error(message)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)


class AssignProjectToResourceTask(Task):
    name = 'AssignProjectToResourceTask'
    ignore_result = True

    def run(self, *args, **kwargs):
        url = kwargs.get('url')
        data = kwargs.get('data')
        headers = kwargs.get('headers')

        try:
            requests.put(url, data=data, headers=headers)
        except requests.Timeout as err:
            message = 'requests.Timeout: {}-{}'.format(err, url)
            logger.error(message)
        except requests.RequestException as err:
            message = 'requests.RequestException: {}-{}'.format(err, url)
            logger.error(message)
        except Exception as err:
            message = 'requests.Exception: {}'.format(err)
            logger.error(message)
