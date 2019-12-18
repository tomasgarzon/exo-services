from django.urls import reverse
from django.utils import timezone

import requests_mock
from unittest import mock
from rest_framework import status
from rest_framework.test import APITestCase
from actstream.models import followers

from utils.test_mixin import UserTestMixin
from utils.faker_factory import faker
from utils.mock_mixins import MagicMockMixin

from .. import models
from ..conf import settings

from .test_mixin import OpportunityTestMixin, request_mock_account
from ..signals_define import (
    signal_create_new_conversation,
    opportunity_post_removed,
    opportunity_post_closed,
)


class OpportunityAPITest(
        UserTestMixin,
        OpportunityTestMixin,
        MagicMockMixin,
        APITestCase):

    def setUp(self):
        super().setUp()
        self.create_super_user()
        request_mock_account.reset()
        request_mock_account.add_mock(
            self.super_user, is_consultant=False, is_superuser=True)

    @requests_mock.Mocker()
    def test_send_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        self.setup_credentials(self.super_user)
        opp = self.create_opportunity()
        opp._status = settings.OPPORTUNITIES_CH_DRAFT
        opp.save()
        url = reverse('api:opportunity-send', kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.put(url, data={})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()
        self.assertTrue(opp.is_requested)
        self.assertEqual(opp.requested_by.user, self.super_user)

    @requests_mock.Mocker()
    def test_close_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        self.setup_credentials(self.super_user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)

        url = reverse(
            'api:opportunity-close',
            kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.put(url, data={'comment': faker.text()})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()
        self.assertTrue(opp.is_closed)

    @requests_mock.Mocker()
    def test_re_open_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        self.setup_credentials(self.super_user)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.assign(self.super_user, applicant)
        opp.close(self.super_user)

        url = reverse(
            'api:opportunity-re-open',
            kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.put(
            url,
            data={'deadline_date': timezone.now().strftime('%Y-%m-%d')},
            **{'QUERY_STRING': 'published_by_you=True'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()
        self.assertTrue(opp.is_requested)
        self.assertEqual(opp.deadline_date, timezone.now().date())

    @requests_mock.Mocker()
    def test_close_opportunity_with_user_tagged(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_USERS = 3
        opp = self.create_opportunity(target=settings.OPPORTUNITIES_CH_TARGET_FIXED)
        users = [self.get_user() for _ in range(TOTAL_USERS)]
        for user in users:
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            opp.users_tagged.create(user=user)
            models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())

        url = reverse(
            'api:opportunity-close',
            kwargs={'pk': opp.pk})

        # DO ACTION
        self.setup_credentials(opp.created_by)
        response = self.client.put(
            url, data={'comment': faker.text()},
            **{'QUERY_STRING': 'published_by_you=True'})

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        opp.refresh_from_db()
        self.assertTrue(opp.is_closed)

    @requests_mock.Mocker()
    def test_see_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse(
            'api:opportunity-see',
            kwargs={'pk': opp.pk})

        # DO ACTION
        response = self.client.put(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(opp.has_seen(user))

    @requests_mock.Mocker()
    def test_start_conversation_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        handler = mock.Mock()
        signal_create_new_conversation.connect(
            handler, sender=models.Opportunity)
        mock_request.register_uri(
            'POST',
            '{}{}{}'.format(
                settings.EXOLEVER_HOST,
                settings.SERVICE_CONVERSATIONS_HOST,
                'api/conversations-create-group/'),
            json={'status': ''})
        opp = self.create_opportunity()
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse(
            'api:opportunity-create-conversation',
            kwargs={'pk': opp.pk})

        # DO ACTION
        data = {
            'message': ' '.join(faker.sentences()),
            'files': [
                {
                    'filestack_status': 'Stored',
                    'filename': 'watermark.png',
                    'mimetype': 'image/png',
                    'url': 'https://www.filestackapi.com/api/file/s7tdGfE5RRKFUxwsZoYv'}
            ]}
        response = self.client.post(url, data=data)
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertIsNone(
            self.get_mock_kwarg(handler, 'user_to'))
        self.assertEqual(
            followers(opp), [user])

    @requests_mock.Mocker()
    def test_start_conversation_opportunity_for_applicant(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        handler = mock.Mock()
        signal_create_new_conversation.connect(
            handler, sender=models.Opportunity)
        mock_request.register_uri(
            'POST',
            '{}{}{}'.format(
                settings.EXOLEVER_HOST,
                settings.SERVICE_CONVERSATIONS_HOST,
                'api/conversations-create-group/'),
            json={'status': ''})
        opp = self.create_opportunity()
        user = self.get_user()
        self.add_marketplace_permission(user)
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        applicant = models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        self.setup_credentials(user)
        self.add_marketplace_permission(user)
        url = reverse(
            'api:opportunity-start-conversation-applicant',
            kwargs={'pk': opp.pk, 'applicant_pk': applicant.pk})

        # DO ACTION
        data = {
            'message': ' '.join(faker.sentences()),
            'files': [
                {
                    'filestack_status': 'Stored',
                    'filename': 'watermark.png',
                    'mimetype': 'image/png',
                    'url': 'https://www.filestackapi.com/api/file/s7tdGfE5RRKFUxwsZoYv'}
            ]}
        response = self.client.post(url, data=data)
        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(handler.called)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'user_to'),
            user)

    @requests_mock.Mocker()
    def test_remove_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        self.setup_credentials(self.super_user)
        self.handler = mock.Mock()
        opportunity_post_removed.connect(self.handler)

        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})
        data = {
            'comment': faker.text()
        }
        # DO ACTION
        response = self.client.delete(url, data=data)

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(opp.is_removed)
        self.assertEqual(
            self.get_mock_kwarg(self.handler, 'comment'),
            data['comment'])
        opportunity_post_removed.disconnect(self.handler)

    @requests_mock.Mocker()
    def test_remove_opportunity_tagged(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        TOTAL_USERS = 3
        opp = self.create_opportunity(
            target=settings.OPPORTUNITIES_CH_TARGET_FIXED)
        users = [self.get_user() for _ in range(TOTAL_USERS)]
        for user in users:
            request_mock_account.add_mock(
                user, is_consultant=True, is_superuser=False)
            opp.users_tagged.create(user=user)
            models.Applicant.objects.create_open_applicant(
                user, user, opp, faker.text())
        self.setup_credentials(self.super_user)

        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})
        data = {
            'comment': faker.text()
        }
        # DO ACTION
        response = self.client.delete(
            url, data=data, **{'QUERY_STRING': 'published_by_you=True'})

        # ASSERTS
        opp.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(opp.is_removed)

    @requests_mock.Mocker()
    def test_remove_after_close_opportunity(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        self.setup_credentials(self.super_user)
        opp.close(self.super_user)

        url = reverse(
            'api:opportunity-detail',
            kwargs={'pk': opp.pk})
        data = {
            'comment': faker.text()
        }

        # DO ACTION
        response = self.client.delete(url + '?published_by_you=True', data=data)
        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))

    @requests_mock.Mocker()
    def test_close_opportunity_multiple_times(self, mock_request):
        # PREPARE DATA
        self.init_mock(mock_request)
        opp = self.create_opportunity()
        self.setup_credentials(self.super_user)
        handler = mock.Mock()
        opportunity_post_closed.connect(handler)
        user = self.get_user()
        request_mock_account.add_mock(
            user, is_consultant=True, is_superuser=False)
        models.Applicant.objects.create_open_applicant(
            user, user, opp, faker.text())
        opp.close(self.super_user)
        handler.reset_mock()
        opp.re_open(self.super_user, timezone.now().date())

        # DO ACTION
        opp.close_by_positions_covered()
        # ASSERTS
        self.assertTrue(handler.called)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'user_list'),
            [])

        # DO ACTION
        handler.reset_mock()
        opp.re_open(self.super_user, timezone.now().date())
        opp.close(self.super_user)
        # ASSERTS
        self.assertTrue(handler.called)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'user_list'),
            [])

        # DO ACTION
        handler.reset_mock()
        opp.re_open(self.super_user, timezone.now().date())
        opp.close_by_deadline()
        # ASSERTS
        self.assertTrue(handler.called)
        self.assertEqual(
            self.get_mock_kwarg(handler, 'user_list'),
            [])
