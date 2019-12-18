from exo_auth.faker_factories import FakeUserFactory
from exo_auth.jwt_helpers import _build_jwt


class UserTestMixin:

    def setUp(self):
        super().setUp()
        self.create_super_user()
        self.create_user()

    def create_user(self, password=None):
        password = password or '123456'
        self.user = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            password=password)
        return self.user

    def create_super_user(self, password=None):
        password = password or '123456'
        self.super_user = FakeUserFactory.create(
            is_superuser=True,
            is_active=True,
            password=password)
        return self.super_user

    def get_user(self, password=None):
        password = password or '123456'
        user = FakeUserFactory.create(
            is_superuser=False,
            is_active=True,
            password=password
        )
        return user

    def do_login(self, user):
        token = _build_jwt(user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)

    def reset_credentials(self):
        self.client.credentials()
