from django.test import TestCase
from django.conf import settings

from mock import patch

from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from test_utils.mock_mixins import MagicMockMixin

from ..faker_factories import (
    FakeAgreementFactory,
    FakeUserAgreementFactory
)


class MarketplaceAgreementTest(
        SuperUserTestMixin,
        UserTestMixin,
        MagicMockMixin,
        TestCase
):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()

    @patch('marketplace.tasks.RemoveMarketplaceUserPermsTask.apply')
    @patch('marketplace.tasks.AddMarketplaceUserPermsTask.apply')
    def test_marketplace_agreement_user_permissions_after_accept_and_revoke(
            self, task_add_handler, task_remove_handler):
        # PREPARE DATA
        agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
            domain=settings.AGREEMENT_DOMAIN_CH_MARKETPLACE,
            recipient=settings.AGREEMENT_RECIPIENT_GENERAL,
        )
        consultant = FakeConsultantFactory.create(user=self.user)
        user_to = consultant.user
        user_agreement = FakeUserAgreementFactory.create(
            user=user_to,
            agreement=agreement,
            status=settings.AGREEMENT_USER_STATUS_SIGNED,
        )

        # DO ACTION
        user_agreement.revoke(user_to)

        # ASSERTS
        self.assertFalse(user_agreement.user.has_perm(
            settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED))

        # ASSERTS TASKS
        self.assertTrue(task_add_handler.called)
        self.assertTrue(task_remove_handler.called)
        self.assertEqual(
            user_agreement.user.uuid,
            self.get_mock_arg(task_add_handler, 'uuid'),
        )
        self.assertEqual(
            user_agreement.user.uuid,
            self.get_mock_arg(task_remove_handler, 'uuid'),
        )

    @patch('marketplace.tasks.RemoveMarketplaceUserPermsTask.apply')
    @patch('marketplace.tasks.AddMarketplaceUserPermsTask.apply')
    def test_marketplace_agreement_user_permissions_after_delete(
            self, task_add_handler, task_remove_handler):
        # PREPARE DATA
        agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
            domain=settings.AGREEMENT_DOMAIN_CH_MARKETPLACE,
            recipient=settings.AGREEMENT_RECIPIENT_GENERAL,
        )
        consultant = FakeConsultantFactory.create(user=self.user)
        user_to = consultant.user
        user_agreement = FakeUserAgreementFactory.create(
            user=user_to,
            agreement=agreement,
        )
        user_agreement.accept(user_to)

        # DO ACTION
        user_agreement.delete()

        # ASSERTS
        self.assertFalse(user_agreement.user.has_perm(
            settings.EXO_ACCOUNTS_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED))

        # ASSERTS TASKS
        self.assertTrue(task_add_handler.called)
        self.assertTrue(task_remove_handler.called)
        self.assertEqual(
            user_agreement.user.uuid,
            self.get_mock_arg(task_add_handler, 'uuid'),
        )
        self.assertEqual(
            user_agreement.user.uuid,
            self.get_mock_arg(task_remove_handler, 'uuid'),
        )
