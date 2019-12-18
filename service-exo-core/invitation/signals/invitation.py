from django.conf import settings


def when_invitation_post_save(sender, instance, created, *args, **kwargs):
    add_permission = False
    if created:
        # when an invitation is created as pending
        # sender user can cancel the invitation (if exists) and resend
        add_permission = True

    else:
        update_fields = kwargs.get('update_fields') or []
        if 'status' in update_fields:
            if instance.is_active:
                instance.clear_user_perms(instance.user)
                if instance.invite_user:
                    instance.clear_user_perms(instance.invite_user)
            elif instance.is_pending and not instance.can_be_accepted(instance.user):
                add_permission = True

    if add_permission:
        if instance.invite_user:
            instance.add_permission(settings.INVITATION_CANCEL, instance.invite_user)
            instance.add_permission(settings.INVITATION_RESEND, instance.invite_user)
        # invited user can accept o deny the invitation
        instance.add_permission(settings.INVITATION_CANCEL, instance.user)
        instance.add_permission(settings.INVITATION_ACCEPT, instance.user)
