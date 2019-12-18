from django.db import models
from django.conf import settings
from django.utils.translation import get_language

from model_utils.models import TimeStampedModel

from utils.models import CreatedByMixin

from .mixins import SurveyReportMixin
from ..manager.survey import SurveyManager
from ..signals_define import post_survey_filled


class Survey(SurveyReportMixin, CreatedByMixin, TimeStampedModel):
    name = models.CharField(
        max_length=500,
        default='')
    slug = models.CharField(
        max_length=200,
        unique=True)
    send_results = models.BooleanField(default=True)
    show_results = models.BooleanField(default=True)
    language = models.CharField(
        max_length=2,
        blank=True, null=True,
        choices=settings.SURVEY_CH_LANGUAGES,
        default=settings.SURVEY_CH_ENGLISH)
    objects = SurveyManager()

    def __str__(self):
        return self.name

    def fill(self, name, email, answers, industry, organization=None):
        survey_filled = self.surveys_filled.create(
            name=name,
            organization=organization,
            industry=industry,
            email=email,
            language=get_language())
        survey_filled._fill_answers(answers)
        post_survey_filled.send(
            instance=survey_filled,
            sender=survey_filled.__class__)
        return survey_filled

    @property
    def public_url(self):
        return settings.DOMAIN_NAME + '/public-exq/'
