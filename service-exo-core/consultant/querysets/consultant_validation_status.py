from django.db import models

from ..conf import settings


class ConsultantValidationStatusQuerySet(models.QuerySet):

    def filter_by_status(self, status):
        return self.filter(status=status)

    def filter_by_type(self, validation_type):
        return self.filter(validation__name=validation_type)

    def filter_denied(self):
        return self.filter_by_status(
            status=settings.CONSULTANT_VALIDATION_CH_DENIED,
        )

    def filter_accepted(self):
        return self.filter_by_status(
            status=settings.CONSULTANT_VALIDATION_CH_ACCEPTED,
        )

    def filter_waiting(self):
        return self.filter_by_status(
            status=settings.CONSULTANT_VALIDATION_CH_WAITING,
        )

    def filter_agreements(self):
        return self.filter_by_type(settings.CONSULTANT_VALIDATION_AGREEMENT)

    def filter_skillassessments(self):
        return self.filter_by_type(settings.CONSULTANT_VALIDATION_SKILL_ASSESSMENT)

    def filter_application(self):
        return self.filter_by_type(settings.CONSULTANT_VALIDATION_APPLICATION)

    def filter_test(self):
        return self.filter_by_type(settings.CONSULTANT_VALIDATION_TEST)
