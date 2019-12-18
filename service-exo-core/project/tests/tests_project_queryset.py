from django import test
from django.contrib.auth.models import Permission
from django.conf import settings

from guardian.shortcuts import assign_perm

from exo_accounts.test_mixins.faker_factories import FakeUserFactory
from sprint_automated.faker_factories import FakeSprintAutomatedFactory
from test_utils.test_case_mixins import SuperUserTestMixin
from custom_auth.models import InternalOrganization
from customer.faker_factories import FakeCustomerFactory
from utils.faker_factory import faker

from ..models import Project


class ProjectQuerySetTest(SuperUserTestMixin, test.TestCase):

    def setUp(self):
        self.create_superuser()

    def test_filter_by_type(self):
        # PPEPARE DATA
        FakeSprintAutomatedFactory.create_batch(size=3)

        # ASSERTIONS
        queryset = Project.objects.filter_by_type(settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED).count()
        self.assertEqual(queryset, 3)

    def test_filter_by_user(self):
        user1 = FakeUserFactory.create(is_active=True)
        projects = FakeSprintAutomatedFactory.create_batch(size=3)
        queryset = Project.objects.filter_by_type(
            settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED,
        ).filter_by_user(
            user1,
        ).count()
        self.assertEqual(queryset, 0)
        queryset = Project.objects.filter_by_type(
            settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED,
        ).filter_by_user(
            self.super_user,
        ).count()
        self.assertEqual(queryset, 3)
        assign_perm(settings.PROJECT_PERMS_VIEW_PROJECT, user1, projects[0].project_ptr)
        queryset = Project.objects.filter_by_type(
            settings.PROJECT_CH_TYPE_SPRINT_AUTOMATED,
        ).filter_by_user(
            user1,
        ).count()
        self.assertEqual(queryset, 1)

    def test_filter_by_user_or_organization(self):
        # PREPARE DATA
        name = settings.BRAND_NAME
        users = FakeUserFactory.create_batch(size=2, is_active=True)
        customer = FakeCustomerFactory.create()
        organization = InternalOrganization.objects.get(name=name)
        for user in users:
            user.user_permissions.add(
                Permission.objects.get(codename=settings.PROJECT_PERMS_ADD_PROJECT))
            user.user_permissions.add(
                Permission.objects.get(codename=settings.SPRINT_AUTOMATED_ADD_SPRINT))
            organization.users_roles.get_or_create(user=user)

        FakeSprintAutomatedFactory.create_batch(
            size=3, created_by=users[0], internal_organization=organization)

        customer.create_sprint_automated(
            user_from=users[1],
            name=faker.name(),
            description=faker.text(),
            duration=settings.SPRINT_AUTOMATED_STEPS_COUNT,
        )
        # DO ACTION and ASSERTS
        for user in users:
            projects = Project.objects.filter_by_user_or_organization(user).count()
            self.assertEqual(projects, 4)

        self.assertEqual(
            Project.objects.filter_by_user_or_organization(
                FakeUserFactory.create(is_active=True)).count(),
            0)
