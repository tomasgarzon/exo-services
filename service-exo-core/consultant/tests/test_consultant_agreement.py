from django.test import TestCase
from django.test import tag

from agreement.faker_factories import (
    FakeAgreementFactory,
    FakeUserAgreementFactory
)

from ..conf import settings
from ..faker_factories import FakeConsultantFactory


@tag('sequencial')
class TestConsultantAgreement(TestCase):

    def setUp(self):
        agreement_recipient = settings.AGREEMENT_RECIPIENT_CONSULTANT
        agreement_status_active = settings.AGREEMENT_STATUS_ACTIVE
        self.agreement = FakeAgreementFactory(
            recipient=agreement_recipient,
            status=agreement_status_active,
        )

    def test_agreeement_property(self):

        consultant = FakeConsultantFactory()

        agreement = FakeUserAgreementFactory(
            user=consultant.user,
            agreement=self.agreement,
            status=settings.AGREEMENT_USER_STATUS_SIGNED,
        )

        self.assertIsNotNone(agreement)
        self.assertEqual(agreement, consultant.agreement)
