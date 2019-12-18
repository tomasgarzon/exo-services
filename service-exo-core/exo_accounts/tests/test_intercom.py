from django.conf import settings
from django.test import TestCase

from ..test_mixins import UserTestMixin


class TestIntercomUser(UserTestMixin,
                       TestCase):

    def test_intercom_hash_for_user(self):
        # PREPARE DATA
        settings.INTERCOM_SECRET_KEY = '1234'

        # DO ACTION
        user = self.create_new_user()

        # ASSERTS
        self.assertEqual(
            user.intercom_hash,
            user.build_intercom_hash()
        )
        self.assertEqual(
            user.build_intercom_hash(),
            user.get_intercom_hash_from_redis()
        )
