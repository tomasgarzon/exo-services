from django.conf import settings
from django.test import TestCase

from mock import patch

from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import UserTestMixin

from .. import signals_define


class EcosystemSignalsTestCase(UserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()

    @patch.object(signals_define.ecosystem_member_created_signal, 'send')
    def test_ecosytem_member_created_signal(self, patch_signal):
        # DO ACTION
        FakeConsultantFactory(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)

        # ASSERTS
        self.assertEqual(patch_signal.call_count, 1)
