from ...cache import UserEmailCache, UserPkCache


class UserCacheMixin:
    def get_cache_by_email(self):
        return UserEmailCache()

    def get_cache_by_pk(self):
        return UserPkCache()
