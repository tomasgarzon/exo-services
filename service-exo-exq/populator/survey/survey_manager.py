from singleton_decorator import singleton

from survey.models import Survey

from populate.populator.manager import Manager
from .survey_builder import SurveyBuilder


@singleton
class SurveyManager(Manager):
    model = Survey
    attribute = 'name'
    builder = SurveyBuilder
    files_path = '/survey/files/'
