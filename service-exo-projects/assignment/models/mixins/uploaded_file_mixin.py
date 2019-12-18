from django.conf import settings


class UploadedFileMixin:

    @property
    def uploaded_files(self):
        return self.files.all()

    def get_uploaded_files_with_visibility(self):
        return self.files_with_visibility.all()

    def uploaded_files_with_visibility(self, user_from):
        user_from_files = []

        all_files = self.uploaded_files
        all_files_without_visibility = all_files.filter(visibility__isnull=True)
        all_files_with_visibility = self.get_uploaded_files_with_visibility()

        files_with_visibility_public = all_files_with_visibility.filter(visibility=settings.FILES_VISIBILITY_GROUP)
        files_with_visibility_private = all_files_with_visibility.filter(visibility=settings.FILES_VISIBILITY_PRIVATE)

        # ALL users --> Files without visibility relation model or with public visibility
        user_from_files += all_files_without_visibility.values_list('pk', flat=True)
        user_from_files += files_with_visibility_public.values_list('uploaded_file__pk', flat=True)

        # COACH perms --> All files private
        if self.team.user_is_admin(user_from):
            user_from_files += files_with_visibility_private \
                .values_list('uploaded_file__pk', flat=True)
        # TEAM perms --> Private files created by me
        else:
            user_from_files += files_with_visibility_private \
                .filter(created_by=user_from) \
                .values_list('uploaded_file__pk', flat=True)

        return all_files.filter(pk__in=user_from_files).distinct()

    def can_upload_files(self, user, raise_exception=True):
        raise NotImplementedError

    def can_view_uploaded_file(self, user, raise_exception=True):
        raise NotImplementedError

    def can_update_uploaded_file(self, user, uploaded_file_version, raise_exception=True):
        raise NotImplementedError

    def can_delete_uploaded_file(self, user, uploaded_file, raise_exception=True):
        raise NotImplementedError
