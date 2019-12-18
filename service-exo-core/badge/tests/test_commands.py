from django.test import TestCase
from django.core.management import call_command

from consultant.models import Consultant
from consultant.faker_factories import FakeConsultantFactory
from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from relation.faker_factories import FakeConsultantProjectRoleFactory

from ..conf import settings


class UserBadgeCommandsTestCase(SuperUserTestMixin, UserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        self.create_user()
        self.consultant = FakeConsultantFactory.create(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)

    def test_creation_badges_command(self):
        # PREPARE DATA
        FakeConsultantProjectRoleFactory.create_batch(
            consultant=self.consultant,
            size=20)

        # DO ACTION
        call_command('create_user_badges')

        # ASSERTS
        for consultant in Consultant.objects.all():
            self.assertTrue(consultant.user.badge_userbadge_related.all().exists())
