from django.core.files.storage import get_storage_class
from django.conf import settings


def get_storage(path=None, options=None):
    path = path or settings.EXOMAILER_STORAGE
    options = options or settings.EXOMAILER_STORAGE_OPTIONS
    if not path:
        raise Exception('You must specify a storage class using '
                        'EXOMAILER_STORAGE settings.')
    return Storage(path, **options)


class Storage:
    def __init__(self, storage_path=None, **options):
        self._storage_path = storage_path or settings.EXOMAILER_STORAGE
        options = options.copy()
        options.update(settings.EXOMAILER_STORAGE_OPTIONS)
        options = dict([(key.lower(), value) for key, value in options.items()])
        self.storage_class = get_storage_class(self._storage_path)
        self.storage = self.storage_class(**options)
        self.name = self.storage_class.__name__

    def __str__(self):
        return self.storage.__str__()

    def write_file(self, filehandle, filename):
        return self.storage.save(name=filename, content=filehandle)

    def read_file(self, filepath):
        file_ = self.storage.open(name=filepath, mode='rb')
        if not getattr(file_, 'name', None):
            file_.name = filepath
        return file_.read()
