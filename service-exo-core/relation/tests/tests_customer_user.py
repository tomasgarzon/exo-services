from django.test import TestCase

from customer.faker_factories import FakeCustomerFactory
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..faker_factories import FakeCustomerUserRoleFactory
from ..models import CustomerUserRole
from ..conf import settings


class CustomerUserRoleTest(TestCase):

    def setUp(self):
        super().setUp()
        self.customer = FakeCustomerFactory.create()
        self.user1 = FakeUserFactory.create(is_active=True)
        self.user2 = FakeUserFactory.create(is_active=True)
        self.user3 = FakeUserFactory.create(is_active=True)

        self.role1 = FakeCustomerUserRoleFactory.create(
            customer=self.customer,
            user=self.user1,
        )
        self.role2 = FakeCustomerUserRoleFactory.create(
            customer=self.customer,
            user=self.user2,
        )

    def test_objects_manager(self):
        count = CustomerUserRole.objects.all().count()
        self.assertEqual(count, 2)

    def test_filter_actives(self):
        self.role1.status = settings.RELATION_ROLE_CH_ACTIVE
        self.role1.save()
        self.role2.status = settings.RELATION_ROLE_CH_INACTIVE
        self.role2.save()
        count = CustomerUserRole.objects.actives().count()
        self.assertEqual(count, 1)

    def test_filter_by_user(self):
        self.assertEqual(CustomerUserRole.objects.filter_by_user(user=self.user1).count(), 1)
        self.assertEqual(CustomerUserRole.objects.filter_by_user(user=self.user3).count(), 0)

    def test_queryset_roles(self):
        roles = CustomerUserRole.objects.filter(
            customer=self.customer,
        ).filter_by_user(
            user=self.user1,
        )
        self.assertEqual(len(roles), 1)

    def test_customer_users_manager(self):
        self.assertEqual(self.customer.users_roles.filter_by_user(self.user1).count(), 1)
