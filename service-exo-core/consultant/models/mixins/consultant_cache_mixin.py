from ...cache import ConsultantPkCache


class ConsultantCacheMixin:

    def get_cache_by_pk(self):
        return ConsultantPkCache()
