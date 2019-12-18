from django.test import TestCase
from django.conf import settings

from exo_role.models import ExORole

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from consultant.faker_factories import FakeConsultantFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from relation.faker_factories import FakeConsultantProjectRoleFactory
from utils.faker_factory import faker
from team.faker_factories.faker_factory_team import FakeTeamFactory


class TestProjectPermissions(TestCase):

    def setUp(self):
        super().setUp()
        self.sprint = FakeSprintAutomatedFactory.create()

    def test_project_collaborator(self):
        consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        FakeConsultantProjectRoleFactory(
            consultant=consultant,
            project=self.sprint.project_ptr,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_ADVISOR),
        )
        self.assertFalse(consultant.user.has_perm(settings.PROJECT_PERMS_PROJECT_MANAGER, self.sprint.project_ptr))

    def test_manager_sprint(self):
        consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        FakeConsultantProjectRoleFactory(
            consultant=consultant,
            project=self.sprint.project_ptr,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )
        self.assertTrue(consultant.user.has_perm(settings.PROJECT_PERMS_PROJECT_MANAGER, self.sprint.project_ptr))

    def test_delivery_managers_property_after_add_new_member(self):
        #  PREPARE DATA
        super_user = FakeUserFactory(is_superuser=True)
        self.sprint.launch(super_user)
        project = self.sprint.project_ptr

        # DO ACTION
        member = project.add_user_project_delivery_manager(
            super_user,
            faker.name(),
            faker.email(),
        )

        # ASSERTS
        self.assertEqual(project.delivery_managers, [member])
        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_DELIVERY_MANAGER,
            project,
        ))

    def test_delivery_managers_property_before_add_new_member(self):
        #  PREPARE DATA
        super_user = FakeUserFactory(is_superuser=True)
        self.sprint.launch(super_user)
        project = self.sprint.project_ptr

        # DO ACTION
        member = project.add_user_project_delivery_manager(
            super_user,
            faker.name(),
            faker.email(),
        )
        project.remove_permission(
            settings.PROJECT_PERMS_DELIVERY_MANAGER,
            member,
        )

        # ASSERTS
        self.assertEqual(project.delivery_managers, [])

    def test_managers_added_as_participant_removed(self):
        #  PREPARE DATA
        super_user = FakeUserFactory(is_superuser=True)
        self.sprint.launch(super_user)
        project = self.sprint.project_ptr
        consultant = FakeConsultantFactory(
            status=settings.CONSULTANT_STATUS_CH_ACTIVE,
        )

        FakeConsultantProjectRoleFactory(
            consultant=consultant,
            project=project,
            status=settings.RELATION_ROLE_CH_ACTIVE,
            exo_role=ExORole.objects.get(code=settings.EXO_ROLE_CODE_SPRINT_HEAD_COACH),
        )
        new_team = FakeTeamFactory.create(project=project)
        new_team.add_member(
            user_from=super_user,
            email=consultant.user.email,
            name=consultant.user.short_name,
        )

        # DO ACTION
        new_team.remove_member(super_user, consultant.user)

        # ASSERTS
        self.assertTrue(
            consultant.user.has_perm(
                settings.PROJECT_PERMS_VIEW_PROJECT, new_team.project,
            ))
        self.assertTrue(
            consultant.user.has_perm(
                settings.EXO_ACCOUNTS_PERMS_USER_EDIT, consultant.user,
            ))
