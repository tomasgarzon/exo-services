from singleton_decorator import singleton

from survey.models import SurveyFilled

from populate.populator.manager import Manager
from .survey_filled_builder import SurveyFilledBuilder


@singleton
class SurveyFilledManager(Manager):
    model = SurveyFilled
    attribute = 'name'
    builder = SurveyFilledBuilder
    files_path = '/survey_filled/files/'
