from django.test import TestCase

from consultant.faker_factories import FakeConsultantFactory

from ..conf import settings
from ..faker_factories import (
    FakeAgreementFactory,
    FakeUserAgreementFactory
)


class TestMixinAgreement(TestCase):

    def setUp(self):
        self.consultant = FakeConsultantFactory()
        self.agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
            domain=settings.AGREEMENT_DOMAIN_CH_TOS,
        )

    def test_agreement_property(self):

        FakeUserAgreementFactory(
            user=self.consultant.user,
            agreement=self.agreement,
            status=settings.AGREEMENT_USER_STATUS_SIGNED,
        )

        self.assertIsNotNone(self.consultant.agreement)
        self.assertTrue(self.consultant.agreement.is_accepted)

    def test_agreements_property(self):

        extra_agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )

        FakeUserAgreementFactory(
            user=self.consultant.user,
            agreement=self.agreement,
            status=settings.AGREEMENT_USER_STATUS_SIGNED,
        )

        FakeUserAgreementFactory(
            user=self.consultant.user,
            agreement=extra_agreement,
            status=settings.AGREEMENT_USER_STATUS_REVOKED,
        )

        self.assertEqual(self.consultant.agreements.count(), 2)
        self.assertEqual(
            self.consultant.agreements.filter_by_status_revoked().count(),
            1,
        )

    def test_last_agreement(self):
        extra_agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )

        self.assertIsNone(self.consultant.last_agreement)

        FakeUserAgreementFactory(
            user=self.consultant.user,
            agreement=self.agreement,
            status=settings.AGREEMENT_USER_STATUS_SIGNED,
        )

        last_agreement = FakeUserAgreementFactory(
            user=self.consultant.user,
            agreement=extra_agreement,
            status=settings.AGREEMENT_USER_STATUS_REVOKED,
        )

        self.assertEqual(
            self.consultant.last_agreement,
            last_agreement,
        )

    def test_agreements_status_properties(self):
        extra_agreement_1 = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
            domain=settings.AGREEMENT_DOMAIN_CH_TOS,
        )

        extra_agreement_2 = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
            domain=settings.AGREEMENT_DOMAIN_CH_TOS,
        )

        extra_agreement_3 = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
            domain=settings.AGREEMENT_DOMAIN_CH_TOS,
        )

        signed_a = FakeUserAgreementFactory(
            user=self.consultant.user,
            agreement=extra_agreement_1,
            status=settings.AGREEMENT_USER_STATUS_SIGNED,
        )

        pending_a = FakeUserAgreementFactory(
            user=self.consultant.user,
            agreement=extra_agreement_2,
            status=settings.AGREEMENT_USER_STATUS_PENDING,
        )

        revoked_a = FakeUserAgreementFactory(
            user=self.consultant.user,
            agreement=extra_agreement_3,
            status=settings.AGREEMENT_USER_STATUS_REVOKED,
        )

        self.assertEqual(self.consultant.active_agreements.count(), 1)
        self.assertEqual(self.consultant.active_agreements[0], signed_a)

        self.assertEqual(self.consultant.revoked_agreements.count(), 1)
        self.assertEqual(self.consultant.revoked_agreements[0], revoked_a)

        self.assertEqual(self.consultant.pending_agreements.count(), 1)
        self.assertEqual(self.consultant.pending_agreements[0], pending_a)
