from django.contrib.auth.models import Group

from .faker_factories import FakeUserFactory


class UserTestMixin:

    def setUp(self):
        super().setUp()

    def create_user(self, password=None):
        """
        Creates an user and add to the class context
        """
        password = password or '123456'
        self.user = FakeUserFactory.create(is_superuser=False,
                                           is_active=True,
                                           password=password)

    def create_inactive_user(self):
        self.user = FakeUserFactory.create(is_superuser=False)

    def create_new_user(self, password=None, group_name=None):
        """
        Creates a new User for test that need it
        """
        password = password or '123456'
        user = FakeUserFactory.create(is_superuser=False,
                                      is_active=True,
                                      password=password)

        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            group.user_set.add(user)
        return user

    def do_login(self, user, password='123456'):
        self.client.login(
            username=user.username,
            password=password)


class SuperUserTestMixin:

    def setUp(self):
        super().setUp()
        self.create_superuser()

    def create_superuser(self, password=None):
        password = password or '123456'
        self.super_user = FakeUserFactory.create(is_superuser=True,
                                                 is_active=True,
                                                 is_staff=True,
                                                 password=password)
