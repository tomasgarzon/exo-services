from project.models import Step

from ..conf import settings
from .base import BaseValidator


class StepValidator(BaseValidator):

    def validate(self):
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_STEPS_DEFINED,
            defaults={
                'validation_type': settings.VALIDATION_CH_ERROR,
                'subject': settings.VALIDATION_LABEL_VALIDATION[settings.VALIDATION_CH_STEPS_DEFINED],
            }
        )

        if not Step.objects.filter_by_project(self.project).exists():
            validation.pending()
        else:
            validation.fixed()

        return validation.is_pending
