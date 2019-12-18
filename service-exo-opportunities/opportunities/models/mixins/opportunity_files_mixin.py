from django.core.exceptions import ValidationError


class OpportunityFileMixin:

    def can_upload_files(self, user, raise_exception=True):
        allowed = user in self.admin_users
        if not allowed and raise_exception:
            raise ValidationError('user can not upload')
        return allowed

    def can_view_uploaded_file(self, user, raise_exception=True):
        return True

    def can_update_uploaded_file(self, user, uploaded_file_version, raise_exception=True):
        allowed = user in self.admin_users
        if not allowed and raise_exception:
            raise ValidationError('user can not update')
        return allowed

    def can_delete_uploaded_file(self, user, uploaded_file, raise_exception=True):
        allowed = user in self.admin_users
        if not allowed and raise_exception:
            raise ValidationError('user can not upload')
        return allowed
