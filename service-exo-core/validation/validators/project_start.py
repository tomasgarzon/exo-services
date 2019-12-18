from ..conf import settings
from .base import BaseValidator


class ProjectStartValidator(BaseValidator):

    def validate(self):
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

        return validation.is_pending
