from ..conf import settings
from .base import BaseValidator


class TeamValidator(BaseValidator):

    def validate(self):
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_NO_TEAM,
            defaults={
                'validation_type': settings.VALIDATION_CH_ERROR,
                'subject': settings.VALIDATION_LABEL_VALIDATION[
                    settings.VALIDATION_CH_NO_TEAM
                ],
            },
        )

        if self.project.teams.count() > 0:
            validation.fixed()
        else:
            validation.pending()
        return validation.is_pending
