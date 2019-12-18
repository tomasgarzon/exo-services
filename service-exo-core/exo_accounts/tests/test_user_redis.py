from django.conf import settings
from django.test import TestCase
from django.contrib.auth import get_user_model
from mock import patch

from ..test_mixins.faker_factories import FakeUserFactory


class BasicProfileAPITests(TestCase):

    def test_new_user_platform_language_by_redis(self):
        users = FakeUserFactory.create_batch(size=4)
        user = users[0]

        self.assertEqual(user.platform_language_user,
                         user.platform_language)

        user.platform_language = settings.LANGUAGE_ES
        self.assertEqual(user.platform_language_user,
                         settings.LANGUAGE_ES)

    @patch('exo_accounts.lang.UserLanguageManager._repair_langs')
    def test_platform_language_cache_is_updated(self,
                                                mock_repair_platform_language):

        user = FakeUserFactory()

        self.assertFalse(mock_repair_platform_language.called)

        get_user_model().objects.get_platform_languages([user.email])

        self.assertTrue(mock_repair_platform_language.called)
        self.assertEqual(mock_repair_platform_language.call_count, 1)

    @patch('exo_accounts.cache.UserEmailCache.set_key_value')
    def test_platform_language_redis_cache_success(self, mock_redis_set_value):

        user = FakeUserFactory()
        self.assertFalse(mock_redis_set_value.called)

        get_user_model().objects.get_platform_languages([user.email])
        self.assertEqual(mock_redis_set_value.call_count, 1)

    @patch('exo_accounts.cache.UserEmailCache.delete_keys')
    def test_platform_language_redis_cache_invalidation(self,
                                                        mock_redis_delete,):

        user = FakeUserFactory()

        get_user_model().objects.get_platform_languages([user.email])
        user.platform_language = settings.LANGUAGE_ES

        self.assertEqual(mock_redis_delete.call_count, 1)
