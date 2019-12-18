from .connection import RedisConnection


class RedisCacheMixin(RedisConnection):

    def _get_value(self, key):
        return self.connection.get(key)

    def _get_keys_filtered(self, keys):
        return self.connection.mget(keys)

    def _set_value(self, key_name, value):
        return self.connection.set(key_name, value)

    def _delete(self, key_names):
        return self.connection.delete(key_names)
