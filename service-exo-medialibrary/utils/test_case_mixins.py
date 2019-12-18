import uuid

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.conf import settings

from auth_uuid.jwt_helpers import _build_jwt


class UserTestMixin:

    def create_user(self, group_name=None):
        self.user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
        )
        self.user.set_password('123456')
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            group.user_set.add(self.user)

    def create_super_user(self):
        self.super_user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
            is_superuser=True,
            is_staff=True
        )
        self.super_user.set_password('123456')

    def get_user(self):
        user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
        )
        user.set_password('123456')
        return user

    def do_login(self, user):
        token = _build_jwt(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def do_token_login(self):
        self.client.credentials(HTTP_USERNAME=settings.AUTH_SECRET_KEY)
