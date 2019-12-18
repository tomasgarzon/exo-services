from django.db import models

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin


class Answer(CreatedByMixin, TimeStampedModel):

    applicant = models.ForeignKey(
        'opportunities.Applicant',
        related_name='answers',
        on_delete=models.CASCADE,
    )
    question = models.ForeignKey(
        'opportunities.Question',
        related_name='answers',
        on_delete=models.CASCADE,
    )
    response = models.CharField(max_length=512)

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    def __str__(self):
        return '{} - {}'.format(
            self.question,
            self.response,
        )

    @property
    def response_text(self):
        response_text = self.response
        if self.is_boolean:
            response_text = 'Yes' if eval(self.response) else 'No'

        return response_text

    @property
    def is_boolean(self):
        return self.question.is_boolean
