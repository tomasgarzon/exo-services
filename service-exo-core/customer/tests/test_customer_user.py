from django.conf import settings
from django.test import TestCase

from guardian.models import UserObjectPermission

from exo_accounts.test_mixins import SuperUserTestMixin, UserTestMixin
from exo_accounts.test_mixins.faker_factories import FakeUserFactory

from ..faker_factories import FakeCustomerFactory


class TestCustomerUser(SuperUserTestMixin,
                       UserTestMixin,
                       TestCase):

    def setUp(self):
        super().setUp()

    def test_delete_customer_and_permissions(self):
        """
        This test will checkout that django Guardian Permissions are deleted
        when a Customer is deleted from the platform
        """

        user_to_clean = FakeUserFactory.create(is_active=True)
        customer = FakeCustomerFactory.create()
        extra_customer = FakeCustomerFactory.create()

        self.assertEqual(UserObjectPermission.objects.filter(user=user_to_clean).count(), 1)  # edit himself profile

        ALL_PERMS = settings.CUSTOMER_ADMIN_PERMISSIONS + settings.CUSTOMER_REGULAR_PERMISSIONS
        for permission_name in ALL_PERMS:
            customer.add_permission(permission_name, user_to_clean)
        self.assertIsNot(UserObjectPermission.objects.filter(user=user_to_clean).count(), 0)

        for permission_name in ALL_PERMS:
            extra_customer.add_permission(permission_name, user_to_clean)

        user_to_clean.clear_perms()
        self.assertEqual(UserObjectPermission.objects.filter(user=user_to_clean).count(), 0)

        # Check all permissions are deleted when user is deleted from the db
        for permission_name in ALL_PERMS:
            customer.add_permission(permission_name, user_to_clean)
        for permission_name in ALL_PERMS:
            extra_customer.add_permission(permission_name, user_to_clean)

        self.assertIsNot(UserObjectPermission.objects.filter(user=user_to_clean).count(), 0)
        user_to_clean_id = user_to_clean.id
        user_to_clean.delete()
        self.assertEqual(UserObjectPermission.objects.filter(user__id=user_to_clean_id).count(), 0)
