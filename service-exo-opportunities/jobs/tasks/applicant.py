import celery
import logging
import requests

from django.conf import settings

from ..models import Job
from ..helper import data_job_for_applicant


JOB_URL_CREATE = 'api/admin/'
JOB_URL_DETAIL = 'api/admin/{}/'

logger = logging.getLogger('celery-task')


class ApplicantJobMixin:
    host = settings.EXOLEVER_HOST + settings.SERVICE_JOBS_HOST
    headers = {'USERNAME': settings.AUTH_SECRET_KEY}

    def get_url(self, uuid=None):
        if uuid is None:
            url = self.host + JOB_URL_CREATE
        else:
            url = self.host + JOB_URL_DETAIL.format(uuid.__str__())

        return url

    def get_job(self, *args, **kwargs):
        try:
            return Job.objects.get(id=kwargs.get('job_id'))
        except Job.DoesNotExist:
            logger.error('Job does not exist')
            raise Exception()


class ApplicantJobCreate(ApplicantJobMixin, celery.Task):
    name = 'ApplicantJobCreate'

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return

        job = self.get_job(*args, **kwargs)
        url = self.get_url()
        data = data_job_for_applicant(job.applicant)

        try:
            response = requests.post(url, json=data, headers=self.headers)
            assert response.status_code == requests.codes.created
            uuid = response.json().get('uuid')
            job.uuid = uuid
            job.save()
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)


class ApplicantJobUpdate(ApplicantJobMixin, celery.Task):
    name = 'ApplicantJobUpdate'

    def run(self, *args, **kwargs):
        if settings.POPULATOR_MODE:
            return

        job = self.get_job(*args, **kwargs)
        url = self.get_url(uuid=job.uuid.__str__())
        data = data_job_for_applicant(job.applicant)

        try:
            response = requests.put(url, json=data, headers=self.headers)
            assert response.status_code == requests.codes.ok
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)


class ApplicantJobDelete(ApplicantJobMixin, celery.Task):
    name = 'ApplicantJobDelete'

    def run(self, *args, **kwargs):
        uuid = kwargs.get('job_uuid', None)

        if settings.POPULATOR_MODE or uuid is None:
            return

        url = self.get_url(uuid=kwargs.get('job_uuid'))

        try:
            response = requests.delete(url, headers=self.headers)
            assert response.status_code == requests.codes.no_content
        except AssertionError:
            message = 'Exception: {}-{}'.format(response.content, url)
            logger.error(message)
            self.retry(countdown=120, max_retries=20)
