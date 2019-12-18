from django.urls import reverse
from django.conf import settings

import requests_mock
from unittest.mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from team.models import UserTeamRole

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


class LaunchProjectAPITest(
        UserTestMixin,
        ProjectTestMixin,
        APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    @requests_mock.Mocker()
    @patch('project.models.project.Project._create_participants')
    def test_project_launch(self, mock_request, mock_participants):
        # PREPARE DATA
        self.init_mock(mock_request)

        head_coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=head_coach_role,
            user=user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            teams=self.project.teams.all(),
            user=user)

        for team in self.project.teams.all():
            user_role = models.UserProjectRole.objects.create_participant(
                project=self.project,
                teams=self.project.teams.all(),
                name=faker.name(),
                email=faker.email())
            request_mock_account.add_mock(
                user_role.user, is_consultant=False, is_superuser=False)

        # DO ACTION
        self.project.sync_launch(self.super_user)
        self.project.launch(self.super_user)

        # ASSERTS
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_waiting)
        self.assertFalse(models.UserProjectRole.objects.filter(
            active=False, project_role__project=self.project).exists())
        self.assertFalse(UserTeamRole.objects.filter(
            active=False, team__project=self.project).exists())
        self.assertTrue(mock_participants.called)

    @requests_mock.Mocker()
    @patch('project.models.project.Project.launch')
    def test_api_project_launch(self, mock_request, mock_launch):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        url = reverse('api:project-launch', kwargs={'pk': self.project.pk})
        data = {
            'message': faker.text()
        }
        # DO ACTION
        response = self.client.put(url, json=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_launch.called)
