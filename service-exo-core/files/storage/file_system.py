from pathlib import Path

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class ResourceStorage(FileSystemStorage):

    def __init__(self):
        folder_name = settings.FILES_S3_RESOURCE_FOLDER
        path = Path(settings.PROTECTED_ROOT, folder_name)
        location = path.as_posix()
        super().__init__(location=location)

    def save_multipart(self, file_name, file_data):
        # multipart not sopported
        return self.save(file_name, file_data.raw)
