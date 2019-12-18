from project.models import Step

from ..conf import settings
from .base import BaseValidator


class SprintAutomatedStartDateValidator(BaseValidator):

    def validate(self):
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_PERIOD_1_NO_START_DATE,
            defaults={
                'validation_type': settings.VALIDATION_CH_WARNING,
                'subject': settings.VALIDATION_LABEL_VALIDATION[settings.VALIDATION_CH_PERIOD_1_NO_START_DATE],
            }
        )

        steps = Step.objects.filter_by_project(self.project)
        if steps.exists():
            steps = steps.exclude(id=steps.first().id)

        if steps.filter(start__isnull=True).exists():
            validation.pending()
        else:
            validation.fixed()

        return validation.is_pending
