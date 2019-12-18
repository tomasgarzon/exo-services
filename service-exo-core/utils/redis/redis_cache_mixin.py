from .connection import RedisConnection


class RedisCacheMixin(RedisConnection):

    def _get_value(self, key):
        value = self.connection.get(key)
        try:
            return eval(value)
        except TypeError:
            return value

    def _get_keys_filtered(self, keys):
        return self.connection.mget(keys)

    def _set_value(self, key_name, value):
        return self.connection.set(key_name, value.__str__())

    def _delete(self, key_names):
        return self.connection.delete(key_names)
