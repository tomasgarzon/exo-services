import uuid

from django.contrib.auth import get_user_model


class UserTestMixin:

    def create_user(self):
        self.user = get_user_model().objects.create(
            uuid=uuid.uuid4(),
            is_active=True,
        )
        self.user.set_password('123456')

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
