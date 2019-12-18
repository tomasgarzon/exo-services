from unittest.mock import patch

from django.urls import reverse
from django.conf import settings

import requests_mock
from rest_framework.test import APITestCase
from rest_framework import status

import uuid

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin
from utils.mock_mixins import MagicMockMixin

from ..models import Page
from .test_mixin import TestMixin, request_mock_account


class PageTestCase(TestMixin, UserTestMixin, MagicMockMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.uuid = uuid.uuid4().__str__()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_create_page(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)

        url = reverse('api:landing:page-list')
        data = {'uuid': self.uuid, 'slug': faker.slug()}

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        page = Page.objects.filter(uuid=self.uuid)
        self.assertEqual(
            page.count(),
            1)
        self.assertTrue(
            page.first().sections.all().exists())
        self.assertIsNotNone(page.first().user)
        self.assertEqual(page.first().user, self.user)
        self.assertEqual(page.first().page_type, settings.LANDING_CH_WORKSHOP)
        self.assertFalse(
            page.first().published)

    @requests_mock.Mocker()
    @patch('landing.process.build')
    def test_update_page(self, mock_request, mock_build):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        url = reverse('api:landing:page-detail', kwargs={'uuid': self.uuid})
        page = Page.objects.create(uuid=self.uuid, slug=faker.slug())

        data = {
            'theme': settings.LANDING_CH_STELLAR,
            'slug': faker.slug(),
            'sections': [
                {'name': faker.word(), 'content': '<p>{}</p>'.format(faker.text())},
                {'name': faker.word(), 'content': '<p>{}</p>'.format(faker.text())},
                {'name': faker.word(), 'content': '<p>{}</p>'.format(faker.text())},
            ]}

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        page.refresh_from_db()
        self.assertEqual(
            page.sections.count(), 3)
        self.assertTrue(mock_build.called)
        self.assertTrue(
            page.published)
        self.assertTrue(response.data.get('published'))

    @requests_mock.Mocker()
    @patch('landing.process.build_preview')
    def test_preview_page(self, mock_request, mock_build):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        url = reverse('api:landing:page-preview', kwargs={'uuid': self.uuid})
        Page.objects.create(uuid=self.uuid, slug=faker.slug())

        data = {
            'theme': settings.LANDING_CH_STELLAR,
            'slug': faker.slug(),
            'sections': [
                {
                    'name': faker.word(),
                    'content': '<p>{}</p>'.format(faker.text()),
                },
                {
                    'name': faker.word(),
                    'content': '<p>{}</p>'.format(faker.text()),
                },
                {
                    'name': faker.word(),
                    'content': '<p>{}</p>'.format(faker.text()),
                },
            ]}

        # DO ACTION
        response = self.client.put(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_build.called)
        self.assertEqual(
            'workshop',
            self.get_mock_kwarg(mock_build, 'page_type'))

    @requests_mock.Mocker()
    def test_validate_ko(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        slug = faker.slug()
        Page.objects.create(uuid=self.uuid, slug=slug)
        url = reverse('api:landing:page-validate')

        # DO ACTION
        data = {'value': slug}
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.content.decode(), 'false')

    @requests_mock.Mocker()
    def test_validate_ok(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        slug = faker.slug()
        Page.objects.create(uuid=self.uuid, slug=slug)
        url = reverse('api:landing:page-validate')

        # DO ACTION
        data = {'value': faker.slug()}
        response = self.client.get(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            response.content.decode(), 'true')

    def test_public_page_retrieve(self):
        # PREPARE DATA
        slug = faker.slug()
        Page.objects.create(uuid=self.uuid, slug=slug)
        url = reverse(
            'api:landing:public-page-detail',
            kwargs={'uuid': self.uuid},
        )

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNotNone(
            response.data['link'])

    @requests_mock.Mocker()
    def test_delete_page(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        slug = faker.slug()
        Page.objects.create(uuid=self.uuid, slug=slug)
        url = reverse(
            'api:landing:page-detail',
            kwargs={'uuid': self.uuid},
        )

        # DO ACTION
        response = self.client.delete(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(
            Page.objects.filter(uuid=self.uuid).exists())

    @requests_mock.Mocker()
    @patch('landing.process.build')
    def test_publish_page(self, mock_request, mock_build):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.user)
        slug = faker.slug()
        page = Page.objects.create(uuid=self.uuid, slug=slug)
        url = reverse(
            'api:landing:page-change-status',
            kwargs={'uuid': self.uuid},
        )
        # DO ACTION
        response = self.client.put(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        page.refresh_from_db()
        self.assertTrue(page.published)
        self.assertTrue(mock_build.called)
