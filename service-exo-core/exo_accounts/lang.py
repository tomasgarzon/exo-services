
from django.contrib.auth import get_user_model

from collections import OrderedDict

from exo_accounts.cache import UserEmailCache

from .conf import settings


class UserLanguageManager:

    def __init__(self, **kwargs):
        self.users_email = kwargs.get('emails')

    def get_platform_languages(self):
        languages = self._get_langs()
        return [_ for _ in OrderedDict.fromkeys(languages).keys()]

    def _get_langs(self):
        key_name = settings.EXO_ACCOUNTS_REDIS_KEY_PLATFORM_LANGUAGE
        languages = self._get_langs_filter(key_name)

        if None in languages:
            languages = self._repair_langs(languages)
        return languages

    def _get_langs_filter(self, key):
        cache = UserEmailCache()
        keys_filters = [cache._build_key_resolver(key, cache.KEY_FIELD_RESOLVER) for _ in self.users_email]
        return cache._get_keys_by_filter(keys_filters)

    def _get_user(self, email):
        return get_user_model().objects.get_by_email(email=email)

    def _repair_langs(self, languages):
        for index, language in enumerate(languages):
            if language is None:
                email = self.users_email[index]
                user = self._get_user(email)
                lang = user.platform_language
                user.set_platform_language_in_redis(lang)
                languages[index] = lang
        return languages
