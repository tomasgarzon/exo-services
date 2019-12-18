import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from unittest.mock import patch


from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin
from utils.tasks import SendMailTask

from ..models import Payment
from .mocked_posts_mixin import mocked_requests


class PaymentEmailNotificationWebhookTestCase(UserTestMixin, TestCase):

    @patch('utils.mails.handlers.MailHandler.send_mail')
    def test_notification_webhook_url_is_processed_by_send_mail_signal(self, mail_handler_mock):
        self.create_user()

        # DO ACTION
        payment = Payment.objects.create(
            created_by=self.user,
            amount=int(faker.numerify()) * 0.01,
            concept=faker.sentence(),
            email=faker.email(),
            full_name=faker.name(),
        )

        # Asserts
        self.assertTrue(mail_handler_mock.called)
        called_params = mail_handler_mock.call_args[1]
        self.assertTrue('notify_webhook' in called_params.keys())
        self.assertEqual(
            called_params.get('notify_webhook'),
            '{}{}'.format(
                settings.DOMAIN_NAME,
                reverse(
                    'api:email-notify',
                    kwargs={'hash': payment._hash_code}
                )
            )
        )

    @patch('requests.post', side_effect=mocked_requests)
    def test_notification_webhook_url_is_managed_by_send_mail_task(self, request_mock):
        payment_hash_code = faker.ean()
        notification_url = '{}{}'.format(
            settings.DOMAIN_NAME,
            reverse(
                'api:email-notify',
                kwargs={'hash': payment_hash_code}
            )
        )
        email_data = {
            'notify_webhook': notification_url,
            'concept': faker.sentence(),
            'detail': faker.text(),
            'full_name': faker.name(),
            'amount': faker.numerify(),
            'currency': settings.PAYMENTS_CH_EUR,
            'public_url': faker.uri(),
            'from_email': faker.email(),
            'recipients': [faker.email()],
        }

        # DO ACTION
        SendMailTask().s(
            template=faker.word(),
            params=email_data,
        ).apply_async()

        # Asserts
        self.assertTrue(request_mock.called)
        called_url = request_mock.call_args[0][0]
        called_params = json.loads(request_mock.call_args[1].get('data').fields.get('params'))
        self.assertTrue(settings.EMAIL_POST_URL in called_url)
        self.assertTrue('notify_webhook' in called_params.keys())
        self.assertEqual(
            called_params.get('notify_webhook'),
            '{}{}'.format(
                settings.DOMAIN_NAME,
                reverse(
                    'api:email-notify',
                    kwargs={'hash': payment_hash_code}
                )
            )
        )
