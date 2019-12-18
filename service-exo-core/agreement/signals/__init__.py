from django.apps import apps
from django.db.models.signals import post_save, post_delete

from .agreements import (
    post_save_agreement,
    post_save_user_agreement,
    post_delete_user_agreement)


def setup_signals():
    Agreement = apps.get_model(
        app_label='agreement',
        model_name='Agreement',
    )
    UserAgreement = apps.get_model(
        app_label='agreement',
        model_name='UserAgreement',
    )

    post_save.connect(post_save_agreement, sender=Agreement)
    post_save.connect(post_save_user_agreement, sender=UserAgreement)
    post_delete.connect(post_delete_user_agreement, sender=UserAgreement)
