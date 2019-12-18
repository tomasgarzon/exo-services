from django.utils.module_loading import import_string
from ..conf import settings


def get_storage_class(default_storage, import_path=None):
    return import_string(import_path or default_storage)


class DefaultResourceStorage():
    def __init__(self):
        import_path = getattr(settings, 'RESOURCE_STORAGE', None)
        self._storage_class = get_storage_class(
            default_storage=settings.FILES_RESOURCE_STORAGE,
            import_path=import_path,
        )

    def build(self):
        return self._storage_class()


resource_storage = DefaultResourceStorage()
