from guardian.shortcuts import assign_perm, remove_perm

from ..conf import settings


def post_save_participant(sender, instance, created, *args, **kwargs):
    if instance.user:
        if instance.is_deleted:
            remove_perm(
                settings.EVENT_PERMS_EDIT_EVENT,
                instance.user,
                instance.event,
            )
        elif instance.is_active:
            assign_perm(
                settings.EVENT_PERMS_EDIT_EVENT,
                instance.user,
                instance.event,
            )
