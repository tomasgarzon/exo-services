from populate.populator.common.errors import ConfigurationError
from .survey_filled_manager import SurveyFilledManager


def survey_filled_constructor(loader, node):
    item = loader.construct_mapping(node=node)
    if not isinstance(item, dict) or not item:
        raise ConfigurationError(
            'value {} cannot be interpreted as an opportunity'.format(item))
    return SurveyFilledManager().get_object(item)
