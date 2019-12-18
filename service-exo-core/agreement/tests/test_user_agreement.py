from django.test import TestCase
from django.db.utils import IntegrityError

from datetime import datetime

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin

from ..models import UserAgreement
from ..conf import settings
from ..faker_factories import (
    FakeAgreementFactory,
    FakeUserAgreementFactory
)


class UserAgreementTest(
        SuperUserTestMixin,
        UserTestMixin,
        TestCase
):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()

    def prepare_user_agreement(self):
        previous_agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
        )
        new_agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
        )

        user_agreement_previous = UserAgreement.objects.create(
            agreement=previous_agreement,
            user=self.user,
        )
        user_agreement_previous.accept(self.user)
        previous_agreement.set_status(settings.AGREEMENT_STATUS_INACTIVE)

        return previous_agreement, new_agreement, user_agreement_previous

    def test_user_agreement_cancel(self):
        # PREPARE DATA
        active_agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
        )

        user_agreement = FakeUserAgreementFactory.create(
            agreement=active_agreement,
            status=settings.AGREEMENT_USER_STATUS_PENDING,
        )

        # DO ACTION
        user_agreement.cancel(user_agreement.user)

        # ASSERTS
        self.assertTrue(user_agreement.is_revoked)
        self.assertFalse(user_agreement.is_accepted)
        self.assertFalse(user_agreement.is_pending)
        self.assertIsNone(user_agreement.date_signed)
        self.assertEqual(
            user_agreement.date_revoked.date(),
            datetime.today().date(),
        )

    def test_user_agreement_revoke(self):
        # PREPARE DATA
        active_agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
        )
        user_agreement = FakeUserAgreementFactory.create(
            agreement=active_agreement,
            status=settings.AGREEMENT_USER_STATUS_PENDING,
        )
        # DO ACTION
        user_agreement.revoke(user_agreement.user)

        # ASSERTS
        self.assertTrue(user_agreement.is_revoked)
        self.assertFalse(user_agreement.is_pending)
        self.assertFalse(user_agreement.is_accepted)
        self.assertIsNone(user_agreement.date_signed)
        self.assertEqual(
            user_agreement.date_revoked.date(),
            datetime.today().date(),
        )

    def test_user_agreement_can_be_accepted(self):
        # INPUTS
        status_inputs = [
            settings.AGREEMENT_STATUS_INACTIVE,
            settings.AGREEMENT_STATUS_CANCELLED,
            settings.AGREEMENT_STATUS_ACTIVE,
        ]

        # OUTPUTS
        can_be_accepted_output = [False, False, True]

        for index, status in enumerate(status_inputs):
            # PREPARE DATA
            agreement = FakeAgreementFactory(status=status)
            user = FakeUserFactory()

            # ACTION
            user_agreement = FakeUserAgreementFactory.create(
                agreement=agreement,
                user=user,
            )

            # ASSERTS
            self.assertEqual(
                user_agreement.can_be_accepted(),
                can_be_accepted_output[index],
            )

    def test_unique_user_agreement_instance(self):
        # PREPARE DATA
        agreement = FakeAgreementFactory(status=settings.AGREEMENT_STATUS_ACTIVE)
        UserAgreement.objects.create(
            agreement=agreement,
            user=self.user,
        )

        # DO ACTION
        with self.assertRaises(IntegrityError):
            UserAgreement.objects.create(
                agreement=agreement,
                user=self.user,
            )
            # ASSERTS
            self.assertEqual(
                UserAgreement.objects.filter(user=self.user).count(),
                1,
            )
