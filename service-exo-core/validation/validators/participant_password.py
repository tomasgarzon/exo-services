from ..conf import settings
from .base import BaseValidator


class ParticipantPasswordValidator(BaseValidator):

    def validate(self):
        validation, _ = self.project.validations.get_or_create(
            validation_detail=settings.VALIDATION_CH_PART_PASS,
            defaults={
                'validation_type': settings.VALIDATION_CH_WARNING,
                'subject': settings.VALIDATION_LABEL_VALIDATION[
                    settings.VALIDATION_CH_PART_PASS
                ],
            },
        )

        if self.project.settings.launch['fix_password'] != '':
            validation.fixed()
        else:
            validation.pending()
        return validation.is_pending
