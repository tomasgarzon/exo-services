import datetime
from unittest.mock import patch

import requests_mock
from django.conf import settings
from django.core.management import call_command
from django.urls import reverse
from django.utils import timezone

from rest_framework import status

from consultant.faker_factories import FakeConsultantFactory
from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker
from utils.dates import decrease_date

from .test_mixins import ExOCertificationTestMixin
from ..helpers.payment import get_root_payments_url
from ..faker_factories import FakeCouponFactory


def get_payment_mock():
    return {
        'paymentUuid': faker.word(),
        'nextUrl': faker.url(),
    }


class CertificationApplicationCouponAPITestCase(
        ExOCertificationTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        call_command('update_core_countries')
        super().setUp()
        self.create_cohorts()

    def generate_data(self):
        return {
            'fullName': faker.name(),
            'email': faker.email(),
            'level': settings.EXO_CERTIFICATION_LEVEL_CH_2,
            'recaptcha': faker.word(),
            'coupon': '',
        }

    @requests_mock.Mocker()
    @patch(
        'utils.drf.mixins.recaptcha_serializer.RecaptchaSerializerMixin.validate_recaptcha',
        return_value=faker.word(),
    )
    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_pending_guest_application_consultant(self, mock_request, mock_recaptcha, mock_email):
        # PREPARE DATA
        mock_request.register_uri(
            'POST',
            get_root_payments_url() + settings.EXO_CERTIFICATION_PAYMENTS_API_URL,
            json=get_payment_mock()
        )
        url = reverse('api:exo-certification:applications-list')
        payload = self.generate_data()
        coupon = FakeCouponFactory.create(
            expiry_date=decrease_date(days=2, date=timezone.now().today()),
            certification=self.cohort_lvl_2.certification,
        )
        payload['coupon'] = coupon.code

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_client_error(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('coupon'))

    def test_guest_draft_application_expired_coupon(self):
        # PREPARE DATA
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        coupon = FakeCouponFactory.create(
            expiry_date=yesterday,
            certification=self.cohort_lvl_2.certification,
        )
        payload = {
            'coupon': coupon.code,
            'fullName': faker.name(),
            'email': faker.email(),
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_user_draft_application_expired_coupon(self):
        # PREPARE DATA
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        coupon = FakeCouponFactory.create(
            expiry_date=yesterday,
            certification=self.cohort_lvl_2.certification,
        )

        payload = {
            'coupon': coupon.code,
            'fullName': faker.name(),
            'email': faker.email(),
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_guest_draft_application_with_coupon_valid_another_level(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(certification=self.cohort_lvl_3.certification)
        payload = {
            'coupon': coupon.code,
            'fullName': faker.name(),
            'email': faker.email(),
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_user_draft_application_with_coupon_valid_another_level(self):
        # PREPARE DATA
        coupon = FakeCouponFactory.create(certification=self.cohort_lvl_3.certification)
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        payload = {
            'coupon': coupon.code,
            'email': user.email,
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
