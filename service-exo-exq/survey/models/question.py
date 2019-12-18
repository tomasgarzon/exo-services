from django.db import models

from model_utils.models import TimeStampedModel

from ..conf import settings


class Question(TimeStampedModel):
    name = models.CharField(
        max_length=500,
        default='')
    section = models.CharField(
        max_length=1,
        choices=settings.SURVEY_CH_SECTION)
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return '{} - {}: {}'.format(
            self.name, self.get_section_display(), self.order)

    @property
    def order_increased(self):
        return self.order + 1


class Option(TimeStampedModel):
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='options',
    )
    value = models.TextField()
    score = models.FloatField()
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.value
