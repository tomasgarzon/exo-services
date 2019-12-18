from django.db import models

from model_utils.models import TimeStampedModel


class Answer(TimeStampedModel):
    survey = models.ForeignKey(
        'SurveyFilled',
        related_name='answers',
        on_delete=models.CASCADE)
    question = models.ForeignKey(
        'Question',
        related_name='answers',
        on_delete=models.CASCADE)
    option = models.ForeignKey(
        'Option',
        related_name='answers',
        null=True, blank=True,
        on_delete=models.CASCADE)
    score = models.FloatField()

    class Meta:
        ordering = ['question__order']

    def __str__(self):
        return '{} - {}: {}'.format(
            self.survey, self.question.name, self.score)

    def section(self):
        return self.question.section

    @property
    def order(self):
        return self.option_selected.order

    @property
    def value(self):
        return self.option_selected.value

    @property
    def option_selected(self):
        return self.option or self.question.options.filter(score=self.score).first()
