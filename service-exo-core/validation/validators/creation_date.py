from django.utils import timezone

from ..conf import settings
from .base import BaseValidator


class CreationDateValidator(BaseValidator):
    creation_from = timezone.datetime(
        2017, 1, 1, tzinfo=timezone.get_current_timezone(),
    )

    def validate(self):
        valid = True
        if self.project.created <= self.creation_from:
            validation, _ = self.project.validations.get_or_create(
                validation_detail=settings.VALIDATION_CH_NO_DATE,
                defaults={
                    'validation_type': settings.VALIDATION_CH_ERROR,
                    'subject': settings.VALIDATION_LABEL_VALIDATION[
                        settings.VALIDATION_CH_NO_DATE
                    ].format(self.creation_from.year),
                },
            )
            valid = False
        return valid


class PlatformCreateValidator(CreationDateValidator):
    creation_from = timezone.datetime(
        2018, 7, 8, tzinfo=timezone.get_current_timezone(),
    )
