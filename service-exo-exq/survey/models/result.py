from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel


class Result(TimeStampedModel):
    survey = models.ForeignKey(
        'SurveyFilled',
        on_delete=models.CASCADE,
        related_name='results')
    section = models.CharField(
        max_length=1,
        choices=settings.SURVEY_CH_SECTION)
    score = models.FloatField()
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{}: {}'.format(
            self.get_section_display(), self.score)

    @property
    def max_score(self):
        return 3 if self.section != settings.SURVEY_CH_BUSINESS_MODEL else 1
