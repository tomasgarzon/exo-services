from django.utils import timezone
from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..faker_factories import FakeProjectFactory
from .. import models
from .test_mixin import ProjectTestMixin, request_mock_account


class ProjectAPITest(
        UserTestMixin,
        ProjectTestMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    def get_data(self):
        return {
            'name': faker.word(),
            'customer': faker.company(),
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'place_id': faker.pyint(),
            'start': timezone.now().date().strftime('%Y-%m-%d'),
        }

    @requests_mock.Mocker()
    def test_create_project(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user,
            is_consultant=False,
            is_superuser=False,
        )

        self.setup_credentials(user)

        data = self.get_data()
        url = reverse('api:project-list')

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        project = models.Project.objects.get(pk=response.json()['pk'])
        self.assertTrue(project.steps.exists())
        self.assertTrue(models.Project.objects.filter(created_by=user).exists())
        for step in project.steps.all():
            self.assertIsNotNone(step.start)
            self.assertIsNotNone(step.end)

    @requests_mock.Mocker()
    def test_project_list(self, mock_request):
        # PREPARE DATA
        NUM_PROJECTS = 5
        PAGE_SIZE = 2
        self.init_mock(mock_request)
        users = [self.get_user() for _ in range(NUM_PROJECTS)]
        for user in users:
            request_mock_account.add_mock(
                user,
                is_consultant=False,
                is_superuser=False,
            )
            FakeProjectFactory.create(created_by=user)

        url = reverse('api:project-list')

        # ASSERTS
        for user in users:
            self.setup_credentials(user)
            response = self.client.get(url)
            self.assertTrue(status.is_success(response.status_code))
            self.assertEqual(
                len(response.json()['results']), 1)

        self.setup_credentials(self.super_user)
        response = self.client.get(url, data={'page_size': PAGE_SIZE})
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], NUM_PROJECTS)
        self.assertEqual(
            len(response.json()['results']), PAGE_SIZE)

    @requests_mock.Mocker()
    def test_project_edit(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user,
            is_consultant=False,
            is_superuser=False,
        )
        project = FakeProjectFactory.create(created_by=user)

        url = reverse('api:project-detail', kwargs={'pk': project.pk})

        # DO ACTION
        self.setup_credentials(user)
        data = self.get_data()
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        project.refresh_from_db()
        self.assertEqual(project.name, data['name'])
        self.assertEqual(project.created_by, user)

    @requests_mock.Mocker()
    def test_project_delete(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user,
            is_consultant=False,
            is_superuser=False,
        )
        project = FakeProjectFactory.create(created_by=user)

        url = reverse('api:project-detail', kwargs={'pk': project.pk})

        # DO ACTION
        self.setup_credentials(user)
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

        response = self.client.get(url)
        self.assertEqual(
            response.status_code,
            status.HTTP_410_GONE)

        url = reverse('api:project-list')
        response = self.client.get(url)
        self.assertEqual(
            len(response.json()['results']),
            0)

    @requests_mock.Mocker()
    def test_project_settings_edit(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user,
            is_consultant=False,
            is_superuser=False,
        )
        project = FakeProjectFactory.create(created_by=user)

        url = reverse('api:project-settings', kwargs={'pk': project.pk})

        # DO ACTION
        self.setup_credentials(user)

        data = {
            'ticketsModuleEnabled': True,
            'swarmSessionsModuleEnabled': True,
            'teamCommunicationsModuleEnabled': True,
            'askEcosystemEnabled': True,
            'directoryEnabled': True,
            'quizesEnabled': True,
            'feedbackEnabled': True,
        }
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        project.settings.refresh_from_db()
        self.assertTrue(project.settings.team_communication)
