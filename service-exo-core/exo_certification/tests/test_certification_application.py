import requests_mock

from unittest.mock import patch

from django.conf import settings
from django.core.management import call_command
from django.urls import reverse

from referral.faker_factories import FakeCampaignFactory
from rest_framework import status
from exo_role.models import CertificationRole

from consultant.faker_factories import FakeConsultantFactory
from exo_accounts.test_mixins import FakeUserFactory
from exo_certification.faker_factories import FakeCertificationRequestFactory
from exo_certification.models import ExOCertification
from relation.models import ConsultantRole
from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker

from .test_mixins import ExOCertificationTestMixin
from ..helpers.payment import get_root_payments_url
from ..models import CertificationRequest, Coupon


def get_payment_mock():
    return {
        'paymentUuid': faker.word(),
        'nextUrl': faker.url(),
    }


class CertificationApplicationAPITestCase(
        ExOCertificationTestMixin,
        DjangoRestFrameworkTestCase):

    def setUp(self):
        call_command('update_core_countries')
        super().setUp()
        self.create_cohorts()

    def generate_application_details_data(self):
        return {
            'reasons': ' '.join(faker.words()),
            'whereMetUs': faker.word(),
        }

    def assertAppDetails(self, data, expected):
        self.assertEqual(data.get('reasons'), expected.get('reasons'))
        self.assertEqual(data.get('where_met_us'), expected.get('whereMetUs'))

    def test_draft_guest_application_consultant(self):
        # PREPARE DATA
        payload = {
            'fullName': faker.name(),
            'email': faker.email(),
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
            'coupon': '',
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), payload.get('fullName'))
        self.assertEqual(data.get('email'), payload.get('email'))
        self.assertEqual(data.get('level'), payload.get('level'))

    def test_draft_guest_application_consultant_with_referrer(self):
        # PREPARE DATA
        referrer = '{}:{}'.format(faker.word(), faker.word())
        payload = {
            'fullName': faker.name(),
            'email': faker.email(),
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
            'referrer': referrer,
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), payload.get('fullName'))
        self.assertEqual(data.get('email'), payload.get('email'))
        self.assertEqual(data.get('level'), payload.get('level'))
        certification_request = CertificationRequest.objects.get(pk=data.get('pk'))
        self.assertEqual(certification_request.referrer, referrer)

    def test_draft_existing_user_as_guest_application_consultant_failure(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        payload = {
            'fullName': consultant.user.full_name,
            'email': consultant.user.email,
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), payload.get('fullName'))
        self.assertEqual(data.get('email'), payload.get('email'))
        self.assertEqual(data.get('level'), payload.get('level'))

    def test_assert_multiple_calls_for_same_user_and_cohort_do_not_duplicate_requests(self):
        consultant = FakeConsultantFactory.create()
        payload = {
            'fullName': consultant.user.full_name,
            'email': consultant.user.email,
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        self.client.post(url, data=payload)
        self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(CertificationRequest.objects.count(), 1)
        self.assertEqual(
            CertificationRequest.objects.first().status,
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_DEFAULT,
        )

    def test_assert_multiple_calls_for_same_user_and_cohort_do_not_duplicate_requests_for_level_3(self):
        consultant = FakeConsultantFactory.create()
        cert_request = CertificationRequest.objects.create(
            user=consultant.user,
            requester_email=consultant.user.email,
            requester_name=consultant.user.full_name,
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3
            ),
        )
        payload = {
            'country': 'NO',
            'recaptcha': faker.word(),
            'billingName': faker.name(),
            'taxId': faker.word(),
            'billingAddress': faker.address(),
            'companyName': faker.name(),
            'cohort': self.cohort_lvl_3.pk,
            'application_details': self.generate_application_details_data(),
        }
        url = reverse('api:exo-certification:applications-detail', kwargs={'pk': cert_request.pk})

        # DO ACTION
        self.client.put(url, data=payload)

        payload = {
            'email': consultant.user.email,
            'password': consultant.user.short_name,
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(CertificationRequest.objects.count(), 1)
        self.assertEqual(
            CertificationRequest.objects.first().status,
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
        )

    def test_draft_guest_application_coach_failure(self):
        # PREPARE DATA
        payload = {
            'fullName': faker.name(),
            'email': faker.email(),
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_draft_guest_application_consultant_ft_with_coupon(self):
        # PREPARE DATA
        coupon = Coupon.objects.create(
            code=faker.word(),
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A
            ),
            max_uses=10,
            discount=500,
        )
        payload = {
            'fullName': faker.name(),
            'email': faker.email(),
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A,
            'coupon': coupon.code,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), payload.get('fullName'))
        self.assertEqual(data.get('email'), payload.get('email'))
        self.assertEqual(data.get('level'), payload.get('level'))

    def test_try_user_application_wrong_password(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        payload = {
            'email': user.email,
            'password': 'aaaa',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_draft_user_application_consultant(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        payload = {
            'email': user.email,
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), user.full_name)
        self.assertEqual(data.get('email'), user.email)
        self.assertEqual(data.get('level'), payload.get('level'))
        self.assertIsNotNone(data.get('contractingData'))

    def test_draft_user_application_consultant_with_referrer(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        referrer = '{}:{}'.format(faker.word(), faker.word())
        payload = {
            'email': user.email,
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
            'referrer': referrer,
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), user.full_name)
        self.assertEqual(data.get('email'), user.email)
        self.assertEqual(data.get('level'), payload.get('level'))
        self.assertIsNotNone(data.get('contractingData'))
        certification_request = CertificationRequest.objects.get(pk=data.get('pk'))
        self.assertEqual(certification_request.referrer, referrer)

    def test_draft_user_as_guest_application_consultant(self):
        # PREPARE DATA
        consultant_1 = FakeConsultantFactory.create()
        FakeCertificationRequestFactory.create(
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
            user=consultant_1.user,
        )
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        payload = {
            'email': user.email,
            'fullName': user.full_name,
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), user.full_name)
        self.assertEqual(data.get('email'), user.email)
        self.assertEqual(data.get('level'), payload.get('level'))

    def test_draft_user_application_consultant_ft_with_coupon(self):
        # PREPARE DATA
        coupon = Coupon.objects.create(
            code=faker.word(),
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A
            ),
            max_uses=10,
            discount=500,
        )
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        payload = {
            'email': user.email,
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A,
            'coupon': coupon.code,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), user.full_name)
        self.assertEqual(data.get('email'), user.email)
        self.assertEqual(data.get('level'), payload.get('level'))
        self.assertIsNotNone(data.get('contractingData'))

    def test_draft_user_application_coach(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()
        certification_role = CertificationRole.objects.get(
            code=settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT)
        ConsultantRole.objects.create(
            certification_role=certification_role,
            consultant=consultant,
        )

        payload = {
            'email': user.email,
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), user.full_name)
        self.assertEqual(data.get('email'), user.email)
        self.assertEqual(data.get('level'), payload.get('level'))
        self.assertIsNotNone(data.get('contractingData'))

    def test_draft_user_application_coach_no_consultant(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()

        payload = {
            'email': user.email,
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('pk'))
        self.assertEqual(data.get('fullName'), user.full_name)
        self.assertEqual(data.get('email'), user.email)
        self.assertEqual(data.get('level'), payload.get('level'))
        self.assertIsNotNone(data.get('contractingData'))

    def test_try_draft_application_coach_non_existing_user(self):
        # PREPARE DATA
        payload = {
            'email': faker.email(),
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    def test_try_draft_application_guest_already_paid(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        CertificationRequest.objects.create(
            user=user,
            requester_email=user.email,
            requester_name=user.full_name,
            certification=self.cohort_lvl_2.certification,
            price=1500,
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
        )
        payload = {
            'email': user.email,
            'fullName': user.full_name,
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_try_draft_application_user_secondary_email_already_paid(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        secondary_email = faker.email()
        user.add_email_address(secondary_email, True)
        user.set_password('123456')
        user.save()

        CertificationRequest.objects.create(
            user=user,
            requester_email=user.email,
            requester_name=user.full_name,
            certification=self.cohort_lvl_2.certification,
            price=1500,
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
        )
        payload = {
            'email': secondary_email,
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_draft_user_apply_coach_already_paid_consultant(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        user.set_password('123456')
        user.save()

        CertificationRequest.objects.create(
            user=user,
            requester_email=user.email,
            requester_name=user.full_name,
            certification=self.cohort_lvl_2.certification,
            price=1500,
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_APPROVED,
        )
        payload = {
            'email': user.email,
            'password': '123456',
            'level': settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-existing-user')

        # DO ACTION
        response = self.client.post(url, data=payload)

        # ASSERTS
        self.assertEqual(status.HTTP_200_OK, response.status_code)

    def test_draft_user_updating_existing_request_coupon(self):
        # PREPARE DATA
        consultant = FakeConsultantFactory.create()
        user = consultant.user
        cert_request = CertificationRequest.objects.create(
            requester_email=user.email,
            requester_name=user.full_name,
            user=user,
            certification=self.cohort_lvl_2.certification,
            cohort=self.cohort_lvl_2,
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
            price=1500,
        )
        coupon = Coupon.objects.create(
            code=faker.word(),
            certification=self.cohort_lvl_2.certification,
            max_uses=10,
            discount=500,
        )
        payload = {
            'coupon': coupon.code,
            'email': user.email,
            'fullName': user.full_name,
            'level': cert_request.certification.level,
            'recaptcha': faker.word(),
        }
        url = reverse('api:exo-certification:applications-list')

        # DO ACTION
        response = self.client.post(url, data=payload)
        cert_request.refresh_from_db()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertEqual(data.get('pk'), cert_request.pk)
        self.assertEqual(cert_request.coupon, coupon)

    @requests_mock.Mocker()
    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_pending_guest_application_consultant(self, mock_request, mock_email):
        # PREPARE DATA
        mock_request.register_uri(
            'POST',
            get_root_payments_url() + settings.EXO_CERTIFICATION_PAYMENTS_API_URL,
            json=get_payment_mock()
        )
        cert_request = CertificationRequest.objects.create(
            requester_email=faker.email(),
            requester_name=faker.name(),
            certification=self.cohort_lvl_2.certification,
        )
        payload = {
            'country': 'NO',
            'recaptcha': faker.word(),
            'billingName': faker.name(),
            'taxId': faker.word(),
            'billingAddress': faker.address(),
            'companyName': faker.name(),
            'cohort': self.cohort_lvl_2.pk,
            'application_details': self.generate_application_details_data(),
        }
        url = reverse('api:exo-certification:applications-detail', kwargs={'pk': cert_request.pk})

        # DO ACTION
        response = self.client.put(url, data=payload)
        cert_request.refresh_from_db()

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('nextUrl'))
        self.assertAppDetails(
            cert_request.application_details,
            payload.get('application_details')
        )

    @requests_mock.Mocker()
    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_pending_guest_application_consultant_ft_with_coupon(self, mock_request, mock_email):
        # PREPARE DATA
        mock_request.register_uri(
            'POST',
            get_root_payments_url() + settings.EXO_CERTIFICATION_PAYMENTS_API_URL,
            json=get_payment_mock()
        )
        coupon = Coupon.objects.create(
            code=faker.word(),
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A
            ),
            max_uses=10,
            discount=500,
        )
        cert_request = CertificationRequest.objects.create(
            requester_email=faker.email(),
            requester_name=faker.name(),
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2A
            ),
            coupon=coupon,
        )
        payload = {
            'country': 'NO',
            'recaptcha': faker.word(),
            'billingName': faker.name(),
            'taxId': faker.word(),
            'billingAddress': faker.address(),
            'companyName': faker.name(),
            'cohort': self.cohort_lvl_2_ft.pk,
            'application_details': self.generate_application_details_data(),
        }
        url = reverse('api:exo-certification:applications-detail', kwargs={'pk': cert_request.pk})

        # DO ACTION
        response = self.client.put(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('nextUrl'))

    @requests_mock.Mocker()
    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_pending_user_application_consultant(self, mock_request, mock_email):
        # PREPARE DATA
        mock_request.register_uri(
            'POST',
            get_root_payments_url() + settings.EXO_CERTIFICATION_PAYMENTS_API_URL,
            json=get_payment_mock()
        )
        consultant = FakeConsultantFactory.create()
        cert_request = CertificationRequest.objects.create(
            requester_email=consultant.user.email,
            requester_name=consultant.user.full_name,
            user=consultant.user,
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2
            ),
        )
        payload = {
            'country': 'NO',
            'recaptcha': faker.word(),
            'billingName': faker.name(),
            'taxId': faker.word(),
            'billingAddress': faker.address(),
            'companyName': faker.name(),
            'cohort': self.cohort_lvl_2.pk,
            'application_details': self.generate_application_details_data(),
        }
        url = reverse('api:exo-certification:applications-detail', kwargs={'pk': cert_request.pk})

        # DO ACTION
        response = self.client.put(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('nextUrl'))

    @requests_mock.Mocker()
    @patch('utils.mail.handlers.mail_handler.send_mail')
    def test_pending_user_non_consultant_application_consultant(self, mock_request, mock_email):
        # PREPARE DATA
        mock_request.register_uri(
            'POST',
            get_root_payments_url() + settings.EXO_CERTIFICATION_PAYMENTS_API_URL,
            json=get_payment_mock()
        )
        user = FakeUserFactory.create()
        cert_request = CertificationRequest.objects.create(
            requester_email=user.email,
            requester_name=user.full_name,
            user=user,
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2
            ),
        )
        payload = {
            'country': 'PT',
            'recaptcha': faker.word(),
            'billingName': faker.name(),
            'taxId': faker.word(),
            'billingAddress': faker.address(),
            'companyName': faker.name(),
            'cohort': self.cohort_lvl_2.pk,
            'application_details': self.generate_application_details_data(),
        }
        url = reverse('api:exo-certification:applications-detail', kwargs={'pk': cert_request.pk})

        # DO ACTION
        response = self.client.put(url, data=payload)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        data = response.json()
        self.assertIsNotNone(data.get('nextUrl'))

    @patch('referral.models.campaign.Campaign.subscribe')
    def test_certification_early_parrot_notification(self, mock_subscribe):
        # PREPARE DATA
        campaign = FakeCampaignFactory.create()
        user = FakeUserFactory.create()
        cert_request = CertificationRequest.objects.create(
            requester_email=user.email,
            requester_name=user.full_name,
            user=user,
            certification=ExOCertification.objects.get(
                level=settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2
            ),
            status=settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
            price=1500,
            referrer='{}:{}'.format(faker.word(), campaign.campaign_id),
        )

        # DO ACTION
        cert_request.notify_referrer(conversion=False)

        # ASSERTS
        self.assertTrue(mock_subscribe.called)
