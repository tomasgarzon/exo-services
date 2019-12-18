from django.test import TestCase
from django.conf import settings

from test_utils.test_case_mixins import UserTestMixin, SuperUserTestMixin
from consultant.faker_factories import FakeConsultantFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from consultant.signals_define import consultant_post_activated
from exo_role.models import ExORole

from ..models import ExOHub


class ConsultantExOHubAlumniTestCase(
        UserTestMixin,
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_superuser()
        self.hub = ExOHub.objects.get(_type=settings.EXO_HUB_CH_ALUMNI)

    def test_participant_complete_onboarding(self):
        # PREPARE DATA
        sprint = FakeSprintAutomatedFactory.create(
            category=settings.PROJECT_CH_CATEGORY_TRANSFORMATION,
            created_by=self.super_user)

        exo_role = ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT)
        sprint.project_ptr.users_roles.get_or_create(user=self.user, exo_role=exo_role)
        consultant = FakeConsultantFactory.create(user=self.user)

        self.assertEqual(
            self.hub.users.count(), 0, 'No users added yet')

        # DO ACTION
        consultant_post_activated.send(
            sender=consultant.__class__,
            consultant=consultant)

        # ASSERTS
        self.assertEqual(
            self.hub.users.count(), 1, 'No user in project added yet')
