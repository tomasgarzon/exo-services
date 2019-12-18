from django.apps import apps
from django.db.models.signals import post_save

from .consultant import consultant_post_save_resource_perms

from ..signals_define import microlearning_webhook_received_send
from .microlearning_signal import microlearning_handler


def setup_signals():
    Consultant = apps.get_model(
        app_label='consultant', model_name='Consultant',
    )
    post_save.connect(consultant_post_save_resource_perms, sender=Consultant)

    microlearning_webhook_received_send.connect(
        microlearning_handler)
