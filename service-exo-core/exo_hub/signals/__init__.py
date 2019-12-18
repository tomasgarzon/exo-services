from django.apps import apps

from consultant.signals_define import consultant_post_activated
from .consultant_hub import (
    consultant_to_hub_handler)


def setup_signals():
    Consultant = apps.get_model(
        app_label='consultant', model_name='Consultant')

    consultant_post_activated.connect(
        consultant_to_hub_handler, sender=Consultant)
