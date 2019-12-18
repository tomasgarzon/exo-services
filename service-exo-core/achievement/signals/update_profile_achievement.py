from django.conf import settings

from consultant.helpers.cache import *  # noqa
from ..models import UserAchievement


def check_update_achievement_for_user(sender, consultant, *args, **kwargs):
    user_achievement = UserAchievement.objects.filter(
        user=consultant.user,
        achievement__code=settings.ACHIEVEMENT_CH_CODE_FILL_PROFILE,
        status=settings.ACHIEVEMENT_STATUS_CH_PENDING,
    )
    if user_achievement.exists():
        check_requirements = True
        class_requirements = [
            KeywordFieldFilled, LanguageFieldFilled,  # noqa
            ProfilePictureFieldFilled, SummaryFieldFilled,  # noqa
            LocationFieldFilled,    # noqa
        ]
        for ProfileRequirement in class_requirements:
            check_requirements &= ProfileRequirement(consultant).check()
        if check_requirements:
            user_achievement.first().complete()
