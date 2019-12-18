from django.apps import apps
from django.db.models.signals import post_save

from typeform_feedback.signals_define import new_user_typeform_response
from typeform_feedback.models import UserGenericTypeformFeedback

from .typeform_feedback_signal import post_save_typeform_feedback_handler
from .user_typeform_responses import notify_by_mail_new_typeform_response


def setup_signals():
    UserGenericTypeformFeedback = apps.get_model(
        app_label='typeform_feedback',
        model_name='UserGenericTypeformFeedback',
    )

    post_save.connect(
        post_save_typeform_feedback_handler,
        sender=UserGenericTypeformFeedback)
    new_user_typeform_response.connect(
        notify_by_mail_new_typeform_response,
        sender=UserGenericTypeformFeedback,
    )
