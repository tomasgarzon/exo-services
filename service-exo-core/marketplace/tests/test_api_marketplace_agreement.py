from django.urls import reverse
from django.conf import settings

from mock import patch

from rest_framework import status
from rest_framework.test import APITestCase

from agreement.models import Agreement
from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from test_utils.mock_mixins import MagicMockMixin


class MarketplaceAgreementAPITestCase(
        UserTestMixin,
        SuperUserTestMixin,
        MagicMockMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.consultant = FakeConsultantFactory(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        self.client.login(
            username=self.consultant.user.username,
            password='123456')

    def get_current_marketplace_agreement(self):
        return Agreement.objects.filter_by_domain_marketplace() \
            .filter_by_status_active() \
            .latest_version()

    def test_get_marketplace_agreement_api(self):
        # PREPARE DATA
        current_greement = self.get_current_marketplace_agreement()
        url = reverse('api:marketplace:agreement-list')

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

    @patch('marketplace.tasks.AddMarketplaceUserPermsTask.apply')
    def test_accept_marketplace_agreement_api(self, task_add_handler):
        # PREPARE DATA
        current_greement = self.get_current_marketplace_agreement()
        kwargs = {'pk': current_greement.pk}
        url = reverse('api:marketplace:agreement-accept', kwargs=kwargs)

        # DO ACTION
        response = self.client.post(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(self.consultant.user.has_signed_marketplace_agreement())
        self.assertTrue(
            self.consultant.user.agreements.filter_by_agreement(
                current_greement).filter_by_status_accepted().exists())

        # ASSERTS TASKS
        self.assertTrue(task_add_handler.called)
        self.assertEqual(
            self.consultant.user.uuid,
            self.get_mock_arg(task_add_handler, 'uuid'),
        )

    @patch('marketplace.tasks.RemoveMarketplaceUserPermsTask.apply')
    def test_reject_marketplace_agreement_api(self, task_remove_handler):
        # PREPARE DATA
        current_greement = self.get_current_marketplace_agreement()
        kwargs = {'pk': current_greement.pk}
        url = reverse('api:marketplace:agreement-reject', kwargs=kwargs)

        # DO ACTION
        response = self.client.post(url)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(self.consultant.user.has_signed_marketplace_agreement())
        self.assertTrue(
            self.consultant.user.agreements.filter_by_agreement(
                current_greement).filter_by_status_revoked().exists())

        # ASSERTS TASKS
        self.assertTrue(task_remove_handler.called)
        self.assertEqual(
            self.consultant.user.uuid,
            self.get_mock_arg(task_remove_handler, 'uuid'),
        )
