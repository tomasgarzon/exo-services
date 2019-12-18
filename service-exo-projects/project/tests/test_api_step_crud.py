from django.utils import timezone
from django.urls import reverse

import requests_mock
from datetime import timedelta

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker

from .. import models
from ..faker_factories import FakeProjectFactory
from .test_mixin import ProjectTestMixin, request_mock_account


TOTAL_STEP_FOR_SPRINT = 13


class StepProjectAPITest(
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

    def get_data(self):
        return {
            'name': faker.word(),
            'index': faker.pyint(),
            'start': timezone.now().strftime('%Y-%m-%d'),
            'end': (timedelta(days=2) + timezone.now()).strftime('%Y-%m-%d'),
        }

    @requests_mock.Mocker()
    def test_step_list(self, mock_request):
        url = reverse('api:project-step-list', kwargs={'project_pk': self.project.pk})

        # ASSERTS
        self.setup_credentials(self.super_user)
        response = self.client.get(url)
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            len(response.json()), TOTAL_STEP_FOR_SPRINT)

    @requests_mock.Mocker()
    def test_create_step(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)

        data = self.get_data()
        url = reverse('api:project-step-list', kwargs={'project_pk': self.project.pk})

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.project.steps.count(),
            TOTAL_STEP_FOR_SPRINT + 1)

    @requests_mock.Mocker()
    def test_step_edit(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        step = self.project.steps.first()
        url = reverse(
            'api:project-step-detail',
            kwargs={
                'pk': step.pk,
                'project_pk': self.project.pk})

        # DO ACTION
        self.setup_credentials(self.super_user)
        data = self.get_data()
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        step.refresh_from_db()
        self.assertEqual(step.name, data['name'])
        self.assertEqual(self.project.steps.count(), TOTAL_STEP_FOR_SPRINT)

    @requests_mock.Mocker()
    def test_step_delete(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        step = self.project.steps.first()
        url = reverse(
            'api:project-step-detail',
            kwargs={
                'pk': step.pk,
                'project_pk': self.project.pk})

        # DO ACTION
        self.setup_credentials(self.super_user)
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        with self.assertRaises(models.Step.DoesNotExist):
            step.refresh_from_db()
        self.assertEqual(
            self.project.steps.count(), TOTAL_STEP_FOR_SPRINT - 1)
