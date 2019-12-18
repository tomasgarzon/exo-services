from django.apps import apps

from .define import signal_update_profile_achievement
from .update_profile_achievement import check_update_achievement_for_user


def setup_signals():
    Consultant = apps.get_model(
        app_label='consultant', model_name='Consultant',
    )

    signal_update_profile_achievement.connect(
        check_update_achievement_for_user,
        sender=Consultant,
    )
