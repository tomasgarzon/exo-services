from django.urls import reverse
from django.conf import settings

from mock import patch
from rest_framework import status

from test_utils import DjangoRestFrameworkTestCase

from utils.faker_factory import faker
from test_utils.test_case_mixins import SuperUserTestMixin
from utils.crypto import AESCipher

from .test_mixins import ExOCertificationTestMixin
from ..faker_factories import FakeCertificationRequestFactory
from ..signals_define import certification_request_payment_success


class TestPaymentWebhookAPI(
        ExOCertificationTestMixin,
        SuperUserTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.create_cohorts()

    def prepare_notify_webhook(
            self, status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED):
        cipher = AESCipher(settings.PAYMENT_SECRET_KEY)
        return {
            'token': cipher.encrypt(faker.sentence()),
            'payment_id': faker.numerify(),
            'payment_status': status,
            'payment_method': 'Card',
        }

    def test_payments_service_notify_succesful_payment(self):
        # PREPARE DATA
        certification_request = FakeCertificationRequestFactory(
            certification=self.cohort_lvl_2.certification,
            cohort=self.cohort_lvl_2,
        )
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        url = reverse(
            'api:exo-certification:webhooks-detail',
            kwargs={'pk': certification_request.pk},
        )

        # DO ACTION
        response = self.client.put(url, data=self.prepare_notify_webhook())

        # ASSERTIONS
        certification_request.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            certification_request.status,
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
        )

    def test_payments_service_notify_errored_payment(self):
        # PREPARE DATA
        certification_request = FakeCertificationRequestFactory(
            certification=self.cohort_lvl_2.certification,
            cohort=self.cohort_lvl_2,
        )
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        url = reverse(
            'api:exo-certification:webhooks-detail',
            kwargs={'pk': certification_request.pk},
        )
        payload = self.prepare_notify_webhook(
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_CANCELLED)

        # DO ACTION
        response = self.client.put(url, data=payload)

        # ASSERTIONS
        certification_request.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            certification_request.status,
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_CANCELLED,
        )

    def test_payments_service_notify_non_succesful_payment_do_not_mark_as_paid(self):
        # PREPARE DATA
        certification_request = FakeCertificationRequestFactory(
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
            certification=self.cohort_lvl_2.certification,
            cohort=self.cohort_lvl_2,
        )
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        url = reverse(
            'api:exo-certification:webhooks-detail',
            kwargs={'pk': certification_request.pk},
        )
        payload = self.prepare_notify_webhook(
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING)

        # DO ACTION
        response = self.client.put(url, data=payload)

        # ASSERTIONS
        certification_request.refresh_from_db()
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(
            certification_request.status,
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
        )

    def test_payemnts_service_notify_invalid_payment(self):
        # PREPARE DATA
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        url = reverse(
            'api:exo-certification:webhooks-detail',
            kwargs={'pk': faker.uuid4()}
        )

        # DO ACTION
        response = self.client.put(url, data=self.prepare_notify_webhook())

        # ASSERTIONS
        self.assertTrue(status.is_client_error(response.status_code))

    def test_call_webhook_without_authenticate_return_an_error(self):
        # PREPARE DATA
        certification_request = FakeCertificationRequestFactory(
            certification=self.cohort_lvl_2.certification,
            cohort=self.cohort_lvl_2,
        )
        url = reverse(
            'api:exo-certification:webhooks-detail',
            kwargs={'pk': certification_request.pk}
        )

        # DO ACTION
        response = self.client.post(url, data=self.prepare_notify_webhook())

        # ASSERTIONS
        self.assertTrue(status.HTTP_403_FORBIDDEN, response.status_code)

    @patch.object(certification_request_payment_success, 'send')
    def test_signal_called_after_receive_certification_payment(self, signal_patch):
        # PREPARE DATA
        certification_request = FakeCertificationRequestFactory(
            certification=self.cohort_lvl_2.certification,
            cohort=self.cohort_lvl_2,
        )
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
        url = reverse(
            'api:exo-certification:webhooks-detail',
            kwargs={'pk': certification_request.pk}
        )

        # DO ACTION
        self.client.put(url, data=self.prepare_notify_webhook())

        # ASSERTIONS
        self.assertTrue(signal_patch.called)
