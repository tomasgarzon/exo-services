from django.urls import reverse
from django.conf import settings

import requests_mock

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


class UserProjectAPITest(
        UserTestMixin,
        ProjectTestMixin,
        APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_collaborators_without_team(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        for role in self.project.project_roles.exclude(code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=False, is_superuser=False)
            models.UserProjectRole.objects.create(
                project_role=role,
                user=user)

        self.setup_credentials(self.super_user)
        url = reverse('api:project-user-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(
            data.get('count'),
            self.project.project_roles.exclude(code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).count()
        )

    @requests_mock.Mocker()
    def test_collaborator_with_teams(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        coach = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=coach,
            user=user,
            teams=self.project.teams.all())

        self.setup_credentials(self.super_user)
        url = reverse('api:project-user-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        data = response.json()
        user_row = data['results'][0]
        self.assertEqual(
            len(user_row['teams']),
            self.project.teams.count()
        )

    @requests_mock.Mocker()
    def test_participants_without_team(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        models.UserProjectRole.objects.create_participant(
            project=self.project,
            name=faker.name(),
            email=faker.email())

        self.setup_credentials(self.super_user)
        url = reverse('api:project-user-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(
            data.get('count'),
            1
        )

    @requests_mock.Mocker()
    def test_users_without_team(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_NO_TEAM = 2
        for role in self.project.project_roles.exclude(code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=False, is_superuser=False)
            models.UserProjectRole.objects.create(
                project_role=role,
                user=user)
        models.UserProjectRole.objects.create_participant(
            project=self.project,
            name=faker.name(),
            email=faker.email())

        # other coach/participant with team
        models.UserProjectRole.objects.create(
            project_role=self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            user=user,
            team=self.project.teams.first())
        models.UserProjectRole.objects.create_participant(
            project=self.project,
            team=self.project.teams.first(),
            name=faker.name(),
            email=faker.email())

        self.setup_credentials(self.super_user)
        url = reverse('api:project-user-no-team', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(
            len(data),
            TOTAL_NO_TEAM
        )

    @requests_mock.Mocker()
    def test_delete_user(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            user=user,
            team=self.project.teams.first())
        user_participant_role = models.UserProjectRole.objects.create_participant(
            project=self.project,
            team=self.project.teams.first(),
            name=faker.name(),
            email=faker.email())
        user_participant = user_participant_role.user

        self.setup_credentials(self.super_user)
        url = reverse('api:project-user-detail', kwargs={
            'project_pk': self.project.pk,
            'uuid': user.uuid.__str__()})

        # DO ACTION for exo collaborator
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(
            user.user_project_roles.filter(project_role__project=self.project).exists())

        # do action for participant
        url = reverse('api:project-user-detail', kwargs={
            'project_pk': self.project.pk,
            'uuid': user_participant.uuid.__str__()})

        # DO ACTION
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(
            user.user_project_roles.filter(project_role__project=self.project).exists())
        self.assertFalse(
            user.user_team_roles.filter(team__project=self.project).exists())
