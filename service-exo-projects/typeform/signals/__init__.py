from django.apps import apps
from django.db.models.signals import post_save

from .typeform_feedback_signal import post_save_typeform_feedback_handler


def setup_signals():
    UserGenericTypeformFeedback = apps.get_model(
        app_label='typeform_feedback',
        model_name='UserGenericTypeformFeedback',
    )

    post_save.connect(
        post_save_typeform_feedback_handler,
        sender=UserGenericTypeformFeedback)
