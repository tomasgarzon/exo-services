from django.urls import reverse
from django.conf import settings

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account
from ..models import UserProjectRole


class ViewProjectAPITest(
        UserTestMixin,
        ProjectTestMixin,
        APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.create_super_user(cls)
        cls.create_user(cls)
        cls.project = FakeProjectFactory.create(created_by=cls.user)

    def setUp(self):
        super().setUp()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)
        request_mock_account.add_mock(
            self.user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_project_detail(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        url = reverse('api-view:project-detail', kwargs={'pk': self.project.pk})

        # DO ACTON SUPERUSER
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

        # DO ACTION USER
        self.setup_credentials(self.user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_project_list(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        url = reverse('api-view:project-list')

        # DO ACTON SUPERUSER
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()['count'], 1)

        # DO ACTION USER
        self.setup_credentials(self.user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()['count'], 1)

    @requests_mock.Mocker()
    def test_project_users(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        project2 = FakeProjectFactory.create(created_by=self.user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        UserProjectRole.objects.create(
            project_role=self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            user=user,
            teams=[self.project.teams.all().first()])

        UserProjectRole.objects.create(
            project_role=project2.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            user=user,
            teams=[project2.teams.all().last()])

        url = reverse('api-view:project-user-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION USER
        self.setup_credentials(self.user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()['count'], 1)

        # filter by team name

        response = self.client.get(url + '?search=' + project2.teams.all().last().name)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()['count'], 0)

        # filter by rolename
        response = self.client.get(url + '?search=coach')
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()['count'], 1)

        # filter empty
        response = self.client.get(url + '?search=1' + faker.word())
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.json()['count'], 0)

    @requests_mock.Mocker()
    def test_project_step_detail(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)

        # DO ACTION USER
        self.setup_credentials(self.user)
        for step in self.project.steps.all():
            for team in self.project.teams.all():
                url = reverse(
                    'api-view:project-step-detail',
                    kwargs={
                        'project_pk': self.project.pk,
                        'team_pk': team.pk,
                        'pk': step.pk})
                response = self.client.get(url)
                self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_send_feedback(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        team = self.project.teams.first()
        step = self.project.steps.first()
        user_participant = UserProjectRole.objects.create_participant(
            project=self.project,
            teams=[team],
            name=faker.name(),
            email=faker.email()).user
        UserProjectRole.objects.create(
            project_role=self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            user=self.get_user(),
            teams=self.project.teams.all())
        UserProjectRole.objects.create(
            project_role=self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            user=self.get_user(),
            teams=self.project.teams.all())
        self.project._active_roles(self.project.created_by)

        url = reverse(
            'api-view:project-step-feedback',
            kwargs={
                'project_pk': self.project.pk,
                'team_pk': team.id,
                'pk': step.id
            })
        data = {
            'rate': 3,
            'feedback': 2,
            'comments': faker.text()
        }

        # DO ACTION
        self.setup_credentials(user_participant)
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    @requests_mock.Mocker()
    def test_download_report(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        team = self.project.teams.first()
        step = self.project.steps.first()
        user = UserProjectRole.objects.create_participant(
            project=self.project,
            teams=[team],
            name=faker.name(),
            email=faker.email()).user
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=True)
        user_coach = UserProjectRole.objects.create(
            project_role=self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH),
            user=self.get_user(),
            teams=self.project.teams.all()).user
        user_head_coach = UserProjectRole.objects.create(
            project_role=self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
            user=self.get_user(),
            teams=self.project.teams.all()).user
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=True)
        request_mock_account.add_mock(
            user_coach, is_consultant=False, is_superuser=True)
        request_mock_account.add_mock(
            user_head_coach, is_consultant=False, is_superuser=True)
        self.project._active_roles(self.project.created_by)

        url = reverse(
            'api-view:project-step-download-report',
            kwargs={
                'project_pk': self.project.pk,
                'team_pk': team.id,
                'pk': step.id
            })

        # DO ACTION
        self.setup_credentials(self.project.created_by)
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
