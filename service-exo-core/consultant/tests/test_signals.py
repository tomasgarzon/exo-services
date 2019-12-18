from django.conf import settings
from django.test import TestCase

from consultant.faker_factories import FakeConsultantFactory
from ecosystem.models import Member
from test_utils.test_case_mixins import UserTestMixin


class ConsultantSignalsTestCase(UserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()

    def test_post_save_consultant(self):
        # DO ACTION
        consultant = FakeConsultantFactory(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)

        # ASSERTS
        self.assertTrue(Member.objects.filter(user=consultant.user).exists())
