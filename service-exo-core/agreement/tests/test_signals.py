from django.test import TestCase

from test_utils.test_case_mixins import UserTestMixin

from ..conf import settings
from ..faker_factories import (
    FakeAgreementFactory,
    FakeUserAgreementFactory
)


class AgreementSignalsTest(UserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()

    def test_agreement_post_save(self):
        # PREPARE DATA
        num_user_agreements = 15
        agreement = FakeAgreementFactory.create(
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
            status=settings.AGREEMENT_STATUS_ACTIVE,
            domain=settings.AGREEMENT_DOMAIN_CH_ACTIVITY)
        FakeUserAgreementFactory.create_batch(
            size=num_user_agreements,
            agreement=agreement,
            status=settings.AGREEMENT_USER_STATUS_SIGNED)

        # PRE-ASSERTS
        self.assertTrue(agreement.user_agreements.filter_by_status_accepted().exists())

        # DO ACTION
        agreement.set_status(settings.AGREEMENT_STATUS_INACTIVE)

        # ASSERTS
        self.assertFalse(agreement.user_agreements.filter_by_status_accepted().exists())
        self.assertEqual(
            agreement.user_agreements.filter_by_status_revoked().count(),
            num_user_agreements)
