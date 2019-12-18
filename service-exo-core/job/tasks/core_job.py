import celery
import logging
import requests

from django.conf import settings

from ..models import CoreJob
from ..helpers import get_data_for_job


JOB_URL_CREATE = 'api/admin/'
JOB_URL_DETAIL = 'api/admin/{}/'

logger = logging.getLogger('service')


class CoreJobMixin:
    host = settings.EXOLEVER_HOST + settings.SERVICE_JOBS_HOST
    headers = {'USERNAME': settings.AUTH_SECRET_KEY}

    def get_url(self, uuid=None):
        if uuid is None:
            url = self.host + JOB_URL_CREATE
        else:
            url = self.host + JOB_URL_DETAIL.format(uuid.__str__())

        return url

    def get_core_job(self, *args, **kwargs):
        try:
            return CoreJob.objects.get(id=kwargs.get('job_id'))
        except CoreJob.DoesNotExist:
            logger.error('CoreJob does not exist')
            raise Exception()


class CoreJobCreate(CoreJobMixin, celery.Task):
    name = 'CoreJobCreate'

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return

        core_job = self.get_core_job(*args, **kwargs)
        url = self.get_url()
        data = get_data_for_job(core_job)

        try:
            response = requests.post(url, json=data, headers=self.headers)
            assert response.status_code == requests.codes.created
            uuid = response.json().get('uuid')
            core_job.uuid = uuid
            core_job.save()
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)


class CoreJobUpdate(CoreJobMixin, celery.Task):
    name = 'CoreJobUpdate'

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return

        core_job = self.get_core_job(*args, **kwargs)
        url = self.get_url(uuid=core_job.uuid.__str__())
        data = get_data_for_job(core_job)

        try:
            response = requests.put(url, json=data, headers=self.headers)
            assert response.status_code == requests.codes.ok
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)


class CoreJobDelete(CoreJobMixin, celery.Task):
    name = 'CoreJobDelete'

    def run(self, *args, **kwargs):
        uuid = kwargs.get('uuid', None)

        if settings.POPULATOR_MODE or uuid is None:
            return

        url = self.get_url(uuid=uuid)

        try:
            response = requests.delete(url, headers=self.headers)
            assert response.status_code == requests.codes.no_content
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)
