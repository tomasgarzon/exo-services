from django.apps import apps
from django.db.models.signals import post_save

from .page_post_save import (
    save_page_handler,
    update_website_handler)
from ..signals_define import signal_website_update


def setup_signals():
    Page = apps.get_model(
        app_label='landing', model_name='Page',
    )

    post_save.connect(save_page_handler, sender=Page)

    signal_website_update.connect(update_website_handler, sender=Page)
