from django.test import TestCase
from django.conf import settings

from exo_role.models import ExORole

from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin, UserTestMixin
from utils.faker_factory import faker
from consultant.faker_factories import FakeConsultantFactory

from ..models import ConsultantProjectRole


class UserProjectVisibleTest(
        UserTestMixin,
        SuperUserTestMixin,
        TestCase):

    def setUp(self):
        self.create_user()
        self.create_superuser()
        self.sprint = FakeSprintAutomatedFactory.create(
            created_by=self.user)
        self.sprint_training = FakeSprintAutomatedFactory.create(
            created_by=self.user,
            category=settings.PROJECT_CH_CATEGORY_TRAINING)

    def get_members(self):
        member1 = self.sprint.project_ptr.add_user_project_member(
            self.super_user,
            faker.name(),
            faker.email(),
        )
        member2 = self.sprint_training.project_ptr.add_user_project_member(
            self.super_user,
            faker.name(),
            faker.email(),
        )
        return [
            member1.projects_member.first(),
            member2.projects_member.first()
        ]

    def get_reporters(self):
        relation1, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=self.sprint.project_ptr,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            consultant=FakeConsultantFactory.create(user__is_active=True),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_REPORTER)
        )
        relation2, _ = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            project=self.sprint_training.project_ptr,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            consultant=FakeConsultantFactory.create(user__is_active=True),
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_REPORTER)
        )
        return [relation1, relation2]

    def test_create_by_default(self):
        # DO ACTION
        sprint_member, training_member = self.get_members()
        sprint_reporter, training_reporter = self.get_reporters()

        # ASSERTS
        self.assertTrue(sprint_member.visible)
        self.assertFalse(training_member.visible)
        self.assertTrue(sprint_reporter.visible)
        self.assertFalse(training_reporter.visible)

    def test_update_when_changed(self):
        # PREPARE DATA
        sprint_member, training_member = self.get_members()
        sprint_reporter, training_reporter = self.get_reporters()

        # DO ACTION
        self.sprint.project_ptr.category = settings.PROJECT_CH_CATEGORY_TRAINING
        self.sprint.project_ptr.save(update_fields=['category'])
        self.sprint_training.project_ptr.category = settings.PROJECT_CH_CATEGORY_TRANSFORMATION
        self.sprint_training.project_ptr.save(update_fields=['category'])

        # ASSERTS
        all_members = sprint_member, training_member
        all_members += sprint_reporter, training_reporter
        [member.refresh_from_db() for member in all_members]

        self.assertFalse(sprint_member.visible)
        self.assertTrue(training_member.visible)
        self.assertFalse(sprint_reporter.visible)
        self.assertTrue(training_reporter.visible)
