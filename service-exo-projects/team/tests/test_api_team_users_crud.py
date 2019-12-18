from django.urls import reverse
from django.conf import settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from project.tests.test_mixin import ProjectTestMixin, request_mock_account
from project.faker_factories import FakeProjectFactory
from project.models import UserProjectRole


TOTAL_PARTICIPANTS = 5
TOTAL_COACH = 1
TOTAL_USERS = TOTAL_PARTICIPANTS + TOTAL_COACH


class TeamUsersAPITest(
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

    def initialize_team_users(self):
        team = self.project.teams.first()

        users = [{'name': faker.name(), 'email': faker.email()} for _ in range(TOTAL_PARTICIPANTS)]
        for user in users:
            user_data = {
                'name': user['name'],
                'email': user['email'],
                'team': team,
                'project': self.project
            }
            UserProjectRole.objects.create_participant(**user_data)
        for _ in range(TOTAL_COACH):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=False, is_superuser=False)
            user_data = {
                'user': user,
                'project_role': self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
                'team': team,
            }
            UserProjectRole.objects.create(**user_data)
        return team

    @requests_mock.Mocker()
    def test_users_in_team(self, mock_request):
        # PREPARE DATA
        team = self.initialize_team_users()

        url = reverse(
            'api:project-team-detail',
            kwargs={'project_pk': self.project.pk, 'pk': team.pk})
        self.setup_credentials(self.super_user)

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(len(data['users']), TOTAL_USERS)

    @requests_mock.Mocker()
    def test_add_participant(self, mock_request):
        # PREPARE DATA
        team = self.initialize_team_users()
        user_data = {
            'name': faker.name(),
            'email': faker.email(),
            'project': self.project
        }
        user_project_role = UserProjectRole.objects.create_participant(
            **user_data)
        data = {
            'user': user_project_role.user.uuid.__str__(),
            'team_role': settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT
        }
        url = reverse(
            'api:project-team-add-user',
            kwargs={'project_pk': self.project.pk, 'pk': team.pk})
        self.setup_credentials(self.super_user)

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(team.participants.count(), TOTAL_PARTICIPANTS + 1)
        self.assertEqual(team.members.count(), TOTAL_USERS + 1)

    @requests_mock.Mocker()
    def test_add_coach(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        team = self.initialize_team_users()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        user_data = {
            'user': user,
            'project_role': self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        }
        UserProjectRole.objects.create(**user_data)
        data = {
            'user': user.uuid.__str__(),
            'team_role': settings.EXO_ROLE_CODE_SPRINT_COACH
        }
        url = reverse(
            'api:project-team-add-user',
            kwargs={'project_pk': self.project.pk, 'pk': team.pk})
        self.setup_credentials(self.super_user)

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(team.members.count(), TOTAL_USERS + 1)
        self.assertEqual(team.participants.count(), TOTAL_PARTICIPANTS)
        self.assertEqual(team.coaches.count(), TOTAL_COACH + 1)
        self.assertEqual(
            team.user_team_roles.filter(team_role__code=settings.EXO_ROLE_CODE_SPRINT_COACH).count(), 2)
        self.assertEqual(
            team.user_team_roles.filter(
                team_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT
            ).count(), TOTAL_PARTICIPANTS)

    @requests_mock.Mocker()
    def test_delete_user_in_team(self, mock_request):
        # PREPARE DATA
        team = self.initialize_team_users()
        user_team_role = team.user_team_roles.filter(team_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).first()
        url = reverse(
            'api:project-team-detail-user',
            kwargs={
                'project_pk': self.project.pk,
                'pk': team.pk,
                'user_team_role_pk': user_team_role.pk})

        self.setup_credentials(self.super_user)

        # DO ACTION
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(team.members.count(), TOTAL_USERS - 1)

    @requests_mock.Mocker()
    def test_mover_user_to_other_team(self, mock_request):
        # PREPARE DATA
        team = self.initialize_team_users()
        team2 = self.project.teams.exclude(pk=team.pk).first()
        user_team_role = team.user_team_roles.filter(team_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).first()
        url = reverse(
            'api:project-team-move-user',
            kwargs={
                'project_pk': self.project.pk,
                'pk': team.pk,
                'user_team_role_pk': user_team_role.pk})

        self.setup_credentials(self.super_user)
        data = {
            'new_team': team2.pk
        }

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(team.members.count(), TOTAL_USERS - 1)
        self.assertEqual(team2.members.count(), 1)
        self.assertEqual(len(response.json()), 2)

    @requests_mock.Mocker()
    def test_assign_users_to_team(self, mock_request):
        # PREPARE DATA
        users = [{'name': faker.name(), 'email': faker.email()} for _ in range(TOTAL_PARTICIPANTS)]
        for user in users:
            user_data = {
                'name': user['name'],
                'email': user['email'],
                'project': self.project
            }
            UserProjectRole.objects.create_participant(**user_data)
        for _ in range(TOTAL_COACH):
            user = self.get_user()
            request_mock_account.add_mock(
                user, is_consultant=False, is_superuser=False)
            user_data = {
                'user': user,
                'project_role': self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            }
            UserProjectRole.objects.create(**user_data)
        team = self.project.teams.first()

        url = reverse(
            'api:project-team-assign-users',
            kwargs={
                'project_pk': self.project.pk,
                'pk': team.pk})

        self.setup_credentials(self.super_user)
        data = {
            'project_roles': UserProjectRole.objects.filter(
                project_role__project=self.project).values_list('project_role__exo_role__code', flat=True)
        }

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(team.members.count(), TOTAL_USERS)
