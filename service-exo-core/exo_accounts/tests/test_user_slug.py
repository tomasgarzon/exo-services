from django.test import TestCase

from ..test_mixins.faker_factories import FakeUserFactory

from utils.faker_factory import faker


class UserSlugTestCase(TestCase):

    def test_slug_create_user(self):
        # DO ACTION
        user = FakeUserFactory.create()

        # ASSERTS
        self.assertIsNotNone(user.slug)

    def test_slug_modify_user(self):
        # PREPARE DATA
        user = FakeUserFactory.create()
        old_slug = user.slug

        # ASSERTS
        self.assertIsNotNone(old_slug)

        # DO ACTION
        user.full_name = faker.text()
        user.save()
        user.refresh_from_db()

        # ASSERTS
        self.assertEqual(user.slug, old_slug)
