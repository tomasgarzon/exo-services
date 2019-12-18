from django.test import TestCase
from django.conf import settings

from project.faker_factories import FakeProjectFactory
from utils.faker_factory import faker
from test_utils.test_case_mixins import SuperUserTestMixin
from team.faker_factories import FakeTeamFactory
from team.models import Team
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..faker_factories import FakeUserProjectRoleFactory


class UserProjectRoleTest(SuperUserTestMixin, TestCase):

    def setUp(self):
        self.create_superuser()
        super().setUp()

    def test_create(self):
        # PREPARE DATA
        user_project_member = FakeUserProjectRoleFactory.create()

        # ASSERTS
        self.assertIsNotNone(user_project_member)

    def test_create_user_project(self):
        # PREPARE DATA
        user_project_member = FakeUserProjectRoleFactory.create(
            status=settings.RELATION_ROLE_CH_ACTIVE,
            user__is_active=True,
        )
        project = user_project_member.project
        user = user_project_member.user

        # ASSERTS
        self.assertTrue(user.has_perm(settings.PROJECT_PERMS_VIEW_PROJECT, project))

    def test_delete_user_project(self):
        # PREPARE DATA
        user_project_member = FakeUserProjectRoleFactory.create(
            status=settings.RELATION_ROLE_CH_ACTIVE,
            user__is_active=True
        )
        project = user_project_member.project
        user = user_project_member.user
        self.assertTrue(user.has_perm(settings.PROJECT_PERMS_VIEW_PROJECT, project))

        # DO ACTION
        project.users_roles.filter_by_user(user) \
            .filter_by_exo_role_code(settings.EXO_ROLE_CODE_SPRINT_PARTICIPANT).delete()

        # ASSERTS
        self.assertFalse(user.has_perm(settings.PROJECT_PERMS_VIEW_PROJECT, project))

    def test_create_supervisor(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        project_settings = project.settings
        project_settings.launch['fix_password'] = '123456'
        project_settings.save()

        # DO ACTION
        member = project.add_user_project_supervisor(self.super_user, faker.name(), faker.email())

        # ASSERTS
        self.assertTrue(member.check_password('123456'))
        self.assertTrue(member.has_perm(settings.PROJECT_PERMS_VIEW_PROJECT, project))
        self.assertTrue(member.has_perm(settings.PROJECT_PERMS_ONLY_VIEW_PROJECT, project))
        FakeTeamFactory.create_batch(size=3, project=project, user_from=self.super_user)
        teams = Team.objects.filter_by_project(project).filter_by_user(project, member)
        self.assertEqual(teams.count(), 3)

    def test_create_supervisor_no_customer(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(
            status=settings.PROJECT_CH_PROJECT_STATUS_WAITING,
            customer=None)
        project_settings = project.settings
        project_settings.launch['fix_password'] = '123456'
        project_settings.save()

        # DO ACTION
        member = project.add_user_project_supervisor(
            self.super_user, faker.name(), faker.email())

        # ASSERTS
        self.assertIsNotNone(member)

    def test_create_supervisor_previous_launch(self):
        # PREPARE DATA
        project = FakeProjectFactory.create()
        project_settings = project.settings
        project_settings.launch['fix_password'] = '123456'
        project_settings.save()

        # DO ACTION
        member = project.add_user_project_supervisor(self.super_user, faker.name(), faker.email())

        # ASSERTS
        self.assertTrue(member.has_usable_password())
        project.launch(self.super_user)
        member.refresh_from_db()
        self.assertTrue(member.check_password('123456'))

    def test_create_delivery_manager(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        project_settings = project.settings
        project_settings.launch['fix_password'] = '123456'
        project_settings.save()

        # DO ACTION
        member = project.add_user_project_delivery_manager(
            self.super_user,
            faker.name(),
            faker.email(),
        )

        # ASSERTS
        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_VIEW_PROJECT,
            project,
        ))
        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_DELIVERY_MANAGER,
            project,
        ))
        self.assertTrue(member.has_perm(
            settings.PROJECT_PERMS_PROJECT_MANAGER,
            project,
        ))

    def test_create_exo_staff(self):
        # PREPARE DATA
        project = FakeProjectFactory.create(status=settings.PROJECT_CH_PROJECT_STATUS_WAITING)
        project_settings = project.settings
        project_settings.launch['fix_password'] = '123456'
        project_settings.save()
        delivery_manager_user = FakeUserFactory.create(
            is_superuser=True,
            is_active=True,
            is_staff=True,
            password='123456')
        exo_staff_user = FakeUserFactory.create(
            is_superuser=True,
            is_active=True,
            is_staff=True,
            password='123456')

        project.add_user_project_delivery_manager(
            self.super_user,
            delivery_manager_user.short_name,
            delivery_manager_user.email)

        # DO ACTION
        member = project.add_user_project_staff(
            self.super_user,
            exo_staff_user.short_name,
            exo_staff_user.email)

        # ASSERTS
        self.assertTrue(member.has_perm(settings.PROJECT_PERMS_VIEW_PROJECT,
                                        project))
        self.assertTrue(
            member.has_perm(
                settings.PROJECT_PERMS_DELIVERY_MANAGER,
                project))
        delivery_managers = project.delivery_managers
        self.assertEqual(len(delivery_managers), 1)
