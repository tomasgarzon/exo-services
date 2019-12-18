from django.test import TestCase

from datetime import datetime

from ..conf import settings
from ..faker_factories import FakeAgreementFactory
from ..models import Agreement


class FakeAgreementTest(TestCase):

    def setUp(self):
        Agreement.objects.all().delete()

    def test_agreement_activated(self):
        agreement = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_ACTIVE,
        )

        self.assertEqual(
            agreement.status,
            settings.AGREEMENT_STATUS_ACTIVE,
        )

    def test_agreement_recipient(self):
        agreement = FakeAgreementFactory(recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT)

        self.assertEqual(
            agreement.recipient,
            settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )

    def test_agreement_activation(self):
        agreement_1 = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_INACTIVE,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )
        self.assertTrue(agreement_1.is_inactive)

        agreement_2 = FakeAgreementFactory(
            status=settings.AGREEMENT_STATUS_INACTIVE,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )
        self.assertTrue(agreement_2.is_inactive)

        self.assertEqual(
            Agreement.objects.filter(recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT).count(),
            2,
        )

        # ##
        # Check activation and deactivation for agreements
        # ##

        agreement_1.activate()

        agreement_1.refresh_from_db()
        agreement_2.refresh_from_db()

        self.assertTrue(agreement_1.is_active)
        self.assertTrue(agreement_2.is_inactive)

        agreement_2.activate()
        agreement_1.refresh_from_db()
        agreement_2.refresh_from_db()

        self.assertTrue(agreement_2.is_active)
        self.assertTrue(agreement_1.is_cancelled)

        # ##
        # Check dates
        # ##

        self.assertEqual(
            agreement_1.date_cancelled.date(),
            datetime.today().date(),
        )
        self.assertEqual(
            agreement_2.date_activation.date(),
            datetime.today().date(),
        )
