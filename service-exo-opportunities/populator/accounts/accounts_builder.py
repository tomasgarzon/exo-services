import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.shortcuts import get_object_or_404

from populate.populator.builder import Builder


class AccountsBuilder(Builder):

    def create_object(self):
        user = self.create_user(
            uuid4=self.data.get('uuid'),
            is_superuser=self.data.get('is_superuser', False),
            is_staff=self.data.get('is_staff', False),
            is_active=self.data.get('is_active', True))

        market_place = self.data.get('market_place')
        if market_place:
            self.add_marketplace_permission(user=user)

        return user

    def create_user(self, uuid4, is_superuser, is_staff, is_active):
        user = get_user_model().objects.create(
            uuid=uuid.UUID('{}'.format(uuid4)),
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_active=is_active)

        return user

    def add_marketplace_permission(self, user):
        perm = settings.AUTH_USER_PERMS_MARKETPLACE_FULL
        permission = get_object_or_404(
            Permission,
            codename=perm)
        user.user_permissions.add(permission)
