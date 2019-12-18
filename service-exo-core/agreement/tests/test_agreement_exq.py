from django.urls import reverse
from django.conf import settings

from rest_framework import status
from rest_framework.test import APITestCase

from agreement.models import Agreement
from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import UserTestMixin


class ExQAgreementAPITestCase(
    UserTestMixin,
    APITestCase
):

    def setUp(self):
        super().setUp()
        self.create_user()

        self.consultant = FakeConsultantFactory(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        self.client.login(
            username=self.consultant.user.username,
            password='123456')

    def get_current_exq_agreement(self):
        return Agreement.objects.filter_by_domain_exq() \
            .filter_by_status_active() \
            .latest_version()

    def test_get_exq_agreement_api(self):
        # PREPARE DATA
        current_greement = self.get_current_exq_agreement()
        url = reverse('api:agreement:exq-list')

        # DO ACTION
        response = self.client.get(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))

        response_object = response.json()[0]
        self.assertEqual(response_object.get('pk'), current_greement.pk)
        self.assertEqual(response_object.get('name'), current_greement.name)
        self.assertEqual(response_object.get('description'), current_greement.description)
        self.assertEqual(response_object.get('status'), current_greement.status)
        self.assertEqual(response_object.get('pdf'), current_greement.file_url)

    def test_accept_exq_agreement_api(self):
        # PREPARE DATA
        current_greement = self.get_current_exq_agreement()
        kwargs = {'pk': current_greement.pk}
        url = reverse('api:agreement:exq-accept', kwargs=kwargs)

        # DO ACTION
        response = self.client.post(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(self.consultant.user.has_perm(
            settings.EXO_ACCOUNTS_PERMS_EXQ_FULL_PERMISSION_REQUIRED))
        self.assertTrue(
            self.consultant.user.agreements.filter_by_agreement(
                current_greement).filter_by_status_accepted().exists())

    def test_reject_exq_agreement_api(self):
        # PREPARE DATA
        current_greement = self.get_current_exq_agreement()
        kwargs = {'pk': current_greement.pk}
        url = reverse('api:agreement:exq-reject', kwargs=kwargs)

        # DO ACTION
        response = self.client.post(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(self.consultant.user.has_perm(
            settings.EXO_ACCOUNTS_PERMS_EXQ_FULL_PERMISSION_REQUIRED))
        self.assertTrue(
            self.consultant.user.agreements.filter_by_agreement(
                current_greement).filter_by_status_revoked().exists())
