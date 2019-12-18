from populate.populator.common.errors import ConfigurationError
from .survey_manager import SurveyManager


def survey_constructor(loader, node):
    item = loader.construct_mapping(node=node)
    if not isinstance(item, dict) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an survey'.format(item))
    return SurveyManager().get_object(item)


def survey_reference_constructor(loader, node):
    item = loader.construct_scalar(node=node)
    if not isinstance(item, str) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an survey'.format(item))
    return SurveyManager().get_object(item)
