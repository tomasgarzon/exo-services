from django.test import TestCase
from django.conf import settings

from exo_role.models import ExORole

from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from relation.faker_factories import FakeConsultantProjectRoleFactory
from consultant.faker_factories import FakeConsultantFactory


class UserBadgeSignalsTestCase(SuperUserTestMixin, UserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        self.create_user()
        self.consultant = FakeConsultantFactory.create(
            user=self.user,
            status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        self.exo_role = ExORole.objects.get(
            code=settings.EXO_ROLE_CODE_SPRINT_COACH)

    def create_consultant_project_roles(self, exo_role, size):
        FakeConsultantProjectRoleFactory.create_batch(
            consultant=self.consultant,
            exo_role=exo_role,
            status=settings.RELATION_ROLE_CH_INACTIVE,
            size=size)

    def test_user_badge_post_save_signal(self):
        # DO ACTION
        self.create_consultant_project_roles(exo_role=self.exo_role, size=2)

        # ASSERTS
        self.assertEqual(self.user.get_badges().count(), 0)

    def test_user_badge_change_status(self):
        # PREPARE DATA

        self.create_consultant_project_roles(exo_role=self.exo_role, size=2)
        for consultant_project_role in self.consultant.roles.all():
            consultant_project_role.activate(self.super_user)

        # ASSERTS
        user_badges = self.user.get_badges(code=self.exo_role.code)
        self.assertTrue(user_badges.exists())
        self.assertEqual(user_badges.first().num, 2)

    def test_user_badge_post_delete_signal(self):
        # PREPARE DATA
        self.create_consultant_project_roles(exo_role=self.exo_role, size=2)
        for consultant_project_role in self.consultant.roles.all():
            consultant_project_role.activate(self.super_user)

        # DO ACTION
        self.consultant.roles.all().delete()

        # ASSERTS
        self.assertFalse(self.user.get_badges(code=self.exo_role.code).exists())

        # ASSERTS LOGS
        self.assertTrue(
            self.user.actor_actions
            .filter(
                verb=settings.BADGE_ACTION_LOG_DELETE,
                description__icontains=settings.BADGE_ACTION_LOG_CREATE_SIGNAL_DESCRIPTION)
            .exists()
        )
