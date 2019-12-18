from django.test import TestCase, override_settings

from ..models import Agreement
from ..conf import settings
from ..faker_factories import FakeAgreementFactory


class TestAgreement(TestCase):

    def get_tos_agreements(self):
        return Agreement.objects.filter_by_domain_terms_of_service().filter_by_status_active()

    @override_settings(AGREEMENT_AUTO_ACCEPT_AGREEMENTS=False)
    def test_agreement_update_active_status(self):
        """
        Check that Agreements with the same Related objects (objects_to_activate)
        are disabled when a new version for this Agreement is created
        """
        agreement_v1 = FakeAgreementFactory(
            version='1.0',
            status=settings.AGREEMENT_STATUS_ACTIVE,
            domain=settings.AGREEMENT_DOMAIN_CH_TOS,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )

        agreement_v2 = FakeAgreementFactory(
            version='2.0',
            status=settings.AGREEMENT_STATUS_INACTIVE,
            domain=settings.AGREEMENT_DOMAIN_CH_TOS,
            recipient=settings.AGREEMENT_RECIPIENT_CONSULTANT,
        )

        # ASSERTS
        tos_agreements = self.get_tos_agreements()
        self.assertEqual(tos_agreements.count(), 2)
        self.assertEqual(tos_agreements[1], agreement_v1)

        # DO ACTION
        agreement_v2.activate()

        # ASSERTS
        tos_agreements = self.get_tos_agreements()
        self.assertEqual(tos_agreements.count(), 1)
        self.assertEqual(tos_agreements[0], agreement_v2)
