from django.apps import apps
from django.db.models.signals import post_save

from consultant.signals_define import (
    consultant_post_activated,
    consultant_post_deactivated)

from .exo_hub_post_save import exo_hub_post_save_handler
from .consultant import (
    consultant_to_ecosystem_handler,
    consultant_to_ecosystem_handler_disable,
)


def setup_signals():
    ExOHub = apps.get_model(
        app_label='exo_hub', model_name='ExOHub')
    Consultant = apps.get_model(
        app_label='consultant', model_name='Consultant')

    post_save.connect(exo_hub_post_save_handler, sender=ExOHub)
    consultant_post_activated.connect(
        consultant_to_ecosystem_handler, sender=Consultant)
    consultant_post_deactivated.connect(
        consultant_to_ecosystem_handler_disable
    )
