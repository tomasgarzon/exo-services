from ..conf import settings
from ..helpers import update_or_create_badge


def consultant_project_role_post_save(sender, instance, created, *args, **kwargs):
    if instance.project.start is None:
        return

    item = {
        'name': instance.project.name,
        'date': instance.project.start.date(),
    }

    if instance.is_active:
        update_or_create_badge(
            user_from=instance.consultant.user,
            user_to=instance.consultant.user,
            code=instance.exo_role.code,
            category=instance.exo_role.categories.first().code,
            items=[item],
            description=settings.BADGE_ACTION_LOG_CREATE_SIGNAL_DESCRIPTION)


def consultant_project_role_post_delete(sender, instance, *args, **kwargs):

    if instance.project.start is not None:
        item = {
            'name': instance.project.name,
            'date': instance.project.start.date(),
        }

        update_or_create_badge(
            user_from=instance.consultant.user,
            user_to=instance.consultant.user,
            code=instance.exo_role.code,
            category=instance.exo_role.categories.first().code,
            items=[item],
            description=settings.BADGE_ACTION_LOG_CREATE_SIGNAL_DESCRIPTION,
            delete=True)


def user_project_role_post_save(sender, instance, created, *args, **kwargs):
    if instance.project.start is None:
        return

    item = {
        'name': instance.project.name,
        'date': instance.project.start.date(),
    }

    if instance.is_active:
        update_or_create_badge(
            user_from=instance.user,
            user_to=instance.user,
            code=instance.exo_role.code,
            category=instance.exo_role.categories.first().code,
            items=[item],
            description=settings.BADGE_ACTION_LOG_CREATE_SIGNAL_DESCRIPTION)


def user_project_role_post_delete(sender, instance, *args, **kwargs):

    if instance.project.start is not None:
        item = {
            'name': instance.project.name,
            'date': instance.project.start.date(),
        }

        update_or_create_badge(
            user_from=instance.user,
            user_to=instance.user,
            code=instance.exo_role.code,
            category=instance.exo_role.categories.first().code,
            items=[item],
            description=settings.BADGE_ACTION_LOG_CREATE_SIGNAL_DESCRIPTION,
            delete=True)
