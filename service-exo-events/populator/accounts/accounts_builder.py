import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from populate.populator.builder import Builder


class AccountsBuilder(Builder):

    def create_object(self):
        user = self.create_user(
            uuid4=self.data.get('uuid'),
            is_superuser=self.data.get('is_superuser', False),
            is_staff=self.data.get('is_staff', False),
            is_active=self.data.get('is_active', True))

        self.add_permissions(user, self.data.get('permissions', []))

        return user

    def create_user(self, uuid4, is_superuser, is_staff, is_active):
        user = get_user_model().objects.create(
            uuid=uuid.UUID('{}'.format(uuid4)),
            is_superuser=is_superuser,
            is_staff=is_staff,
            is_active=is_active)

        return user

    def add_permissions(self, user, permissions):
        for codename in permissions:
            permission = Permission.objects.get(codename=codename)
            user.user_permissions.add(permission)
