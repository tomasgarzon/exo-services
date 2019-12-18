import builtins
import logging

from django.conf import settings
from django.apps import apps

logger = logging.getLogger(__name__)


def cast_value(type_name, value):
    type_class = getattr(builtins, type_name)
    if type_class is bool:
        try:
            return eval(value)
        except TypeError:
            return False
    return type_class(value)


class ExOConsultingEnabled:

    def __call__(self, agent):
        Consultant = apps.get_model('consultant', 'Consultant')
        if isinstance(agent, Consultant):
            return agent.user.has_perm(
                settings.EXO_ACTIVITY_PERM_CH_ACTIVITY_CONSULTING)
        return False


class ExOAdvisingEnabled:
    def __call__(self, agent):
        Consultant = apps.get_model('consultant', 'Consultant')
        if isinstance(agent, Consultant):
            return agent.user.has_perm(
                settings.EXO_ACTIVITY_PERM_CH_ACTIVITY_ADVISING)
        return False
