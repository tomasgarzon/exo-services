from service.celery import app

from .survey_filled import SurveyFilledTask

app.tasks.register(SurveyFilledTask())
