from .utils.redis import ModelRedisCache


class UserPkCache(ModelRedisCache):
    KEY_FIELD_RESOLVER = 'pk'
    KEY_FIELD_PATTERN = 'user:{key_field_resolver}:{key_name}'


class UserEmailCache(ModelRedisCache):
    KEY_FIELD_RESOLVER = 'email'
    KEY_FIELD_PATTERN = 'user:{key_field_resolver}:{key_name}'
