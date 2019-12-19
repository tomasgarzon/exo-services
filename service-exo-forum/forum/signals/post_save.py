from actstream.actions import follow

from ..conf import settings
from ..tasks.answer_tasks import NotifyAnswerChangeTask
from ..tasks.post_tasks import NotifyPostChangeTask


def new_topic_post_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        follow(instance.created_by, instance)
        instance.add_permission(
            settings.FORUM_PERMS_EDIT_POST,
            instance.created_by)
        action = settings.FORUM_NOTIFICATION_ACTION_CREATE
    elif instance.is_removed:
        action = settings.FORUM_NOTIFICATION_ACTION_DELETE
    else:
        action = settings.FORUM_NOTIFICATION_ACTION_UPDATE

    NotifyPostChangeTask().s(
        action=action,
        post_pk=instance.pk,
    ).apply_async()


def new_answer_post_save_handler(sender, instance, created, *args, **kwargs):
    if created:
        follow(instance.created_by, instance.post)
        follow(instance.created_by, instance)
        instance.add_permission(
            settings.FORUM_PERMS_EDIT_ANSWER,
            instance.created_by)
        action = settings.FORUM_NOTIFICATION_ACTION_CREATE
    elif instance.is_removed:
        action = settings.FORUM_NOTIFICATION_ACTION_DELETE
    else:
        action = settings.FORUM_NOTIFICATION_ACTION_UPDATE

    NotifyAnswerChangeTask().s(
        action=action,
        answer_pk=instance.pk,
    ).apply_async()
