from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.test import TestCase

from utils.faker_factory import faker
from utils.test_mixin import UserTestMixin

from ..models import User


class UserTest(UserTestMixin, TestCase):

    def setUp(self):
        super().setUp()

    def test_create(self):
        user_email = faker.email()
        user_pwd = '123456789'
        user = User.objects.create(
            email=user_email,
            password=user_pwd)
        self.assertIsNotNone(user.email)
        self.assertIsNotNone(user.password)
        self.assertTrue(user.has_usable_password())
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertIsNotNone(authenticate(username=user_email,
                                          password=user_pwd))

    def test_default_create(self):
        # ##
        # By default set a NOT USABLE password
        # ##

        user = User.objects.create(
            email=faker.email())

        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.can_authenticate)

    def test_create_active(self):
        user_email = faker.email()
        user_pwd = '123456789'
        user = User.objects.create(
            email=user_email,
            password=user_pwd,
            is_active=True)
        self.assertIsNotNone(user.email)
        self.assertIsNotNone(user.password)
        self.assertFalse(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertTrue(user.can_authenticate)
        self.assertIsNotNone(authenticate(username=user_email,
                                          password=user_pwd))

    def test_create_superuser(self):
        """
        Users admin should be active users always
        """
        user_email = faker.email()
        user_pwd = '123456789'
        user = User.objects.create_superuser(
            email=user_email,
            password=user_pwd)
        self.assertIsNotNone(user.email)
        self.assertIsNotNone(user.password)
        self.assertTrue(user.is_admin)
        self.assertTrue(user.is_active)
        self.assertIsNotNone(authenticate(username=user_email,
                                          password=user_pwd))

    def test_get_or_create(self):
        name = faker.first_name()
        email = faker.email()
        user, created = User.objects.get_or_create(
            email=email)
        self.assertTrue(created)
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertFalse(user.has_usable_password())
        user2 = User.objects.get_or_create(
            email=faker.email())
        self.assertIsNotNone(user2)
        user3, created = User.objects.get_or_create(
            email=faker.email(),
            defaults={
                'is_active': True,
                'password': name
            })
        self.assertIsNotNone(user3)
        self.assertTrue(created)
        self.assertTrue(user3.has_usable_password())
        self.assertTrue(user3.is_active)
        self.assertTrue(user3.check_password(name))
        user4, created = User.objects.get_or_create(email=email)
        self.assertFalse(created)
        self.assertEqual(user4.id, user.id)

    def test_get_or_create_several_emailaddress(self):
        email = faker.email()
        user, created = User.objects.get_or_create(email=email)
        self.assertTrue(created)
        email2 = faker.email()
        user.add_email_address(email2)
        user2, created = User.objects.get_or_create(
            email=email2)
        self.assertFalse(created)
        self.assertEqual(user2.pk, user.pk)

    def test_default_value_password_updated(self):

        user_email = faker.email()
        user = get_user_model().objects.create(
            email=user_email,
            is_active=True)

        self.assertFalse(user.password_updated)

        # Set a real password
        user.set_password(faker.word())
        self.assertTrue(user.password_updated)

        # Set a random password
        user.set_password(faker.word(), True)
        self.assertFalse(user.password_updated)

        # Set an unusable password
        user.set_unusable_password()
        self.assertFalse(user.password_updated)

        # Set a real password
        user.set_password(faker.word())
        self.assertTrue(user.password_updated)
