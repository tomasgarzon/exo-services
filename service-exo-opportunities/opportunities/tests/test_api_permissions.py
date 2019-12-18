import uuid

from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase

from utils.test_mixin import UserTestMixin

from .test_mixin import OpportunityTestMixin


class UserPermissionsAPITestCase(
        UserTestMixin, OpportunityTestMixin, APITestCase):

    def setUp(self):
        super().setUp()
        self.create_user()
        self.create_super_user()
        self.setup_username_credentials()

    def test_add_marketplace_permission(self):
        # DO ACTION
        self.add_marketplace_permission(self.user)

        # ASSERTS
        self.assertTrue(
            self.user.has_perm(settings.AUTH_USER_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED))

    def test_add_custom_permission_api(self):
        # PREPARE DATA
        kwargs = {'uuid': self.user.uuid}
        url = reverse('api:user-add-permission', kwargs=kwargs)
        permission_code = settings.AUTH_USER_PERMS_MARKETPLACE_FULL
        data = {
            'perm': permission_code
        }

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(self.user.has_perm(settings.AUTH_USER_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED))

    def test_remove_custom_permission_api(self):
        # PREPARE DATA
        self.add_marketplace_permission(self.user)
        kwargs = {'uuid': self.user.uuid}
        url = reverse('api:user-remove-permission', kwargs=kwargs)
        permission_code = settings.AUTH_USER_PERMS_MARKETPLACE_FULL
        data = {
            'perm': permission_code
        }

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        self.assertTrue(status.is_success(response.status_code))
        self.assertFalse(self.user.has_perm(settings.AUTH_USER_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED))

    def test_add_custom_permission_api_no_user_created(self):
        # PREPARE DATA
        user_uuid = uuid.uuid4().__str__()
        kwargs = {'uuid': user_uuid}
        url = reverse('api:user-add-permission', kwargs=kwargs)
        permission_code = settings.AUTH_USER_PERMS_MARKETPLACE_FULL
        data = {
            'perm': permission_code
        }

        # DO ACTION
        response = self.client.post(url, data=data)

        # ASSERTS
        user = get_user_model().objects.get(uuid=user_uuid)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(user.has_perm(settings.AUTH_USER_PERMS_MARKETPLACE_FULL_PERMISSION_REQUIRED))
