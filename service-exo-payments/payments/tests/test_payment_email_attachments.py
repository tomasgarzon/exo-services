import mock

from django.conf import settings
from django.core.files import File
from django.test import TestCase

from unittest.mock import patch

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin
from utils.tasks import SendMailTask

from ..models import Payment
from .mocked_posts_mixin import mocked_requests


class PaymentEmailAttachmentsTestCase(UserTestMixin, TestCase):

    @patch('utils.mails.handlers.MailHandler.send_mail')
    def test_attached_file_for_payments_is_managed_by_email_signal(self, mail_handler_mock):
        self.create_user()
        file_mock = mock.MagicMock(spec=File, name='FileMock')
        file_mock.name = 'test1.jpg'

        Payment.objects.create(
            created_by=self.user,
            amount=int(faker.numerify()) * 0.01,
            concept=faker.sentence(),
            email=faker.email(),
            full_name=faker.name(),
            attached_file=file_mock,
        )

        # Asserts
        self.assertTrue(mail_handler_mock.called)
        task_called_params = mail_handler_mock.call_args[1]
        self.assertTrue('attachments' in task_called_params.keys())
        self.assertEqual(len(task_called_params.get('attachments')), 2)

    @patch('requests.post', side_effect=mocked_requests)
    def test_attached_file_for_payments_is_managed_by_email_task(self, request_mock):
        self.create_user()
        attachment = (
            'test1.pdf',
            faker.text()
        )

        email_data = {
            'notify_webhook': faker.uri(),
            'concept': faker.sentence(),
            'detail': faker.text(),
            'full_name': faker.name(),
            'amount': faker.numerify(),
            'currency': settings.PAYMENTS_CH_EUR,
            'public_url': faker.uri(),
            'from_email': faker.email(),
            'recipients': [faker.email()],
            'attachments': attachment,
        }

        # DO ACTION
        SendMailTask().s(
            template=faker.word(),
            params=email_data,
        ).apply_async()

        # Asserts
        self.assertTrue(request_mock.called)
        file_attached = request_mock.call_args[1].get('data').fields.get('file')
        self.assertIsNotNone(file_attached)
        self.assertEqual(len(file_attached), 2)

    @patch('utils.mails.handlers.MailHandler.send_mail')
    def test_no_attached_file_for_payments_is_managed_by_email_signal(self, mail_handler_mock):
        self.create_user()
        Payment.objects.create(
            created_by=self.user,
            amount=int(faker.numerify()) * 0.01,
            concept=faker.sentence(),
            email=faker.email(),
            full_name=faker.name(),
        )

        # Asserts
        self.assertTrue(mail_handler_mock.called)
        task_called_params = mail_handler_mock.call_args[1]
        self.assertTrue('attachments' in task_called_params.keys())
        self.assertEqual(len(task_called_params.get('attachments')), 0)

    @patch('requests.post', side_effect=mocked_requests)
    def test_no_attached_file_for_payments_is_managed_by_email_task(self, request_mock):
        self.create_user()
        email_data = {
            'notify_webhook': faker.uri(),
            'concept': faker.sentence(),
            'detail': faker.text(),
            'full_name': faker.name(),
            'amount': faker.numerify(),
            'currency': settings.PAYMENTS_CH_EUR,
            'public_url': faker.uri(),
            'from_email': faker.email(),
            'recipients': [faker.email()],
            'attachments': [],
        }

        # DO ACTION
        SendMailTask().s(
            template=faker.word(),
            params=email_data,
        ).apply_async()

        # Asserts
        self.assertTrue(request_mock.called)
        params_sent = request_mock.call_args[1].get('data').fields
        self.assertTrue('file' not in params_sent.keys())
