from django.conf import settings
from django.core.management import call_command
from django.urls import reverse

from consultant.faker_factories import FakeConsultantFactory
from custom_auth.api.serializers.certification_request_helper import CERTIFICATION_REQUIRED
from exo_certification.tests.test_mixins import ExOCertificationTestMixin
from exo_certification.models import CertificationRequest, ExOCertification
from test_utils import DjangoRestFrameworkTestCase
from utils.faker_factory import faker


class TestCertificationRequestHelper(ExOCertificationTestMixin, DjangoRestFrameworkTestCase):

    def setUp(self):
        call_command('update_core_countries')
        super().setUp()
        self.create_cohorts()

    def create_application(self, consultant=None, level=None):
        certification_level = level or settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2
        cert_request = CertificationRequest.objects.create(
            user=consultant.user,
            requester_email=consultant.user.email,
            requester_name=consultant.user.full_name,
            certification=ExOCertification.objects.get(
                level=certification_level
            ),
        )

        if certification_level == settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2:
            cohort = self.cohort_lvl_2.pk
        elif certification_level == settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_3:
            cohort = self.cohort_lvl_3.pk

        payload = {
            'country': 'NO',
            'recaptcha': faker.word(),
            'billingName': faker.name(),
            'taxId': faker.word(),
            'billingAddress': faker.address(),
            'companyName': faker.name(),
            'cohort': cohort,
            'application_details': {
                'reasons': ' '.join(faker.words()),
                'whereMetUs': faker.word(),
            }
        }
        self.client.put(
            reverse('api:exo-certification:applications-detail', kwargs={'pk': cert_request.pk}),
            data=payload,
        )

    def test_user_with_no_certification_request(self):
        consultant = FakeConsultantFactory()
        self.client.login(username=consultant.user.username, password=consultant.user.first_name)

        # DO ACTION
        response = self.client.get(reverse('api:accounts:me'))

        # ASSERTIONS
        certifications = response.json()[0].get('certificationRequests')
        self.assertEqual(certifications, [])
        self.assertEqual(consultant.user.certification_request.count(), 0)

    def test_request_consultant_certification_requires_foundation(self):
        consultant = FakeConsultantFactory()
        self.create_application(consultant=consultant)
        self.client.login(username=consultant.user.username, password=consultant.user.first_name)

        # DO ACTION
        response = self.client.get(reverse('api:accounts:me'))

        # ASSERTIONS
        certifications = response.json()[0].get('certificationRequests')
        self.assertEqual(len(certifications), 2)
        consultant_certification = list(
            filter(
                lambda x: x.get('level') == settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_2,
                certifications,
            )
        )[0]
        exo_foundation_certification = list(
            filter(
                lambda x: x.get('level') == settings.EXO_CERTIFICATION_CERTIFICATION_CH_LEVEL_1,
                certifications,
            )
        )[0]
        self.assertEqual(consultant.user.certification_request.count(), 1)
        self.assertEqual(
            exo_foundation_certification.get('status'),
            CERTIFICATION_REQUIRED,
        )
        self.assertEqual(
            exo_foundation_certification.get('certificationCode'),
            settings.EXO_ROLE_CODE_CERTIFICATION_FOUNDATIONS,
        )
        self.assertEqual(
            consultant_certification.get('status'),
            settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_PENDING,
        )
        self.assertEqual(
            consultant_certification.get('certificationCode'),
            settings.EXO_ROLE_CODE_CERTIFICATION_CONSULTANT,
        )
