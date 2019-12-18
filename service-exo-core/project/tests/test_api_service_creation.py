from django.urls import reverse
from django.conf import settings

from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import SuperUserTestMixin
from customer.faker_factories import FakeCustomerFactory
from utils.faker_factory import faker

from ..models import Project


class TestAPIServiceCreation(
    SuperUserTestMixin,
    DjangoRestFrameworkTestCase
):

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def test_type_project(self):
        # PREPARE DATA
        customer = FakeCustomerFactory()
        self.client.login(username=self.super_user.username, password='123456')
        url = reverse('api:project:create-service')
        data = {
            'name': faker.name(),
            'customer': customer.id,
            'type_project': faker.name(),
        }

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue('type_project' in response.data.keys())

    def _send_api_post(self, data):
        # PREPARE DATA
        self.client.login(username=self.super_user.username, password='123456')
        url = reverse('api:project:create-service')

        # DO ACTION
        response = self.client.post(url, data=data, format='json')

        # ASSERTS
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        return response

    def _create_api_service(
            self, type_project=settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED,
            duration=13, lapse=settings.PROJECT_LAPSE_PERIOD):
        customer = FakeCustomerFactory()
        data = {
            'name': faker.name(),
            'customer': customer.id,
            'type_project': type_project,
            'duration': duration,
            'lapse': lapse,
            'partner': '',
        }
        response = self._send_api_post(data)
        return response, data

    def test_create_service_sprint(self):
        # DO ACTION
        response, data = self._create_api_service()

        # ASSERTS
        p = Project.objects.get(pk=response.data['id'])
        self.assertEqual(p.duration, data['duration'])
        self.assertEqual(p.lapse, data['lapse'])
        self.assertEqual(p.steps.count(), data['duration'])

    def test_create_service_fastrack(self):
        # DO ACTION
        response, data = self._create_api_service(
            type_project=settings.PROJECT_CH_TYPE_FASTRACKSPRINT,
            duration=settings.FASTRACK_STEPS_COUNT,
            lapse=settings.PROJECT_LAPSE_PERIOD,
        )

        # ASSERTS
        p = Project.objects.get(pk=response.data['id'])
        self.assertEqual(p.duration, settings.FASTRACK_STEPS_COUNT)
        self.assertEqual(p.lapse, data['lapse'])
        self.assertEqual(p.steps.count(), data['duration'])
        self.assertIsNone(p.partner)
        self.assertEqual(p.template, 'Fastrack')

    def test_zoom_settings_created(self):
        # Workshop
        response, data = self._create_api_service(
            type_project=settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED,
            duration=1,
        )
        project = Project.objects.get(pk=response.data['id'])
        self.assertIsNotNone(project.zoom_settings)

        # Sprint
        sprint_name = faker.name()
        data = {
            'name': sprint_name,
            'customer': project.customer.id,
            'type_project': settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED,
            'duration': 1,
            'lapse': settings.PROJECT_LAPSE_WEEK,
        }

        # DO ACTION
        response = self._send_api_post(data)
        project = Project.objects.get(pk=response.data['id'])

        # ASSERTS
        self.assertIsNotNone(project.zoom_settings)
