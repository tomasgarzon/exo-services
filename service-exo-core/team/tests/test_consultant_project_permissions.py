from django.test import TestCase

from exo_role.models import ExORole

from test_utils.test_case_mixins import SuperUserTestMixin
from relation.models import ConsultantProjectRole
from consultant.faker_factories import FakeConsultantFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory

from ..conf import settings


class TestConsultantPermission(SuperUserTestMixin, TestCase):
    """
    Test Consultants permissions related with Services
    (Sprint)
    """

    def setUp(self):
        super().setUp()
        self.create_superuser()
        self.consultant = FakeConsultantFactory(status=settings.CONSULTANT_STATUS_CH_ACTIVE)
        self.sprint = FakeSprintAutomatedFactory(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)

    def test_delete_consultant_role_for_project_sprint(self):
        """
        For SPRINT
        Test consultant_project_role_post_delete to check Consultant permissions
            - Create a Consultant
            - Create Trainer role for this Consultant (IS NOT MANAGER)
            - create HeadCoach for this Consultant (IS MANAGER)
            - Delete the Trainer role
            - Consultant should NOT have permissions for the Sprint as Manager
        """
        trainer_role, created = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=self.consultant,
            project=self.sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ALIGN_TRAINER),
        )

        self.assertTrue(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_CONSULTANT,
            self.sprint.project_ptr,
        ))
        self.assertFalse(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            self.sprint.project_ptr,
        ))

        manager_role, created = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=self.consultant,
            project=self.sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )

        self.assertTrue(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_CONSULTANT,
            self.sprint.project_ptr,
        ))
        self.assertTrue(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            self.sprint.project_ptr,
        ))

        manager_role.delete()

        self.assertTrue(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_CONSULTANT,
            self.sprint.project_ptr,
        ))
        self.assertFalse(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            self.sprint.project_ptr,
        ))

        trainer_role.delete()

        self.assertFalse(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_CONSULTANT,
            self.sprint.project_ptr,
        ))
        self.assertFalse(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            self.sprint.project_ptr,
        ))

    def test_delete_manager_perm_for_consultant_role(self):
        """
        Test method remove_head_coach_project to check delete manager role for
        a consultant
        """
        manager_role, created = ConsultantProjectRole.objects.get_or_create_consultant(
            user_from=self.super_user,
            consultant=self.consultant,
            project=self.sprint.project_ptr,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )

        self.assertTrue(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_CONSULTANT,
            self.sprint.project_ptr,
        ))
        self.assertTrue(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            self.sprint.project_ptr,
        ))

        manager_role.delete()

        self.assertFalse(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_CONSULTANT,
            self.sprint.project_ptr,
        ))
        self.assertFalse(self.consultant.user.has_perm(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            self.sprint.project_ptr,
        ))
