from django.conf import settings

from rest_framework import serializers

from ...models import UploadedFile
from .uploaded_file import UploadedFileSerializer


class FilesCreationSerializerMixin(serializers.ModelSerializer):
    uploaded_files = UploadedFileSerializer(many=True, required=False, read_only=True)

    def get_files(self):
        return self.context.get('request').data.get('uploaded_files', [])

    def delete_old_files(self, instance, new_files):
        for file in instance.uploaded_files:
            remove = True

            for new_file in new_files:
                if new_file.get('url') == file.url:
                    remove = False

            if remove:
                file.delete()

    def save_files(self, user_from, instance, delete_old=False):
        files = self.get_files()

        if delete_old:
            self.delete_old_files(instance, files)

        for file in files:
            if settings.FILES_CDN_FILESTACK in file.get('url'):
                UploadedFile.create(
                    created_by=user_from,
                    filename=file.get('filename'),
                    mimetype=file.get('mimetype'),
                    filestack_url=file.get('url'),
                    filestack_status=file.get('filestack_status'),
                    related_to=instance)
