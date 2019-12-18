from django.db import models

from model_utils.models import TimeStampedModel

from ...conf import settings
from ...managers.consultant_industry import ConsultantIndustryManager


class ConsultantIndustry(
        TimeStampedModel
):
    consultant = models.ForeignKey(
        'consultant.Consultant',
        related_name='industries',
        on_delete=models.CASCADE,
    )
    industry = models.ForeignKey(
        'industry.Industry',
        related_name='consultants',
        on_delete=models.CASCADE,
    )
    level = models.IntegerField(
        choices=settings.RELATION_INDUSTRIES_CHOICES,
    )

    objects = ConsultantIndustryManager()

    def __str__(self):
        return '{} - {}: {}'.format(self.consultant, self.industry, self.get_level_display())
