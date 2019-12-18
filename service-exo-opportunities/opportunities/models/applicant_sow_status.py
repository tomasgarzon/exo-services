from django.db import models

from model_utils.models import TimeStampedModel
from multiselectfield import MultiSelectField
from model_utils import Choices


class ApplicantSOWStatus(TimeStampedModel):
    reasons = Choices(
        ('incorrect', 'Incorrect data'),
        ('economic', 'Economic disagreement'),
        ('date', 'Date unavailability'),
        ('other', 'Other'))

    applicant_sow = models.ForeignKey(
        'ApplicantSow', related_name='history',
        on_delete=models.CASCADE)
    reasons_declined = MultiSelectField(
        choices=reasons,
        blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def get_reasons_display(self):
        return [
            dict(self.reasons).get(value) for value in self.reasons_declined]
