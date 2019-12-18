from django.conf import settings
from django.test import TestCase

from ..test_mixins import UserTestMixin


class UserSectionsTest(UserTestMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.create_user()

    def test_sections_visited(self):
        inputs = settings.EXO_ACCOUNTS_SECTIONS_VISITED_AVAILABLE

        # PRE-ASSERTS
        self.assertEqual(self.user.get_sections_visited(), [])
        for section in inputs:
            self.assertFalse(self.user.has_seen_section(section))

        # DO ACTION
        for section in inputs:
            self.user.see_section(section)

            # ASSERTS
            self.assertTrue(self.user.has_seen_section(section))
            self.assertIn(section, self.user.get_sections_visited())
