from django.db import models
from django.conf import settings

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from ..calculate_score import calculate_corrected_score


class SurveyFilled(CreatedByMixin, TimeStampedModel):
    name = models.CharField(
        max_length=500,
        default='')
    email = models.CharField(
        max_length=500,
        default='')
    organization = models.CharField(
        max_length=500,
        default='')
    industry = models.ForeignKey(
        'industry.Industry',
        blank=True, null=True,
        related_name='surveys',
        on_delete=models.SET_NULL)
    language = models.CharField(
        max_length=10,
        blank=True, null=True,
        default=settings.SURVEY_CH_ENGLISH)
    survey = models.ForeignKey(
        'Survey',
        related_name='surveys_filled',
        on_delete=models.CASCADE)
    total = models.FloatField(
        blank=True, null=True)

    def __str__(self):
        return '{} - {}: {}'.format(
            self.name, self.email, self.survey.name)

    def _fill_answers(self, answers):
        for answer in answers:
            score = answer.get('option').score
            self.answers.update_or_create(
                question=answer.get('question'),
                defaults={
                    'option': answer.get('option'),
                    'score': score})
        self._fill_results()
        self.calculate_exq()

    def _fill_results(self):
        for index, (section, _) in enumerate(settings.SURVEY_CH_SECTION):
            score = self.answers.filter(
                question__section=section
            ).aggregate(score=models.Avg('score')).get('score')
            self.results.update_or_create(
                section=section,
                order=index,
                defaults={'score': round(score, 2)})

    def calculate_exq(self):
        if self.total is not None:
            self.result_logs.create(score=self.total)
        self.total = calculate_corrected_score(self)
        self.save(update_fields=['total'])

    def abundance_factors(self):
        attributes = [
            settings.SURVEY_CH_MTP,
            settings.SURVEY_CH_STAFF_ON_DEMAND,
            settings.SURVEY_CH_COMMUNITY_CROUD,
            settings.SURVEY_CH_ALGORITHMS_DATA,
            settings.SURVEY_CH_LEVERAGED_ASSETS,
            settings.SURVEY_CH_ENGAGEMENT
        ]
        results = []
        for attribute in attributes:
            result = self.results.get(section=attributes).score
            results.append(1 if result * 3 >= 5 else 0)
        return results

    @property
    def correction_factor(self):
        total = sum(self.abundance_factors())
        return 100 if total >= 4 else 70


class ResultLog(TimeStampedModel):
    survey_filled = models.ForeignKey(
        'SurveyFilled',
        on_delete=models.CASCADE,
        related_name='result_logs')
    score = models.FloatField()
