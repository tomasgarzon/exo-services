from utils.redis import ModelRedisCache


class ConsultantPkCache(ModelRedisCache):
    KEY_FIELD_RESOLVER = 'pk'
    KEY_FIELD_PATTERN = 'consultant:{key_field_resolver}:{key_name}'
