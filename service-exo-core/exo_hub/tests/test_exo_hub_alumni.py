from django.test import TestCase
from django.conf import settings

from exo_role.models import ExORole

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from relation.models import ConsultantProjectRole
from sprint_automated.faker_factories import FakeSprintAutomatedFactory

from ..models import ExOHub
from ..alumni_helpers import (
    clear_exo_hub_alumni,
    add_coaches_and_head_coach_as_alumni)


class ExOHubAlumniTestCase(
        UserTestMixin,
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.hub = ExOHub.objects.get(_type=settings.EXO_HUB_CH_ALUMNI)

    def test_clear_hub(self):
        # PREPARE DATA
        self.hub.users.create(user=self.user)

        # DO ACTION
        clear_exo_hub_alumni()

        # ASSERTS
        self.assertEqual(self.hub.users.count(), 0, 'Should not have users')
        self.assertEqual(self.hub.circle.followers, [], 'Circle should not have users')

    def test_coach_and_head_coach(self):
        # PREPARE DATA
        sprint = FakeSprintAutomatedFactory.create(
            category=settings.PROJECT_CH_CATEGORY_TRANSFORMATION,
            created_by=self.super_user)

        consultant_manager = FakeConsultantFactory.create(
            user__is_active=True,
        )
        consultant_coaches = FakeConsultantFactory.create_batch(
            size=3, user__is_active=True,
        )
        ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=consultant_manager,
            project=sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH)
        )
        for coach in consultant_coaches:
            ConsultantProjectRole.objects.get_or_create_consultant(
                user_from=self.super_user,
                consultant=coach,
                project=sprint.project_ptr,
                exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_COACH)
            )

        self.assertEqual(self.hub.users.count(), 0, 'No users yet')

        # DO ACTION
        add_coaches_and_head_coach_as_alumni()

        # ASSERTS
        self.assertEqual(self.hub.users.count(), 4, 'No coaches/head coach added yet')
