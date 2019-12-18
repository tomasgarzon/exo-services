from django.test import TestCase

from ..faker_factories import FakeUserFactory


class FakerFactoryTest(TestCase):

    def test_valid_create(self):
        user = FakeUserFactory.create(is_superuser=True)
        self.assertTrue(user.is_admin)
        self.assertIsNotNone(user.email)
