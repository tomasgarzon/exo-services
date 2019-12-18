from django.conf import settings
from django.urls import reverse

from datetime import timedelta
import requests_mock
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

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
        request_mock_account.add_mock(
            cls.super_user, is_consultant=False, is_superuser=False)
        cls.project = FakeProjectFactory.create(created_by=cls.super_user)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_data_for_member_email(self, mock_request, mock_email):
        # PREPARE DATA
        self.project.refresh_from_db()
        self.init_mock(mock_request)

        head_coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=head_coach_role,
            created_by=self.super_user,
            user=user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            created_by=self.super_user,
            project_role=coach_role,
            teams=self.project.teams.all(),
            user=user)
        for team in self.project.teams.all():
            user_role = models.UserProjectRole.objects.create_participant(
                created_by=self.super_user,
                project=self.project,
                teams=[team],
                name=faker.name(),
                email=faker.email())
            request_mock_account.add_mock(
                user_role.user, is_consultant=False, is_superuser=False)

        # DO ACTION
        self.project._send_members_email(self.project.created_by)

        # ASSERTS
        self.assertTrue(mock_email.called)
        self.assertEqual(
            mock_email.call_count, 2 + self.project.teams.count())

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_role_changed(self, mock_request, mock_email):
        # PREPARE DATA
        self.project.refresh_from_db()
        self.init_mock(mock_request)
        head_coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            user=user)
        self.project.set_status(
            self.project.created_by, settings.PROJECT_CH_STATUS_WAITING)

        mock_email.reset_mock()

        # DO ACTION
        data = {
            'user': user.uuid.__str__(),
            'project_roles': [head_coach_role.code]}

        url = reverse(
            'api:project-exo-collaborator-list', kwargs={'project_pk': self.project.pk})
        self.setup_credentials(self.super_user)

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_email.called)
        self.assertEqual(
            mock_email.call_count, 1)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_role_removed(self, mock_request, mock_email):
        # PREPARE DATA
        self.project.refresh_from_db()
        self.init_mock(mock_request)
        head_coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=head_coach_role,
            user=user)
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            user=user)
        self.project.set_status(
            self.project.created_by, settings.PROJECT_CH_STATUS_WAITING)

        mock_email.reset_mock()

        url = reverse('api:project-user-detail', kwargs={
            'project_pk': self.project.pk,
            'uuid': user.uuid.__str__()})

        self.setup_credentials(self.super_user)

        # DO ACTION
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_email.called)
        self.assertEqual(
            mock_email.call_count, 1)

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_add_participant_to_team(self, mock_request, mock_email):
        # PREPARE DATA
        self.project.refresh_from_db()
        self.init_mock(mock_request)

        self.project.set_status(
            self.project.created_by, settings.PROJECT_CH_STATUS_WAITING)

        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        email = faker.email()
        models.Participant.objects.create(user=user, email=email)
        data = {
            'name': faker.name(),
            'email': email,
            'teams': self.project.teams.all().values_list('pk', flat=True)}

        url = reverse('api:project-participant-list', kwargs={'project_pk': self.project.pk})

        self.setup_credentials(self.super_user)

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_email.called)
        self.assertEqual(
            mock_email.call_count, self.project.teams.count() * 2)  # one for project and other for team

    @requests_mock.Mocker()
    @patch('utils.mails.handlers.mail_handler.send_mail')
    def test_edit_project(self, mock_request, mock_email):
        # PREPARE DATA
        self.project.refresh_from_db()
        self.init_mock(mock_request)
        coach_role = self.project.project_roles.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)

        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=False, is_superuser=False)
        models.UserProjectRole.objects.create(
            project_role=coach_role,
            user=user)
        self.project.set_status(
            self.project.created_by, settings.PROJECT_CH_STATUS_WAITING)
        mock_email.reset_mock()
        url = reverse('api:project-detail', kwargs={'pk': self.project.pk})

        # DO ACTION
        self.setup_credentials(self.super_user)
        data = {
            'name': faker.word(),
            'customer': faker.company(),
            'location': '{}, {}'.format(faker.city(), faker.country()),
            'place_id': faker.pyint(),
            'start': (self.project.start + timedelta(days=5)).strftime('%Y-%m-%d'),
        }
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_email.called)
        self.assertEqual(
            mock_email.call_count, 2)
