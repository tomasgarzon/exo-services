import uuid

from django.urls import reverse
from django.conf import settings

import requests_mock

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


class ExOCollaboratorProjectAPITest(
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
        admin = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        basic = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user_head_coach = self.get_user()
        request_mock_account.add_mock(
            user_head_coach, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=admin,
            user=user_head_coach)
        user_coach = self.get_user()
        request_mock_account.add_mock(
            user_coach, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=basic,
            user=user_coach)

    @requests_mock.Mocker()
    def test_users_list(self, mock_request):
        self.init_mock(mock_request)
        url = reverse('api:project-exo-collaborator-list', kwargs={'project_pk': self.project.pk})

        # ASSERTS
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.json()['count'], 2)

    @requests_mock.Mocker()
    def test_create_user(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        class User:
            uuid = None
        user = User()
        user.uuid = uuid.uuid4()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)

        data = {
            'user': user.uuid.__str__(),
            'project_roles': [self.project.project_roles.first().code]}

        url = reverse('api:project-exo-collaborator-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.project.members.count(),
            3)

    @requests_mock.Mocker()
    def test_user_delete(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        user_project_role = models.UserProjectRole.objects.filter_by_project(
            self.project).filter(project_role__code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH).first()
        url = reverse(
            'api:project-exo-collaborator-detail',
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
            self.project.members.count(), 1)

    @requests_mock.Mocker()
    def test_create_user_with_team(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)

        data = {
            'user': user.uuid.__str__(),
            'project_roles': [role.code for role in self.project.project_roles.all()],
            'teams': self.project.teams.all().values_list('pk', flat=True)}

        url = reverse('api:project-exo-collaborator-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.project.members.count(),
            3)
        self.assertTrue(
            self.project.teams.first().user_team_roles.filter(
                user=user,
                team_role__code=settings.EXO_ROLE_CODE_SPRINT_COACH).exists())
        self.assertEqual(
            user.user_project_roles.count(),
            len(data['project_roles']))
        self.assertEqual(
            user.user_team_roles.count(),
            self.project.teams.count())
        self.assertEqual(
            user.user_team_roles.count(),
            len(data['teams']))

    @requests_mock.Mocker()
    def test_edit_exo_collaborator_roles(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)

        initial_roles = [
            settings.EXO_ROLE_CODE_AWAKE_SPEAKER,
            settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
            settings.EXO_ROLE_CODE_SPRINT_OBSERVER]
        initial_teams = self.project.teams.all()[0:2]

        for code in initial_roles:
            project_role = self.project.project_roles.get(code=code)
            models.UserProjectRole.objects.create(
                user=user,
                created_by=self.project.created_by,
                project_role=project_role)
        project_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
        models.UserProjectRole.objects.create(
            user=user,
            created_by=self.project.created_by,
            project_role=project_role,
            teams=initial_teams)

        url = reverse(
            'api:project-user-edit-exo-collaborator',
            kwargs={'project_pk': self.project.pk, 'uuid': user.uuid.__str__()})

        new_roles = models.ProjectRole.objects.filter(
            code__in=[
                settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT,
                settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH,
                settings.EXO_ROLE_CODE_SPRINT_OBSERVER,
                settings.EXO_ROLE_CODE_ACCOUNT_MANAGER,
                settings.EXO_ROLE_CODE_SPRINT_COACH])
        teams = self.project.teams.all().values_list('id', flat=True)[1:]
        data = {
            'project_roles': new_roles.values_list('exo_role__code', flat=True),
            'teams': teams,
        }

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()

        self.assertEqual(
            user.user_team_roles.filter(team__project=self.project).count(),
            len(teams))
        self.assertEqual(
            user.user_project_roles.filter(project_role__project=self.project).count(),
            new_roles.count())

    def test_user_duplicated_role(self):
        # PREPARE DATA
        admin = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        user_head_coach = self.get_user()
        models.UserProjectRole.objects.create(
            project_role=admin,
            user=user_head_coach)

        # DO ACTION
        models.UserProjectRole.objects.create(
            project_role=admin,
            user=user_head_coach)
