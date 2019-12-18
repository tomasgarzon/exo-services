from django.apps import apps
from django.db.models.signals import post_save as post_save_signal

from referral.models import Campaign
from referral.signals_define import referral_reward_acquired

from ..metric.signals import metrics_handler
from .define import set_null_signal, edit_slug_field  # noqa
from .referral_reward import referral_reward_acquired_handler


def setup_signals():

    Action = apps.get_model(app_label='actstream', model_name='Action')

    post_save_signal.connect(metrics_handler, sender=Action)

    # django-earlyparrot
    referral_reward_acquired.connect(referral_reward_acquired_handler, sender=Campaign)
