from django import test

from ..faker_factories import FakeAgreementFactory
from ..models import Agreement
from ..conf import settings


class AgreemenQuerysetTest(test.TestCase):

    def setUp(self):
        Agreement.objects.all().delete()

    def test_filter_consultant(self):
        FakeAgreementFactory.create(
            recipient=settings.AGREEMENT_RECIPIENT_GENERAL,
        )
        FakeAgreementFactory.create(
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )

        self.assertEqual(Agreement.objects.for_consultants().count(), 1)

    def test_filter_actives(self):
        FakeAgreementFactory.create(
            status=settings.AGREEMENT_STATUS_INACTIVE,
        )
        FakeAgreementFactory.create(
            status=settings.AGREEMENT_STATUS_ACTIVE,
        )

        self.assertEqual(Agreement.objects.filter_by_status_active().count(), 1)

    def test_last_version(self):
        FakeAgreementFactory.create(
            version='1.0',
        )
        ag1 = FakeAgreementFactory.create(
            version='2.0',
        )

        self.assertEqual(Agreement.objects.all().latest_version(), ag1)
