from django.urls import reverse

from rest_framework import status

from mock import patch

from test_utils import DjangoRestFrameworkTestCase
from test_utils.test_case_mixins import UserTestMixin
from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from utils.faker_factory import faker
from test_utils import TestInboxMixin

from ..conf import settings


class SendFeedbackTest(
        UserTestMixin,
        TestInboxMixin,
        DjangoRestFrameworkTestCase
):

    def setUp(self):
        self.create_user()
        for email in settings.FRONTEND_FEEDBACK_TO:
            FakeUserFactory.create(email=email)

    def test_send_feedback_error(self):
        self.client.login(username=self.user.username, password='123456')
        url = reverse('api:feedback')
        data = {}
        response = self.client.post(url, data=data, format='multipart')
        self.assertTrue(status.is_client_error(response.status_code))

    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_send_feedback_ok(self, mock_handler):
        self.client.login(username=self.user.username, password='123456')
        url = reverse('api:feedback')
        data = {
            'message': faker.paragraph(),
        }
        response = self.client.post(url, data=data, format='multipart')
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(mock_handler.called)

    def test_send_feedback(self):
        self.client.login(username=self.user.username, password='123456')
        url = reverse('api:feedback')
        data = {
            'message': faker.paragraph(),
        }
        response = self.client.post(url, data=data, format='multipart')
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            self.get_inbox_length(), 1)
