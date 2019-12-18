from ..conf import settings
from .base import BaseValidator


class ProjectInfoValidator(BaseValidator):

    def validate_start(self):
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_NO_START,
            defaults={
                'validation_type': settings.VALIDATION_CH_ERROR,
                'subject': settings.VALIDATION_LABEL_VALIDATION[settings.VALIDATION_CH_NO_START],
            },
        )
        if not self.project.start:
            validation.pending()
        else:
            validation.delete()

    def validate_agenda(self):
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_NO_AGENDA,
            defaults={
                'validation_type': settings.VALIDATION_CH_WARNING,
                'subject': settings.VALIDATION_LABEL_VALIDATION[settings.VALIDATION_CH_NO_AGENDA],
            },
        )
        if not self.project.agenda:
            validation.pending()
        else:
            validation.delete()

    def validate(self):
        v2 = self.validate_start()
        v3 = self.validate_agenda()
        return v2 and v3
