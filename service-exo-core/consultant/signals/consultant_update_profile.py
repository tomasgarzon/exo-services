from achievement.signals.define import signal_update_profile_achievement

from ..helpers.checkers import (
    check_keyword_for_consultant,
    check_summary_for_user,
    check_location_for_user,
    check_profile_picture_for_user
)
from ..models.consultant_profile_requirement import ConsultantProfileRequirement


def post_save_update_languages(sender, instance, *args, **kwargs):
    action = kwargs.get('action')
    if action == 'post_add':
        pk_set = kwargs.get('pk_set')
        if len(pk_set) > 0:
            profile_redis = ConsultantProfileRequirement()
            profile_redis.complete_languages(instance)
            signal_update_profile_achievement.send(
                sender=instance.__class__,
                consultant=instance,
            )


def update_keyword_redis(consultant):
    if check_keyword_for_consultant(consultant):
        profile_redis = ConsultantProfileRequirement()
        profile_redis.complete_keywords(consultant)
        signal_update_profile_achievement.send(
            sender=consultant.__class__,
            consultant=consultant,
        )


def post_save_update_keywords(sender, instance, *args, **kwargs):
    created = kwargs.get('created')
    if created:
        update_keyword_redis(instance.consultant)


def post_save_update_user_redis(sender, instance, *args, **kwargs):
    if not instance.is_consultant:
        return
    completed = False
    profile_redis = ConsultantProfileRequirement()
    if check_summary_for_user(instance):
        profile_redis.complete_summary(instance.consultant)
        completed = True
    if check_location_for_user(instance):
        profile_redis.complete_location(instance.consultant)
        completed = True
    if check_profile_picture_for_user(instance):
        profile_redis.complete_profile_picture(instance.consultant)
        completed = True
    if completed:
        signal_update_profile_achievement.send(
            sender=instance.consultant.__class__,
            consultant=instance.consultant,
        )
