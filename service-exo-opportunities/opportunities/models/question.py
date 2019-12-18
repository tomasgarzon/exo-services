from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from ..conf import settings


class Question(CreatedByMixin, TimeStampedModel):

    opportunity = models.ForeignKey(
        'opportunities.Opportunity',
        related_name='questions',
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=512)
    type_question = models.CharField(
        max_length=1,
        default=settings.OPPORTUNITIES_QUESTION_CH_TYPE_DEFAULT,
        choices=settings.OPPORTUNITIES_QUESTION_CH_TYPE_CHOICES,
    )

    CHOICES_DESCRIPTOR_FIELDS = ['type_question']

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return '{} - {} [{}]'.format(
            self.opportunity,
            self.title,
            self.get_type_question_display(),
        )

    @property
    def is_boolean(self):
        return self.type_question == settings.OPPORTUNITIES_QUESTION_CH_TYPE_BOOLEAN
