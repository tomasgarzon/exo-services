from django.conf import settings
from django.test import TestCase

from mock import patch

from ..faker_factories import FakeCertificationRequestFactory
from .. import signals_define


class CertificationSignalsTestCase(TestCase):

    @patch.object(signals_define.certification_request_status_updated, 'send')
    def test_signal_status_update_on_new_request(self, patch_signal):
        # DO ACTION
        FakeCertificationRequestFactory.create()

        # ASSERTS
        self.assertEqual(patch_signal.call_count, 1)

    @patch.object(signals_define.certification_request_status_updated, 'send')
    def test_signal_status_update_on_existing_request(self, patch_signal):
        # PREPARE DATA
        certification = FakeCertificationRequestFactory.create()

        # DO ACTION
        certification.status = settings.EXO_CERTIFICATION_REQUEST_STATUS_CH_FINISHED
        certification.save()

        # ASSERTS
        self.assertEqual(patch_signal.call_count, 2)
