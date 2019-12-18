from ..models import Validation


class BaseValidator:

    def __init__(self, project):
        self.project = project

    def add_error(self, detail, message='', content_type=None):
        return Validation.objects.create_error(
            self.project,
            detail,
            message,
            content_type,
        )

    def add_warning(self, detail, message='', content_type=None):
        return Validation.objects.create_warning(
            self.project,
            detail,
            message,
            content_type,
        )

    def validate(self):
        raise NotImplementedError('validate method not implemented')
