from django.urls import reverse

import requests_mock
from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from project.tests.test_mixin import ProjectTestMixin, request_mock_account
from project.faker_factories import FakeProjectFactory

from .. import models

TOTAL_TEAM = 4


class TeamProjectAPITest(
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
    def test_team_list(self, mock_request):
        url = reverse('api:project-team-list', kwargs={'project_pk': self.project.pk})

        # ASSERTS
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(self.project.teams.count(), TOTAL_TEAM)
        self.assertEqual(
            response.json()['count'], self.project.teams.count())
        self.assertEqual(
            len(response.json()['results']), self.project.teams.count())

    @requests_mock.Mocker()
    def test_create_team(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        data = {
            'name': faker.word(),
            'stream': self.project.streams.first().pk,
        }

        url = reverse('api:project-team-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.project.teams.count(),
            TOTAL_TEAM + 1)

    @requests_mock.Mocker()
    def test_team_edit(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        team = self.project.teams.first()
        url = reverse(
            'api:project-team-detail',
            kwargs={
                'pk': team.pk,
                'project_pk': self.project.pk})

        # DO ACTION
        self.setup_credentials(self.super_user)
        data = {
            'name': faker.word(),
            'stream': self.project.streams.exclude(pk=team.stream.pk).first().pk,
        }
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        team.refresh_from_db()
        self.assertEqual(team.name, data['name'])
        self.assertEqual(self.project.teams.count(), TOTAL_TEAM)

    @requests_mock.Mocker()
    def test_team_delete(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        team = self.project.teams.first()
        url = reverse(
            'api:project-team-detail',
            kwargs={
                'pk': team.pk,
                'project_pk': self.project.pk})

        # DO ACTION
        self.setup_credentials(self.super_user)
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        with self.assertRaises(models.Team.DoesNotExist):
            team.refresh_from_db()
        self.assertEqual(
            self.project.teams.count(), TOTAL_TEAM - 1)
