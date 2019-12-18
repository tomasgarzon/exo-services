from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

import requests_mock

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


class ParticipantProjectAPITest(
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
    def test_participants_list(self, mock_request):
        self.init_mock(mock_request)
        url = reverse('api:project-participant-list', kwargs={'project_pk': self.project.pk})
        participant = self.project.project_roles.get(
            code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)

        # without team
        for _ in range(5):
            models.UserProjectRole.objects.create_participant(**{
                'project': self.project,
                'created_by': self.project.created_by,
                'project_role': participant,
                'name': faker.name(),
                'email': faker.email()
            })

        # with team
        user = models.UserProjectRole.objects.create_participant(**{
            'project': self.project,
            'created_by': self.project.created_by,
            'project_role': participant,
            'name': faker.name(),
            'email': faker.email(),
            'team': self.project.teams.first()
        }).user

        # ASSERTS
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], 6)
        self.assertTrue(self.project.teams.first().user_team_roles.filter(user=user).exists())

    @requests_mock.Mocker()
    def test_create_participant(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        data = {
            'name': faker.name(),
            'email': faker.email(),
            'teams': self.project.teams.all().values_list('pk', flat=True)}

        url = reverse('api:project-participant-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.project.members.count(),
            1)
        user = get_user_model().objects.get(participant__email=data['email'])
        self.assertEqual(
            user.user_team_roles.count(),
            self.project.teams.count())
        self.assertTrue(
            self.project.teams.first().user_team_roles.filter(
                user__participant__email=data['email']).exists())

    def test_parse_csv_participant(self):
        # PREPARE DATA
        self.setup_credentials(self.super_user)
        TOTAL_USERS = 5

        data = {
            'filename': 'UrwWTEadSgakdrcHBmhx'
        }

        url = reverse('api:project-participant-parse-upload-user', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.json()),
            TOTAL_USERS)

    @requests_mock.Mocker()
    def test_upload_csv_participant(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        TOTAL_USERS = 5
        users = [
            {'name': faker.name(), 'email': faker.email()} for _ in range(TOTAL_USERS)
        ]
        data = {
            'users': users,
            'teams': list(self.project.teams.all().values_list('id', flat=True))}

        url = reverse('api:project-participant-upload-user', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.project.members.count(),
            TOTAL_USERS)
        for team in self.project.teams.all():
            self.assertEqual(
                team.members.count(),
                TOTAL_USERS)

    @requests_mock.Mocker()
    def test_user_delete(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        participant = self.project.project_roles.get(
            code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)
        user_project_role = models.UserProjectRole.objects.create_participant(**{
            'project': self.project,
            'created_by': self.project.created_by,
            'project_role': participant,
            'name': faker.name(),
            'email': faker.email(),
            'team': self.project.teams.first()
        })

        url = reverse(
            'api:project-participant-detail',
            kwargs={
                'pk': user_project_role.pk,
                'project_pk': self.project.pk})

        # DO ACTION
        self.setup_credentials(self.super_user)
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        with self.assertRaises(models.UserProjectRole.DoesNotExist):
            user_project_role.refresh_from_db()
        self.assertEqual(
            self.project.members.count(), 0)
        self.assertEqual(
            self.project.teams.first().members.count(), 0)

    @requests_mock.Mocker()
    def test_edit_participants_roles(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        email = faker.email()

        initial_teams = self.project.teams.all()[0:2]
        models.UserProjectRole.objects.create_participant(
            name=faker.name(),
            email=email,
            created_by=self.project.created_by,
            project=self.project,
            teams=initial_teams)

        user = get_user_model().objects.get(participant__email=email)

        url = reverse(
            'api:project-user-edit-participant',
            kwargs={'project_pk': self.project.pk, 'uuid': user.uuid.__str__()})

        teams = self.project.teams.all().values_list('id', flat=True)[1:]
        data = {
            'name': user.participant.name,
            'email': faker.email(),
            'teams': teams,
        }

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        participant = user.participant
        participant.refresh_from_db()
        self.assertEqual(participant.email, data['email'])
        self.assertEqual(
            user.user_team_roles.filter(team__project=self.project).count(),
            len(teams))
        self.assertTrue(
            user.user_project_roles.filter(
                project_role__project=self.project,
                project_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).exists())

    @requests_mock.Mocker()
    def test_edit_participants_teams(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        email = faker.email()

        initial_teams = self.project.teams.all()[0:2]
        models.UserProjectRole.objects.create_participant(
            name=faker.name(),
            email=email,
            created_by=self.project.created_by,
            project=self.project,
            teams=initial_teams)

        user = get_user_model().objects.get(participant__email=email)

        url = reverse(
            'api:project-user-edit-participant-teams',
            kwargs={'project_pk': self.project.pk, 'uuid': user.uuid.__str__()})

        teams = self.project.teams.all().values_list('id', flat=True)[1:]
        data = {
            'teams': teams,
        }

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            user.user_team_roles.filter(team__project=self.project).count(),
            len(teams))
        self.assertTrue(
            user.user_project_roles.filter(
                project_role__project=self.project,
                project_role__code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).exists())
