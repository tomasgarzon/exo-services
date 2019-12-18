from ..conf import settings
from .base import BaseValidator


class FastrackSprintTypeValidator(BaseValidator):

    def validate(self):
        valid = True
        if self.project.is_fastracksprint:
            validation, _ = self.project.validations.get_or_create(
                validation_detail=settings.VALIDATION_CH_FASTRACK_TYPE,
                defaults={
                    'validation_type': settings.VALIDATION_CH_ERROR,
                    'subject': settings.VALIDATION_LABEL_VALIDATION[
                        settings.VALIDATION_CH_FASTRACK_TYPE
                    ],
                },
            )
            valid = False
        return valid
