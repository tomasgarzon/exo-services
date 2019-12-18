import json

from django.test import TestCase, Client

from rest_framework import status
from unittest.mock import patch

from utils.faker_factory import faker

from ..faker_factories import FakePaymentFactory
from .mixin_stripe_webhooks import StripeWebhookMixin


class TestWebhookStripe(StripeWebhookMixin, TestCase):

    def test_webhook_notify_payment_error(self):
        client = Client()
        payment = FakePaymentFactory()
        url = '/api/webhooks/'
        request_payload = self.construct_stripe_payload_error(payment)

        # DO ACTION
        response = client.post(
            url,
            data=json.dumps(request_payload),
            content_type='application/json',
        )

        # ASSERTS
        payment.refresh_from_db()

        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(payment.is_error)
        self.assertIsNone(payment.date_payment)
        self.assertIsNone(payment._stripe_payment_id)

    def test_webhook_notify_payment_success(self):
        client = Client()
        payment = FakePaymentFactory()
        url = '/api/webhooks/'
        request_payload = self.construct_stripe_payload_success(payment)

        # DO ACTION
        response = client.post(
            url,
            data=json.dumps(request_payload),
            content_type='application/json',
        )

        # ASSERTS
        payment.refresh_from_db()

        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(payment.is_paid)
        self.assertIsNotNone(payment.date_payment)
        self.assertIsNotNone(payment._stripe_payment_id)

    def test_webhook_notify_payment_success_after_error(self):
        client = Client()
        payment = FakePaymentFactory()
        url = '/api/webhooks/'
        error_request_payload = self.construct_stripe_payload_error(payment)
        success_request_payload = self.construct_stripe_payload_success(payment)
        client.post(
            url,
            data=json.dumps(error_request_payload),
            content_type='application/json',
        )

        # DO ACTION
        response = client.post(
            url,
            data=json.dumps(success_request_payload),
            content_type='application/json',
        )

        # ASSERTS
        payment.refresh_from_db()

        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(payment.is_paid)

    def test_webhook_notify_payment_already_success(self):
        client = Client()
        payment = FakePaymentFactory()
        url = '/api/webhooks/'
        success_request_payload = self.construct_stripe_payload_success(payment)
        client.post(
            url,
            data=json.dumps(success_request_payload),
            content_type='application/json',
        )

        # DO ACTION
        response = client.post(
            url,
            data=json.dumps(success_request_payload),
            content_type='application/json',
        )

        # ASSERTS
        payment.refresh_from_db()

        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(payment.is_paid)

    def test_webhook_notify_payment_does_not_exists(self):
        client = Client()
        payment = FakePaymentFactory()
        payment.delete()
        url = '/api/webhooks/'
        success_request_payload = self.construct_stripe_payload_success(payment)
        client.post(
            url,
            data=json.dumps(success_request_payload),
            content_type='application/json',
        )

        # DO ACTION
        response = client.post(
            url,
            data=json.dumps(success_request_payload),
            content_type='application/json',
        )

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

    @patch('payments.signals_define.signal_payment_received.send')
    def test_send_signal_after_stripe_success_notification(self, stripe_signal_mock):
        client = Client()
        payment = FakePaymentFactory()
        url = '/api/webhooks/'
        request_payload = self.construct_stripe_payload_success(payment)

        # DO ACTION
        client.post(
            url,
            data=json.dumps(request_payload),
            content_type='application/json',
        )

        # ASSERTS
        self.assertTrue(stripe_signal_mock.called)

    @patch('payments.tasks.webhook_notification.SendWebhookTask.s')
    def test_launch_notify_webhook_for_payment_after_stripe_success_notification(self, notification_task_patch):
        client = Client()
        payment = FakePaymentFactory(url_notification=faker.uri())
        url = '/api/webhooks/'
        request_payload = self.construct_stripe_payload_success(payment)

        # DO ACTION
        client.post(
            url,
            data=json.dumps(request_payload),
            content_type='application/json',
        )

        # ASSERTS
        self.assertIsNotNone(payment.url_notification)
        self.assertTrue(notification_task_patch.called)

    @patch('payments.tasks.webhook_notification.SendWebhookTask.s')
    def test_not_launch_notify_webhook_if_not_exist_url_to_notificate(self, notification_task_patch):
        client = Client()
        payment = FakePaymentFactory()
        url = '/api/webhooks/'
        request_payload = self.construct_stripe_payload_success(payment)

        # DO ACTION
        client.post(
            url,
            data=json.dumps(request_payload),
            content_type='application/json',
        )

        # ASSERTS
        self.assertIsNone(payment.url_notification)
        self.assertFalse(notification_task_patch.called)

    @patch('payments.tasks.payment_received_mail.SendPaymentReceivedEmailTask.s')
    def test_send_email_and_invoice_for_payment_after_stripe_success_notification(self, email_task_patch):
        client = Client()
        payment = FakePaymentFactory(
            country='Norway',
            country_code='NO',
            send_invoice=True
        )
        url = '/api/webhooks/'
        request_payload = self.construct_stripe_payload_success(payment)

        # DO ACTION
        client.post(
            url,
            data=json.dumps(request_payload),
            content_type='application/json',
        )

        # ASSERTS
        self.assertTrue(payment.send_invoice)
        self.assertTrue(email_task_patch.called)

    @patch('payments.tasks.payment_received_mail.SendPaymentReceivedEmailTask.s')
    def test_do_not_send_email_and_invoice_for_payment_after_stripe_success_notification(self, email_task_patch):
        client = Client()
        payment = FakePaymentFactory()
        url = '/api/webhooks/'
        request_payload = self.construct_stripe_payload_success(payment)

        # DO ACTION
        client.post(
            url,
            data=json.dumps(request_payload),
            content_type='application/json',
        )

        # ASSERTS
        self.assertFalse(payment.send_invoice)
        self.assertFalse(email_task_patch.called)
