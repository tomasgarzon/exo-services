from .redis_cache_mixin import RedisCacheMixin


class ModelRedisCache(RedisCacheMixin):

    def _raise_not_implemented(self, attr):
        message = 'Attr Not Implemented {}'.format(attr)
        raise NotImplementedError(message)

    def _get_field_pattern(self):
        attr = 'KEY_FIELD_PATTERN'
        pattern = getattr(self, attr)
        return pattern if pattern else self._raise_not_implemented(attr)

    def _build_key(self, key, instance):
        key_field_resolver = getattr(instance, self.KEY_FIELD_RESOLVER)
        key_formated = self._get_field_pattern().format(
            key_field_resolver=key_field_resolver,
            key_name=key,
        )
        return key_formated

    def _build_key_resolver(self, key, key_resolver):
        key_formated = self._get_field_pattern().format(
            key_field_resolver=key_resolver,
            key_name=key,
        )
        return key_formated

    def _delete_key(self, instance, key):
        key_formated = self._build_key(key, instance)
        return self._delete(key_formated)

    def _get_keys_by_filter(self, keys_filters):
        return self._get_keys_filtered(keys_filters)

    def get_key_value(self, instance, key):
        key_name = self._build_key(key, instance)
        key_value = self._get_value(key_name)
        return key_value if key_value else None

    def set_key_value(self, instance, key, value):
        key_name = self._build_key(key, instance)
        return self._set_value(key_name, value)

    def delete_keys(self, instance, keys_array):
        for key in keys_array:
            self._delete_key(instance, key)
