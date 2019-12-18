import requests_mock
import uuid

from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin

from .test_mixin import JobTestMixin, request_mock_account
from ..models import Job
from ..faker_factories import FakeJobFactory


class AdminJobAPITest(
        UserTestMixin,
        JobTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def get_job_data(self, user):
        return {
            'user': user.uuid.__str__(),
            'related_class': 'CO',
            'related_uuid': uuid.uuid4().__str__(),
            'exo_role': settings.EXO_ROLE_CODE_SPRINT_COACH,
            'category': settings.EXO_ROLE_CATEGORY_EXO_SPRINT,
            'start': timezone.now().isoformat(),
            'end': (timezone.now() + timedelta(days=5)).isoformat(),
            'title': faker.text(),
            'url': faker.uri(),
            'status_detail': '',
            'extra_data': {}
        }

    @requests_mock.Mocker()
    def test_create_jobs(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=True)

        url = reverse('api:admin-list')
        self.setup_username_credentials()
        data = self.get_job_data(user)

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(Job.objects.filter(user=user).count(), 1)
        job = Job.objects.get(pk=response.json()['id'])
        self.assertEqual(response.json()['uuid'], job.uuid.__str__())
        self.assertEqual(response.json()['relatedClass'], data.get('related_class'))
        self.assertEqual(response.json()['relatedUuid'], data.get('related_uuid'))

    @requests_mock.Mocker()
    def test_update_jobs(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=True)
        job = self.create_job(user)

        url = reverse('api:admin-detail', kwargs={'uuid': job.uuid.__str__()})
        self.setup_username_credentials()
        data = self.get_job_data(user)

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(Job.objects.filter(user=user).count(), 1)
        job.refresh_from_db()
        self.assertEqual(response.json()['uuid'], job.uuid.__str__())
        self.assertEqual(response.json()['title'], job.title)
        self.assertEqual(data['title'], job.title)

    @requests_mock.Mocker()
    def test_filtering_jobs(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=True)
        opp_uuid = uuid.uuid4()
        FakeJobFactory.create(
            user=user,
            related_uuid=uuid.uuid4(),
            related_class=settings.JOBS_CH_CLASS_CORE_PROJECT)
        job = FakeJobFactory.create(
            user=user,
            related_uuid=opp_uuid,
            related_class=settings.JOBS_CH_CLASS_OPP)
        FakeJobFactory.create(
            user=self.get_user(),
            related_uuid=opp_uuid,
            related_class=settings.JOBS_CH_CLASS_OPP)

        url = reverse('api:admin-list')
        self.setup_username_credentials()

        # DO ACTION
        url += '?related_class=CO&related_uuid={}&user__uuid={}'.format(
            opp_uuid, user.uuid.__str__())
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['uuid'], job.uuid.__str__())
