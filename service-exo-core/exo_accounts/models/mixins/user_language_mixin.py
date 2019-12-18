from ...conf import settings


class UserLanguageMixin:

    @property
    def platform_language(self):
        return self._platform_language

    @platform_language.setter
    def platform_language(self, platform_language):
        valid_language = platform_language in dict(settings.LANGUAGES).keys()
        self._platform_language = platform_language if valid_language else settings.LANGUAGE_DEFAULT
        self.save(update_fields=['_platform_language'])

    @property
    def platform_language_user(self):
        language_redis = self.get_platform_language_from_redis()
        return language_redis if language_redis else self.platform_language

    def get_platform_language_from_redis(self):
        cache = self.get_cache_by_email()
        key_name = settings.EXO_ACCOUNTS_REDIS_KEY_PLATFORM_LANGUAGE
        return cache.get_key_value(self, key_name)

    def set_platform_language_in_redis(self, language_value):
        cache = self.get_cache_by_email()
        key_name = settings.EXO_ACCOUNTS_REDIS_KEY_PLATFORM_LANGUAGE
        return cache.set_key_value(self, key_name, language_value)

    def delete_platform_language_from_redis(self):
        cache = self.get_cache_by_email()
        key_name = settings.EXO_ACCOUNTS_REDIS_KEY_PLATFORM_LANGUAGE
        keys = [key_name]
        return cache.delete_keys(self, keys)
