import hmac
import hashlib

from ...conf import settings

KEY_INTERCOM_HASH = settings.EXO_ACCOUNTS_REDIS_KEY_INTERCOM_HASH


class IntercomUserMixin:

    @property
    def intercom_hash(self):
        intercom_hash = self.get_intercom_hash_from_redis()
        if not intercom_hash and self.get_intercom_secret_key():
            intercom_hash = self.build_intercom_hash()
            self.set_intercom_hash_in_redis(intercom_hash)
        return intercom_hash

    def get_intercom_secret_key(self):
        return getattr(settings, 'INTERCOM_SECRET_KEY', None)

    def get_intercom_hash_from_redis(self):
        cache = self.get_cache_by_pk()
        return cache.get_key_value(self, KEY_INTERCOM_HASH)

    def build_intercom_hash(self):
        key = self.get_intercom_secret_key()
        key_bytes = key.encode('ascii')
        message = str(self.id)
        message_bytes = message.encode('ascii')
        return hmac.new(key_bytes, message_bytes, hashlib.sha256).hexdigest()

    def set_intercom_hash_in_redis(self, intercom_hash_value):
        cache = self.get_cache_by_pk()
        return cache.set_key_value(
            self,
            KEY_INTERCOM_HASH,
            intercom_hash_value)
