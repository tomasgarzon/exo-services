from django.apps import apps
from django.db.models.signals import post_save

from .survey import (
    post_save_survey_handler,
    post_survey_filled_handler)

from ..signals_define import post_survey_filled


def setup_signals():
    Survey = apps.get_model('survey', 'Survey')
    SurveyFilled = apps.get_model('survey', 'SurveyFilled')

    post_save.connect(
        post_save_survey_handler, sender=Survey)
    post_survey_filled.connect(
        post_survey_filled_handler,
        sender=SurveyFilled)
