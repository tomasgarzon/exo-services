from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


class ApplicantFeedback(CreatedByMixin, TimeStampedModel):
    applicant = models.ForeignKey(
        'Applicant',
        on_delete=models.CASCADE,
        related_name='feedbacks',
    )
    status = models.CharField(
        max_length=1,
        choices=settings.OPPORTUNITIES_APPLICANT_JOB_STATUS,
        blank=True, null=True)
    explained = models.IntegerField(blank=True, null=True)
    collaboration = models.IntegerField(blank=True, null=True)
    communication = models.IntegerField(blank=True, null=True)
    recommendation = models.IntegerField(blank=True, null=True)
    comment = models.TextField(
        blank=True, null=True,
    )

    def __str__(self):
        return '{} - {}'.format(
            self.applicant,
            self.created_by,
        )
